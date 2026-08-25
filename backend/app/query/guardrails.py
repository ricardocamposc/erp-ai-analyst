"""Deterministic validation for candidate read-only SQL."""

import re
from typing import Literal

from sqlglot import exp, parse

from app.query.contracts import QueryMetadata, QueryProposal, ValidationResult

FORBIDDEN_NAMES = {
    "Insert", "Update", "Delete", "Drop", "Alter", "Create", "Merge",
    "TruncateTable", "Copy", "Grant", "Command",
}

SYSTEM_RELATIVE_TERMS = (
    "este mes", "mes actual", "este año", "ano actual", "últimos meses",
    "ultimos meses", "este período", "este periodo",
)
DATE_LITERAL = re.compile(r"(?:DATE\s*)?'20\d{2}-\d{2}-\d{2}'", re.IGNORECASE)


def _validate_temporal_intent(proposal: QueryProposal) -> list[str]:
    """Prevent fixed historical ranges from answering system-relative questions."""

    question = proposal.question.casefold()
    has_system_relative_intent = any(term in question for term in SYSTEM_RELATIVE_TERMS)
    explicit_period = bool(
        re.search(
            r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|"
            r"setiembre|octubre|noviembre|diciembre)\s+(?:de\s+)?20\d{2}",
            question,
        )
    )
    if has_system_relative_intent and not explicit_period and DATE_LITERAL.search(proposal.sql):
        return [
            "system-relative period cannot use fixed date literals; use CURRENT_DATE "
            "or the runtime system date"
        ]
    return []


def validate_query(
    proposal: QueryProposal,
    metadata: QueryMetadata,
    max_rows: int = 500,
    max_tables: int = 8,
) -> ValidationResult:
    reasons: list[str] = []
    reasons.extend(_validate_temporal_intent(proposal))
    dialect = "postgres" if metadata.dialect == "postgresql" else metadata.dialect
    allowed_tables = {table.name for table in metadata.tables}
    columns_by_table: dict[str, set[str]] = {}
    for column in metadata.columns:
        columns_by_table.setdefault(column.table, set()).add(column.name)
    try:
        statements = parse(proposal.sql, read=dialect)
    except Exception as error:
        return ValidationResult(status="rejected", reasons=[f"SQL parse failed: {error}"])
    if len(statements) != 1:
        reasons.append("multiple SQL statements are not allowed")
    expression = statements[0] if statements else None
    root_is_read = expression is not None and isinstance(expression, (exp.Select, exp.Union))
    if not root_is_read:
        reasons.append("only read-only SELECT statements are allowed")
    if expression is not None:
        if any(node.__class__.__name__ in FORBIDDEN_NAMES for node in expression.walk()):
            reasons.append("destructive or write SQL operation detected")
    table_nodes = list(expression.find_all(exp.Table)) if expression else []
    cte_names = {
        cte.alias_or_name
        for cte in (expression.find_all(exp.CTE) if expression else [])
        if cte.alias_or_name
    }
    tables = sorted({table.name for table in table_nodes if table.name not in cte_names})
    unknown_tables = sorted(set(tables) - allowed_tables)
    if unknown_tables:
        reasons.append(f"tables not in ERP catalog: {', '.join(unknown_tables)}")
    if len(tables) > max_tables:
        reasons.append(f"query uses more than {max_tables} tables")
    derived_aliases = {
        alias.alias
        for alias in expression.find_all(exp.Alias)
        if alias.alias
    } if expression else set()
    aliases = {
        table.alias_or_name: table.name
        for table in table_nodes
        if table.alias_or_name
    }

    def tables_in_select(select: exp.Select) -> list[str]:
        """Return only tables belonging to this SELECT scope, not its subqueries."""
        scoped: list[str] = []
        for table in select.find_all(exp.Table):
            parent = table.parent
            while parent is not None and not isinstance(parent, exp.Select):
                parent = parent.parent
            if parent is select:
                scoped.append(aliases.get(table.alias_or_name, table.name))
        return sorted(set(scoped))

    def select_for_column(column: exp.Column) -> exp.Select | None:
        parent = column.parent
        while parent is not None and not isinstance(parent, exp.Select):
            parent = parent.parent
        return parent if isinstance(parent, exp.Select) else None

    referenced_columns: set[str] = set()
    for sql_column in expression.find_all(exp.Column) if expression else []:
        qualifier = sql_column.table
        column_name = sql_column.name
        if qualifier:
            table_name = aliases.get(qualifier, qualifier)
            if table_name in cte_names:
                referenced_columns.add(f"{table_name}.{column_name}")
                continue
            if column_name not in columns_by_table.get(table_name, set()):
                reasons.append(f"column not in ERP catalog: {table_name}.{column_name}")
            referenced_columns.add(f"{table_name}.{column_name}")
        else:
            if column_name in derived_aliases:
                referenced_columns.add(column_name)
                continue
            scope = select_for_column(sql_column)
            scope_tables = tables_in_select(scope) if scope is not None else tables
            matching = [table for table in scope_tables if column_name in columns_by_table.get(table, set())]
            if not matching:
                reasons.append(f"column not in ERP catalog: {column_name}")
            elif len(matching) > 1:
                reasons.append(f"ambiguous unqualified column: {column_name}")
            else:
                referenced_columns.add(f"{matching[0]}.{column_name}")
    if proposal.needs_clarification:
        reasons.append(proposal.clarification_question or "clarification required")
    limits = [f"max_rows={max_rows}", "read_only_role", "single_statement"]
    status: Literal["approved", "rejected", "needs_revision"] = (
        "approved"
        if not reasons
        else "needs_revision"
        if len(reasons) == 1 and "clarification" in reasons[0]
        else "rejected"
    )
    return ValidationResult(
        status=status,
        normalized_sql=expression.sql(dialect=dialect) if expression and status == "approved" else None,
        diagnostic_sql=(
            expression.sql(dialect=dialect)
            if expression and len(statements) == 1 and root_is_read and not unknown_tables
            else None
        ),
        reasons=sorted(set(reasons)),
        tables=tables,
        columns=sorted(referenced_columns),
        limits_applied=limits,
    )
