from __future__ import annotations

import json
import re
from dataclasses import asdict

from langchain_ollama import ChatOllama

from evals.cases.schema import CaseScore, EvalCase, EvalRunRecord


def _contains_all(haystack: str, needles: list[str]) -> bool:
    text = haystack.lower()
    return all(needle.lower() in text for needle in needles)


def _contains_any(haystack: str, needles: list[str]) -> bool:
    text = haystack.lower()
    return any(needle.lower() in text for needle in needles)


def score_tool_use(case: EvalCase, run: EvalRunRecord) -> tuple[float, list[str]]:
    reasons: list[str] = []
    tool_names = [tool.name for tool in run.tool_calls]

    if case.tool_policy == "must_call":
        if not run.tool_calls:
            reasons.append("Expected at least one tool call but found none.")
            return 0.0, reasons
        if case.expected_tools and not any(name in case.expected_tools for name in tool_names):
            reasons.append(
                f"Expected one of tools {case.expected_tools}, got {tool_names or ['none']}."
            )
            return 0.25, reasons

        if case.expected_query_contains:
            query_ok = False
            for tool in run.tool_calls:
                query_value = str(tool.args.get("query", ""))
                if _contains_all(query_value, case.expected_query_contains):
                    query_ok = True
                    break
            if not query_ok:
                reasons.append("Tool call query did not match expected query hints.")
                return 0.5, reasons

        return 1.0, reasons

    if case.tool_policy == "must_not_call":
        if run.tool_calls:
            reasons.append(f"Expected no tool calls, got {tool_names}.")
            return 0.0, reasons
        return 1.0, reasons

    # optional
    if not case.expected_tools:
        return 1.0, reasons

    if run.tool_calls and any(name in case.expected_tools for name in tool_names):
        return 1.0, reasons

    return 0.75, ["Optional tool guidance not followed; partial credit applied."]


def score_factuality_deterministic(case: EvalCase, run: EvalRunRecord) -> tuple[float, list[str]]:
    reasons: list[str] = []
    answer = run.final_answer or ""

    required_ok = True
    forbidden_ok = True

    if case.required_answer_keywords:
        required_ok = _contains_all(answer, case.required_answer_keywords)
        if not required_ok:
            reasons.append(
                f"Missing required answer keywords: {case.required_answer_keywords}."
            )

    if case.forbidden_answer_keywords:
        forbidden_hit = _contains_any(answer, case.forbidden_answer_keywords)
        forbidden_ok = not forbidden_hit
        if forbidden_hit:
            reasons.append(
                f"Answer contains forbidden keywords: {case.forbidden_answer_keywords}."
            )

    if case.required_answer_keywords and case.forbidden_answer_keywords:
        score = 1.0 if (required_ok and forbidden_ok) else 0.0
    elif case.required_answer_keywords:
        score = 1.0 if required_ok else 0.0
    elif case.forbidden_answer_keywords:
        score = 1.0 if forbidden_ok else 0.0
    else:
        score = 1.0 if answer.strip() else 0.0
        if score == 0.0:
            reasons.append("Answer was empty.")

    return score, reasons


def score_factuality_judge(
    case: EvalCase,
    run: EvalRunRecord,
    judge_model: ChatOllama | None,
) -> tuple[float | None, str | None]:
    if not judge_model:
        return None, None

    if not case.reference_facts:
        return None, None

    prompt = (
        "You are an evaluator. Score the answer against the reference facts from 0 to 1. "
        "Return strict JSON only with keys score (float) and reason (string).\n"
        f"Prompt: {case.prompt}\n"
        f"Reference facts: {case.reference_facts}\n"
        f"Answer: {run.final_answer}\n"
    )

    try:
        response = judge_model.invoke(prompt)
        content = response.content if isinstance(response.content, str) else str(response.content)
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            return None, "Judge response was not valid JSON."
        payload = json.loads(match.group(0))
        score = float(payload["score"])
        score = max(0.0, min(1.0, score))
        reason = str(payload.get("reason", ""))
        return score, reason
    except Exception as exc:  # noqa: BLE001
        return None, f"Judge call failed: {exc}"


def score_latency(case: EvalCase, run: EvalRunRecord) -> tuple[float, str | None]:
    if run.latency_ms <= case.max_latency_ms:
        return 1.0, None

    raw = case.max_latency_ms / max(run.latency_ms, 1)
    score = max(0.0, min(1.0, raw))
    return score, f"Latency {run.latency_ms}ms exceeded max {case.max_latency_ms}ms."


def score_failure(run: EvalRunRecord) -> tuple[float, str | None]:
    if run.success:
        return 1.0, None
    return 0.0, run.error or "Run failed without explicit error."


def score_case(
    case: EvalCase,
    run: EvalRunRecord,
    judge_model: ChatOllama | None = None,
) -> CaseScore:
    reasons: list[str] = []

    tool_use_score, tool_reasons = score_tool_use(case, run)
    reasons.extend(tool_reasons)

    fact_det_score, fact_det_reasons = score_factuality_deterministic(case, run)
    reasons.extend(fact_det_reasons)

    fact_judge_score, fact_judge_reason = score_factuality_judge(case, run, judge_model)
    if fact_judge_reason:
        reasons.append(fact_judge_reason)

    if fact_judge_score is None:
        factuality_score = fact_det_score
    else:
        factuality_score = (0.7 * fact_det_score) + (0.3 * fact_judge_score)

    latency_score, latency_reason = score_latency(case, run)
    if latency_reason:
        reasons.append(latency_reason)

    failure_score, failure_reason = score_failure(run)
    if failure_reason:
        reasons.append(failure_reason)

    aggregate_score = (
        0.4 * tool_use_score
        + 0.3 * factuality_score
        + 0.2 * latency_score
        + 0.1 * failure_score
    )

    return CaseScore(
        case_id=case.id,
        tool_use_score=tool_use_score,
        factuality_deterministic_score=fact_det_score,
        factuality_judge_score=fact_judge_score,
        factuality_score=factuality_score,
        latency_score=latency_score,
        failure_score=failure_score,
        aggregate_score=aggregate_score,
        reasons=reasons,
    )


def summarize_scores(scores: list[CaseScore]) -> dict:
    if not scores:
        return {
            "count": 0,
            "aggregate": 0.0,
            "tool_use": 0.0,
            "factuality": 0.0,
            "latency": 0.0,
            "failure": 0.0,
        }

    def avg(values: list[float]) -> float:
        return sum(values) / len(values)

    return {
        "count": len(scores),
        "aggregate": avg([score.aggregate_score for score in scores]),
        "tool_use": avg([score.tool_use_score for score in scores]),
        "factuality": avg([score.factuality_score for score in scores]),
        "latency": avg([score.latency_score for score in scores]),
        "failure": avg([score.failure_score for score in scores]),
    }


def scores_to_dict(scores: list[CaseScore]) -> list[dict]:
    return [asdict(score) for score in scores]
