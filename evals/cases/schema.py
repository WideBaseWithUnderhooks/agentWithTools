from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ToolPolicy = Literal["must_call", "must_not_call", "optional"]


@dataclass
class EvalCase:
    id: str
    prompt: str
    tool_policy: ToolPolicy
    expected_tools: list[str] = field(default_factory=list)
    expected_query_contains: list[str] = field(default_factory=list)
    required_answer_keywords: list[str] = field(default_factory=list)
    forbidden_answer_keywords: list[str] = field(default_factory=list)
    reference_facts: list[str] = field(default_factory=list)
    max_latency_ms: int = 15000
    tags: list[str] = field(default_factory=list)


@dataclass
class ToolCallRecord:
    name: str
    args: dict


@dataclass
class EvalRunRecord:
    case_id: str
    prompt: str
    node_path: list[str]
    tool_calls: list[ToolCallRecord]
    final_answer: str
    latency_ms: int
    success: bool
    error: str | None = None


@dataclass
class CaseScore:
    case_id: str
    tool_use_score: float
    factuality_deterministic_score: float
    factuality_judge_score: float | None
    factuality_score: float
    latency_score: float
    failure_score: float
    aggregate_score: float
    reasons: list[str] = field(default_factory=list)
