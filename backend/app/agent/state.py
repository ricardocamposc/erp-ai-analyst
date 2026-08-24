"""Explicit state carried by every LangGraph node."""

from typing import Any, TypedDict

from app.agent.contracts import FinalAnswer, IntentContext, PlannedToolCall


class AnalysisState(TypedDict, total=False):
    request_id: str
    question: str
    intent: IntentContext
    remaining_plan: list[PlannedToolCall]
    tool_history: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    warnings: list[str]
    errors: list[str]
    iteration_count: int
    retry_count: int
    final_answer: FinalAnswer
