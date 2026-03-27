from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from evals.cases.schema import EvalCase, EvalRunRecord, ToolCallRecord
from evals.scoring import score_case, scores_to_dict, summarize_scores
from src.graph import app


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = ROOT / "evals" / "cases" / "golden_v1.json"
DEFAULT_RESULTS_DIR = ROOT / "evals" / "results"


def build_tag_breakdown(cases: list[EvalCase], score_dicts: list[dict]) -> dict[str, dict[str, float]]:
    by_case_id = {case.id: case for case in cases}
    grouped: dict[str, list[dict]] = {}

    for score in score_dicts:
        case = by_case_id.get(score["case_id"])
        if not case:
            continue
        for tag in case.tags:
            grouped.setdefault(tag, []).append(score)

    breakdown: dict[str, dict[str, float]] = {}
    for tag, items in grouped.items():
        count = len(items)
        breakdown[tag] = {
            "count": float(count),
            "aggregate": sum(item["aggregate_score"] for item in items) / count,
            "tool_use": sum(item["tool_use_score"] for item in items) / count,
            "factuality": sum(item["factuality_score"] for item in items) / count,
            "latency": sum(item["latency_score"] for item in items) / count,
            "failure": sum(item["failure_score"] for item in items) / count,
        }

    return breakdown


def gates_passed(summary: dict, args: argparse.Namespace) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    aggregate = float(summary.get("aggregate", 0.0))
    if aggregate < args.aggregate_gate:
        reasons.append(
            f"Aggregate score {aggregate:.3f} below gate {args.aggregate_gate:.3f}."
        )

    if aggregate < args.min_aggregate:
        reasons.append(
            f"Aggregate score {aggregate:.3f} below minimum {args.min_aggregate:.3f}."
        )

    for key, threshold, label in [
        ("tool_use", args.min_tool_use, "tool_use"),
        ("factuality", args.min_factuality, "factuality"),
        ("latency", args.min_latency, "latency"),
        ("failure", args.min_failure, "failure"),
    ]:
        score = float(summary.get(key, 0.0))
        if score < threshold:
            reasons.append(
                f"{label} score {score:.3f} below minimum {threshold:.3f}."
            )

    return len(reasons) == 0, reasons


def load_cases(dataset_path: Path) -> list[EvalCase]:
    raw = dataset_path.read_text(encoding="utf-8")
    # Allow JSONC-style comments in dataset files so prompts can be toggled quickly.
    cleaned = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)
    cleaned = re.sub(r"^\s*//.*$", "", cleaned, flags=re.MULTILINE)
    payload = json.loads(cleaned)
    return [EvalCase(**item) for item in payload]


def _normalize_tool_call(tool_call: Any) -> ToolCallRecord:
    if isinstance(tool_call, dict):
        name = str(tool_call.get("name", ""))
        args = tool_call.get("args", {})
        if not isinstance(args, dict):
            args = {}
        return ToolCallRecord(name=name, args=args)

    name = str(getattr(tool_call, "name", ""))
    args = getattr(tool_call, "args", {})
    if not isinstance(args, dict):
        args = {}
    return ToolCallRecord(name=name, args=args)


def run_case(case: EvalCase) -> EvalRunRecord:
    started = time.perf_counter()
    node_path: list[str] = []
    tool_calls: list[ToolCallRecord] = []
    final_answer = ""

    try:
        inputs = {"messages": [("user", case.prompt)]}
        for output in app.stream(inputs, stream_mode="updates"):
            for node, data in output.items():
                node_path.append(str(node))

                messages = data.get("messages") if isinstance(data, dict) else None
                if not messages:
                    continue

                for message in messages:
                    raw_calls = getattr(message, "tool_calls", None)
                    if raw_calls:
                        tool_calls.extend(_normalize_tool_call(item) for item in raw_calls)

                    content = getattr(message, "content", "")
                    if isinstance(content, str) and content.strip():
                        final_answer = content.strip()

        latency_ms = int((time.perf_counter() - started) * 1000)
        return EvalRunRecord(
            case_id=case.id,
            prompt=case.prompt,
            node_path=node_path,
            tool_calls=tool_calls,
            final_answer=final_answer,
            latency_ms=latency_ms,
            success=True,
            error=None,
        )
    except Exception as exc:  # noqa: BLE001
        latency_ms = int((time.perf_counter() - started) * 1000)
        return EvalRunRecord(
            case_id=case.id,
            prompt=case.prompt,
            node_path=node_path,
            tool_calls=tool_calls,
            final_answer=final_answer,
            latency_ms=latency_ms,
            success=False,
            error=str(exc),
        )


def build_markdown_report(
    run_id: str,
    summary: dict,
    scores: list[dict],
    aggregate_gate: float,
) -> str:
    passed = summary.get("aggregate", 0.0) >= aggregate_gate

    lines = [
        f"# Eval Report: {run_id}",
        "",
        f"- Aggregate score: {summary.get('aggregate', 0.0):.3f}",
        f"- Tool-use score: {summary.get('tool_use', 0.0):.3f}",
        f"- Factuality score: {summary.get('factuality', 0.0):.3f}",
        f"- Latency score: {summary.get('latency', 0.0):.3f}",
        f"- Failure score: {summary.get('failure', 0.0):.3f}",
        f"- Cases: {summary.get('count', 0)}",
        f"- Gate ({aggregate_gate:.2f}): {'PASS' if passed else 'FAIL'}",
        "",
        "## Lowest Scoring Cases",
        "",
    ]

    worst = sorted(scores, key=lambda item: item["aggregate_score"])[:10]
    if not worst:
        lines.append("No case scores available.")
    else:
        for item in worst:
            lines.append(
                f"- {item['case_id']}: aggregate={item['aggregate_score']:.3f}, "
                f"tool={item['tool_use_score']:.3f}, factuality={item['factuality_score']:.3f}, "
                f"latency={item['latency_score']:.3f}, failure={item['failure_score']:.3f}"
            )
            for reason in item.get("reasons", [])[:2]:
                lines.append(f"  - reason: {reason}")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run golden dataset evaluations.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to dataset JSON.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory where reports are written.",
    )
    parser.add_argument(
        "--aggregate-gate",
        type=float,
        default=0.70,
        help="Aggregate score required to pass.",
    )
    parser.add_argument("--min-aggregate", type=float, default=0.0)
    parser.add_argument("--min-tool-use", type=float, default=0.0)
    parser.add_argument("--min-factuality", type=float, default=0.0)
    parser.add_argument("--min-latency", type=float, default=0.0)
    parser.add_argument("--min-failure", type=float, default=0.0)
    parser.add_argument(
        "--judge-model",
        type=str,
        default="",
        help="Optional Ollama model for factuality judging (for example: llama3.2:3b).",
    )
    parser.add_argument(
        "--fail-on-gate",
        action="store_true",
        help="Exit non-zero if the aggregate score does not meet the gate.",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()

    cases = load_cases(args.dataset)
    args.results_dir.mkdir(parents=True, exist_ok=True)

    judge_model = ChatOllama(model=args.judge_model, temperature=0) if args.judge_model else None

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_records: list[EvalRunRecord] = []
    case_scores = []

    for case in cases:
        run = run_case(case)
        run_records.append(run)
        case_scores.append(score_case(case, run, judge_model=judge_model))

    score_dicts = scores_to_dict(case_scores)
    summary = summarize_scores(case_scores)
    tag_breakdown = build_tag_breakdown(cases, score_dicts)
    passed, gate_reasons = gates_passed(summary, args)

    json_report = {
        "run_id": run_id,
        "dataset": str(args.dataset),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "tag_breakdown": tag_breakdown,
        "gate": {
            "aggregate_gate": args.aggregate_gate,
            "passed": passed,
            "reasons": gate_reasons,
        },
        "runs": [asdict(record) for record in run_records],
        "scores": score_dicts,
    }

    json_path = args.results_dir / f"eval_report_{run_id}.json"
    md_path = args.results_dir / f"eval_report_{run_id}.md"

    json_path.write_text(json.dumps(json_report, indent=2), encoding="utf-8")
    md_path.write_text(
        build_markdown_report(run_id, summary, score_dicts, args.aggregate_gate),
        encoding="utf-8",
    )

    print(f"Run ID: {run_id}")
    print(f"Aggregate score: {summary.get('aggregate', 0.0):.3f}")
    print(f"Gate ({args.aggregate_gate:.2f}): {'PASS' if passed else 'FAIL'}")
    if gate_reasons:
        for reason in gate_reasons:
            print(f"Gate reason: {reason}")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")

    if args.fail_on_gate and not passed:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
