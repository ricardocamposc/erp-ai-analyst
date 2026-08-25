"""Contracts shared by dynamic-query agents, providers and guardrails."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class MetadataTable(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    domain: str
    description: str
    row_estimate: int | None = None
    temporal_columns: list[str] = Field(default_factory=list)


class MetadataColumn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table: str
    name: str
    data_type: str
    nullable: bool = True
    sensitive: bool = False
    indexed: bool = False
    description: str = ""


class MetadataRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")

    left_table: str
    left_column: str
    right_table: str
    right_column: str
    relationship: str = "many_to_one"


class QueryMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    catalog_version: str
    dialect: str
    tables: list[MetadataTable] = Field(default_factory=list)
    columns: list[MetadataColumn] = Field(default_factory=list)
    relationships: list[MetadataRelationship] = Field(default_factory=list)
    available_periods: dict[str, dict[str, Any]] = Field(default_factory=dict)
    system_date: date | None = None


class QueryProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    analysis_goal: str
    sql: str
    tables: list[str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    joins: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    needs_clarification: bool = False
    clarification_question: str | None = None
    analysis_mode: Literal["fact", "comparison", "projection"] = "fact"


class QuestionRoute(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["data_query", "erp_concept", "unsupported"]
    rationale: str = ""


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["approved", "rejected", "needs_revision"]
    normalized_sql: str | None = None
    diagnostic_sql: str | None = None
    reasons: list[str] = Field(default_factory=list)
    estimated_rows: int | None = None
    estimated_cost: str | None = None
    tables: list[str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    limits_applied: list[str] = Field(default_factory=list)


class ValidatorReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approved: bool
    blocking_issue: bool = True
    blocking_scope: Literal[
        "none", "coverage", "entity", "metric", "relationship", "grain", "meaning", "schema", "tables"
    ] = "none"
    semantic_issues: list[str] = Field(default_factory=list)
    revision_instructions: list[str] = Field(default_factory=list)


class QueryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool = False
    sql_hash: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)


class AnalysisMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_type: str
    request_id: str
    stage: str
    attempt: int = 0
    status: str
    payload: dict[str, Any] = Field(default_factory=dict)
    contract_version: str = "dynamic-query.v1"
