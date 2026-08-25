"""Provider contract and local canonical-ERP implementation."""

from hashlib import sha256
from typing import Protocol

from sqlalchemy import inspect, text

from app.db.connection import create_database_engine
from app.query.contracts import (
    MetadataColumn,
    MetadataRelationship,
    MetadataTable,
    QueryMetadata,
    QueryResult,
)

CANONICAL_TABLES: dict[str, tuple[str, str]] = {
    "customer": ("customers", "Customers and customer segments."),
    "product": ("inventory", "Products and standard costs."),
    "salesperson": ("sales", "Sales representatives."),
    "supplier": ("purchases", "Suppliers and lead times."),
    "cost_center": ("accounting", "Cost centers and areas."),
    "sales_document": ("sales", "Posted or cancelled sales documents."),
    "sales_document_line": ("sales", "Sales document lines."),
    "inventory_movement": ("inventory", "Inventory receipts, sales and adjustments."),
    "stock_balance": ("inventory", "Daily stock balances."),
    "purchase_order": ("purchases", "Purchase orders and status."),
    "purchase_order_line": ("purchases", "Purchase order lines."),
    "goods_receipt": ("purchases", "Goods receipts."),
    "goods_receipt_line": ("purchases", "Goods receipt lines."),
    "payroll_concept": ("payroll", "Aggregate payroll concepts."),
    "employee_payroll_summary": (
        "payroll",
        "Aggregate payroll by period and cost center; contains no employee identity or name.",
    ),
    "payroll_summary_line": ("payroll", "Aggregate payroll concept amounts."),
    "accounting_period": ("accounting", "Closed accounting periods."),
    "account_balance": ("accounting", "Accounting balances by account and cost center."),
}


class ERPQueryProvider(Protocol):
    def metadata(self) -> QueryMetadata: ...

    def row_estimate(self, table_name: str) -> int: ...

    def available_periods(self, table_name: str) -> dict[str, str | None]: ...

    def explain_readonly(self, sql: str) -> dict[str, object]: ...

    def execute_readonly(self, sql: str, max_rows: int) -> QueryResult: ...


class LocalERPQueryProvider:
    """Provider for the local canonical PostgreSQL analytical store."""

    catalog_version = "canonical-erp.v1"
    statement_timeout_ms = 5000

    def metadata(self) -> QueryMetadata:
        engine = create_database_engine()
        inspector = inspect(engine)
        tables: list[MetadataTable] = []
        columns: list[MetadataColumn] = []
        relationships: list[MetadataRelationship] = []
        for name, (domain, description) in CANONICAL_TABLES.items():
            if not inspector.has_table(name):
                continue
            table_columns = inspector.get_columns(name)
            indexes = {
                column
                for index in inspector.get_indexes(name)
                for column in index.get("column_names", [])
            }
            temporal = [
                str(column["name"])
                for column in table_columns
                if str(column["name"]).endswith(("_date", "_start", "_end"))
            ]
            tables.append(MetadataTable(name=name, domain=domain, description=description, temporal_columns=temporal))
            for column in table_columns:
                column_name = str(column["name"])
                column_description = f"{name}.{column_name}"
                if name == "employee_payroll_summary" and column_name == "business_key":
                    column_description = (
                        "Payroll summary business key; identifies an aggregate payroll "
                        "record, not an employee."
                    )
                columns.append(
                    MetadataColumn(
                        table=name,
                        name=column_name,
                        data_type=str(column["type"]),
                        nullable=bool(column.get("nullable", True)),
                        indexed=column_name in indexes,
                        description=column_description,
                    )
                )
            for foreign_key in inspector.get_foreign_keys(name):
                referred = foreign_key.get("referred_table")
                local = foreign_key.get("constrained_columns", [])
                remote = foreign_key.get("referred_columns", [])
                if referred and local and remote:
                    relationships.append(
                        MetadataRelationship(
                            left_table=name,
                            left_column=str(local[0]),
                            right_table=str(referred),
                            right_column=str(remote[0]),
                        )
                    )
        return QueryMetadata(
            catalog_version=self.catalog_version,
            dialect="postgresql",
            tables=tables,
            columns=columns,
            relationships=relationships,
        )

    def execute_readonly(self, sql: str, max_rows: int) -> QueryResult:
        engine = create_database_engine()
        sql_hash = sha256(sql.encode("utf-8")).hexdigest()
        with engine.begin() as connection:
            connection.execute(text("SET TRANSACTION READ ONLY"))
            # PostgreSQL does not accept bind parameters in SET statements.
            # The value is an internal integer limit, never user-controlled SQL.
            timeout_ms = int(self.statement_timeout_ms)
            connection.execute(text(f"SET LOCAL statement_timeout = {timeout_ms}"))
            result = connection.execute(text(sql))
            columns = list(result.keys())
            raw_rows = result.fetchmany(max_rows + 1)
        truncated = len(raw_rows) > max_rows
        rows = [dict(zip(columns, row, strict=True)) for row in raw_rows[:max_rows]]
        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            truncated=truncated,
            sql_hash=sql_hash,
            evidence=[
                {
                    "tool_name": "dynamic_readonly_query",
                    "query_id": f"dynamic.{sql_hash[:16]}",
                    "metric": "dynamic_readonly_query",
                    "row_count": len(rows),
                }
            ],
        )

    def row_estimate(self, table_name: str) -> int:
        if table_name not in CANONICAL_TABLES:
            raise ValueError("table is not in ERP catalog")
        with create_database_engine().connect() as connection:
            row = connection.execute(
                text("SELECT COALESCE(reltuples, 0)::bigint AS estimate FROM pg_class WHERE relname = :table_name"),
                {"table_name": table_name},
            ).one()
        return int(row.estimate)

    def available_periods(self, table_name: str) -> dict[str, str | None]:
        metadata = self.metadata()
        table = next((item for item in metadata.tables if item.name == table_name), None)
        if table is None:
            raise ValueError("table is not in ERP catalog")
        if not table.temporal_columns:
            return {"column": None, "minimum": None, "maximum": None}
        column = table.temporal_columns[0]
        with create_database_engine().connect() as connection:
            row = connection.execute(
                text(f'SELECT MIN("{column}") AS minimum, MAX("{column}") AS maximum FROM "{table_name}"')
            ).one()
        return {
            "column": column,
            "minimum": str(row.minimum) if row.minimum is not None else None,
            "maximum": str(row.maximum) if row.maximum is not None else None,
        }

    def explain_readonly(self, sql: str) -> dict[str, object]:
        with create_database_engine().begin() as connection:
            connection.execute(text("SET TRANSACTION READ ONLY"))
            timeout_ms = int(self.statement_timeout_ms)
            connection.execute(text(f"SET LOCAL statement_timeout = {timeout_ms}"))
            row = connection.execute(
                text("EXPLAIN (FORMAT JSON) " + sql)
            ).one()
        return {"plan": row[0]}
