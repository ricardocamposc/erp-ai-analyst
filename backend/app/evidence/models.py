"""Structured, non-chain-of-thought provenance attached to tool output."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class Evidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    tool_name: str
    query_id: str
    period_start: date
    period_end: date
    metric: str
    contributing_keys: list[str] = []
