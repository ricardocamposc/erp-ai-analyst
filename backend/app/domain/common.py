"""Shared typed period and provenance contracts for deterministic services."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Period:
    start: date
    end: date


@dataclass(frozen=True)
class Provenance:
    repository_query: str
    period_start: date
    period_end: date
    row_count: int
