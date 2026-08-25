"""Metadata and guarded query tools exposed to dynamic agents."""

from app.query.contracts import (
    QueryMetadata,
    QueryProposal,
    QueryResult,
    ValidationResult,
)
from app.query.guardrails import validate_query as validate_sql
from app.query.provider import LocalERPQueryProvider

DYNAMIC_TOOL_NAMES = {
    "list_erp_tables",
    "describe_erp_table",
    "list_erp_columns",
    "list_erp_relationships",
    "list_erp_indexes",
    "get_table_row_estimate",
    "get_available_periods",
    "get_allowed_metrics",
    "get_allowed_dimensions",
    "get_data_classification",
    "validate_query",
    "explain_query",
    "execute_readonly_query",
}


def _plan_metrics(plan: object) -> tuple[int | None, float | None]:
    """Extract conservative estimates from PostgreSQL's JSON execution plan."""

    rows: int | None = None
    cost: float | None = None
    if isinstance(plan, list):
        for item in plan:
            item_rows, item_cost = _plan_metrics(item)
            rows = item_rows if item_rows is not None else rows
            cost = item_cost if item_cost is not None else cost
    elif isinstance(plan, dict):
        if isinstance(plan.get("Plan Rows"), int):
            rows = int(plan["Plan Rows"])
        if isinstance(plan.get("Total Cost"), (int, float)):
            cost = float(plan["Total Cost"])
        for item in plan.values():
            item_rows, item_cost = _plan_metrics(item)
            rows = max(rows or 0, item_rows or 0) or rows
            cost = max(cost or 0, item_cost or 0) or cost
    return rows, cost


def list_erp_tables(provider: LocalERPQueryProvider) -> QueryMetadata:
    return provider.metadata()


def describe_erp_table(provider: LocalERPQueryProvider, table_name: str) -> QueryMetadata:
    metadata = provider.metadata()
    if table_name not in {table.name for table in metadata.tables}:
        raise ValueError("table is not in ERP catalog")
    metadata.tables = [table for table in metadata.tables if table.name == table_name]
    metadata.columns = [column for column in metadata.columns if column.table == table_name]
    metadata.relationships = [
        relation
        for relation in metadata.relationships
        if relation.left_table == table_name or relation.right_table == table_name
    ]
    return metadata


def list_erp_columns(provider: LocalERPQueryProvider, table_name: str) -> list[dict[str, object]]:
    return [
        column.model_dump()
        for column in provider.metadata().columns
        if column.table == table_name
    ]


def list_erp_relationships(provider: LocalERPQueryProvider) -> list[dict[str, str]]:
    return [item.model_dump() for item in provider.metadata().relationships]


def list_erp_indexes(provider: LocalERPQueryProvider) -> list[dict[str, object]]:
    metadata = provider.metadata()
    return [
        {"table": column.table, "column": column.name, "indexed": column.indexed}
        for column in metadata.columns
        if column.indexed
    ]


def get_table_row_estimate(provider: LocalERPQueryProvider, table_name: str) -> int:
    return provider.row_estimate(table_name)


def get_available_periods(provider: LocalERPQueryProvider, table_name: str) -> dict[str, str | None]:
    return provider.available_periods(table_name)


def get_allowed_metrics() -> list[str]:
    return ["count", "sum", "avg", "min", "max", "distinct_count"]


def get_allowed_dimensions(provider: LocalERPQueryProvider) -> list[str]:
    return [f"{column.table}.{column.name}" for column in provider.metadata().columns if not column.sensitive]


def get_data_classification(provider: LocalERPQueryProvider) -> list[dict[str, object]]:
    return [
        {"table": column.table, "column": column.name, "sensitive": column.sensitive}
        for column in provider.metadata().columns
    ]


def validate_dynamic_query(
    provider: LocalERPQueryProvider, proposal: QueryProposal
) -> ValidationResult:
    return validate_sql(proposal, provider.metadata())


def validate_query(
    provider: LocalERPQueryProvider, proposal: QueryProposal
) -> ValidationResult:
    return validate_dynamic_query(provider, proposal)


def explain_query(
    provider: LocalERPQueryProvider, proposal: QueryProposal
) -> dict[str, object]:
    validation = validate_dynamic_query(provider, proposal)
    if validation.status != "approved" or validation.normalized_sql is None:
        raise ValueError("query did not pass the deterministic guardrails")
    return provider.explain_readonly(validation.normalized_sql)


def execute_readonly_query(
    provider: LocalERPQueryProvider,
    proposal: QueryProposal,
    max_rows: int = 500,
) -> QueryResult:
    validation = validate_dynamic_query(provider, proposal)
    if validation.status != "approved" or validation.normalized_sql is None:
        raise ValueError("query did not pass the deterministic guardrails")
    plan = provider.explain_readonly(validation.normalized_sql)
    estimated_rows, estimated_cost = _plan_metrics(plan.get("plan"))
    if estimated_rows is not None and estimated_rows > 100_000:
        raise ValueError("query estimated row count exceeds the dynamic-query limit")
    if estimated_cost is not None and estimated_cost > 1_000_000:
        raise ValueError("query estimated cost exceeds the dynamic-query limit")
    return provider.execute_readonly(validation.normalized_sql, max_rows)
