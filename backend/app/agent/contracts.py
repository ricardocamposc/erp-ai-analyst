"""Structured agent inputs, plans and final responses."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IntentContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str
    current_start: str
    current_end: str
    previous_start: str | None = None
    previous_end: str | None = None
    period_is_explicit: bool = False
    range_start: str | None = None
    range_end: str | None = None
    supported: bool = True
    warning: str | None = None


class PlannedToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    arguments: dict[str, Any]
    # Purpose is useful for observability, but it is not required to execute a
    # validated tool call. The model may omit it in a structured response.
    purpose: str = ""


class PlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # OpenAI structured outputs accept the array shape but reject the JSON
    # Schema maxItems constraint. The bounded length is enforced by the
    # gateway after parsing the model response.
    steps: list[PlannedToolCall] = Field(default_factory=list)


class FinalAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    key_findings: list[str] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    analysis_performed: list[str] = Field(default_factory=list)
    structured_data: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    status: Literal["completed", "insufficient_data", "unsupported", "failed"]

    @field_validator("structured_data", mode="before")
    @classmethod
    def normalize_structured_data(cls, value: Any) -> Any:
        """Keep the public contract list-shaped when a model returns a mapping."""

        if isinstance(value, dict):
            return [{"key": key, "data": item} for key, item in value.items()]
        return value
