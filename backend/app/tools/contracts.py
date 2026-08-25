"""Pydantic contracts shared by all model-facing analytics tools."""

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PeriodRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: date
    end: date
    limit: int = Field(default=100, ge=1, le=100)

    @model_validator(mode="after")
    def validate_period(self) -> "PeriodRequest":
        if self.end < self.start:
            raise ValueError("period end must not precede period start")
        if (self.end - self.start).days > 366:
            raise ValueError("period cannot exceed 366 days")
        return self


class EntityPeriodRequest(PeriodRequest):
    entity_key: str = Field(min_length=1, max_length=40)


class ConceptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str = Field(min_length=1, max_length=80)


class ComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current: PeriodRequest
    previous: PeriodRequest


class ToolResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    domain: str
    data: Any
    evidence: list[dict[str, Any]]
    warnings: list[str] = []
