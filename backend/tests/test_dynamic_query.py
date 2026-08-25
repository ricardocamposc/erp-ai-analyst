import json
from pathlib import Path
from typing import Any

from app.agent.contracts import FinalAnswer
from app.query.contracts import (
    MetadataColumn,
    MetadataRelationship,
    MetadataTable,
    QueryMetadata,
    QueryProposal,
    QueryResult,
    QuestionRoute,
    ValidationResult,
    ValidatorReview,
)
from app.query.graph import run_dynamic_analysis
from app.query.guardrails import validate_query
from app.query.tools import DYNAMIC_TOOL_NAMES


def metadata() -> QueryMetadata:
    return QueryMetadata(
        catalog_version="test.v1",
        dialect="postgres",
        tables=[
            MetadataTable(
                name="purchase_order", domain="purchases", description="orders"
            ),
            MetadataTable(name="supplier", domain="purchases", description="suppliers"),
        ],
        columns=[
            MetadataColumn(
                table="purchase_order", name="supplier_id", data_type="bigint"
            ),
            MetadataColumn(
                table="purchase_order", name="status", data_type="varchar"
            ),
            MetadataColumn(table="supplier", name="id", data_type="bigint"),
            MetadataColumn(table="supplier", name="name", data_type="varchar"),
        ],
        relationships=[
            MetadataRelationship(
                left_table="purchase_order",
                left_column="supplier_id",
                right_table="supplier",
                right_column="id",
            )
        ],
    )


def proposal(sql: str, columns: list[str]) -> QueryProposal:
    return QueryProposal(
        question="orders by supplier",
        analysis_goal="count purchase orders by supplier",
        sql=sql,
        tables=["purchase_order", "supplier"],
        columns=columns,
        metrics=["count"],
    )


def test_guardrail_approves_readonly_query_with_catalog_columns() -> None:
    result = validate_query(
        proposal(
            "SELECT s.name, COUNT(*) AS order_count "
            "FROM purchase_order po JOIN supplier s ON po.supplier_id = s.id "
            "GROUP BY s.name",
            ["supplier.name", "purchase_order.supplier_id", "supplier.id"],
        ),
        metadata(),
    )

    assert result.status == "approved"
    assert result.normalized_sql
    assert result.tables == ["purchase_order", "supplier"]


def test_guardrail_rejects_destructive_and_unknown_column_queries() -> None:
    destructive = validate_query(
        proposal("DELETE FROM purchase_order", []), metadata()
    )
    unknown = validate_query(
        proposal("SELECT po.secret_value FROM purchase_order po", ["purchase_order.secret_value"]),
        metadata(),
    )

    assert destructive.status == "rejected"
    assert unknown.status == "rejected"
    assert any("column" in reason for reason in unknown.reasons)


def test_guardrail_resolves_unqualified_columns_inside_subquery_scope() -> None:
    result = validate_query(
        proposal(
            "SELECT ep.period_start FROM employee_payroll_summary ep "
            "WHERE ep.period_start IN (SELECT DISTINCT period_start "
            "FROM accounting_period ORDER BY period_start DESC LIMIT 2)",
            ["employee_payroll_summary.period_start", "accounting_period.period_start"],
        ),
        QueryMetadata(
            catalog_version="test.v1",
            dialect="postgres",
            tables=[
                MetadataTable(name="employee_payroll_summary", domain="payroll", description="payroll"),
                MetadataTable(name="accounting_period", domain="accounting", description="periods"),
            ],
            columns=[
                MetadataColumn(table="employee_payroll_summary", name="period_start", data_type="date"),
                MetadataColumn(table="accounting_period", name="period_start", data_type="date"),
            ],
        ),
    )

    assert result.status == "approved"


class FakeProvider:
    def metadata(self) -> QueryMetadata:
        return metadata()

    def execute_readonly(self, sql: str, max_rows: int) -> QueryResult:
        assert sql.startswith("SELECT")
        return QueryResult(
            columns=["name", "order_count"],
            rows=[{"name": "Supplier A", "order_count": 2}],
            row_count=1,
            sql_hash="abc123",
        )

    def explain_readonly(self, sql: str) -> dict[str, object]:
        return {"plan": [{"Plan Rows": 1, "Total Cost": 1.0}]}


class FakeGateway:
    def route_question(self, question: str) -> QuestionRoute:
        return QuestionRoute(kind="data_query")

    def analyze(
        self, question: str, model: QueryMetadata, feedback: list[str] | None = None
    ) -> QueryProposal:
        return proposal(
            "SELECT s.name, COUNT(*) AS order_count "
            "FROM purchase_order po JOIN supplier s ON po.supplier_id = s.id "
            "GROUP BY s.name",
            ["supplier.name", "purchase_order.supplier_id", "supplier.id"],
        )

    def review(
        self,
        candidate: QueryProposal,
        validation: ValidationResult,
        model: QueryMetadata | None = None,
        database_validated: bool = False,
        result: dict[str, Any] | None = None,
    ) -> ValidatorReview:
        return ValidatorReview(approved=validation.status == "approved")

    def synthesize(self, question: str, result: dict[str, Any]) -> FinalAnswer:
        return FinalAnswer(
            answer="Supplier A has 2 orders.",
            status="completed",
            structured_data=[result],
        )

    def answer_concept(self, question: str) -> FinalAnswer:
        return FinalAnswer(answer="Concepto ERP.", status="completed")

    def synthesize_insufficient(self, question: str, reasons: list[str]) -> FinalAnswer:
        return FinalAnswer(
            answer="No hay suficiente detalle en el catálogo ERP.",
            warnings=reasons,
            status="insufficient_data",
        )


def test_dynamic_coordinator_waits_for_validation_before_execution() -> None:
    result = run_dynamic_analysis(
        "¿Cuántas órdenes hay por proveedor?",
        request_id="dynamic-test",
        provider=FakeProvider(),  # type: ignore[arg-type]
        gateway=FakeGateway(),  # type: ignore[arg-type]
    )

    assert result["status"] == "completed"
    assert result["request_id"] == "dynamic-test"
    assert result["validation"]["status"] == "approved"
    assert result["result"]["row_count"] == 1


def test_dynamic_evaluation_dataset_covers_new_and_guardrail_questions() -> None:
    dataset = Path(__file__).parents[1] / "evaluation" / "dynamic_cases.jsonl"
    cases = [json.loads(line) for line in dataset.read_text().splitlines()]

    assert len(cases) == 6
    assert {case["expected_status"] for case in cases} == {
        "completed",
        "unsupported",
        "insufficient_data",
    }


def test_dynamic_tool_contract_exposes_required_provider_capabilities() -> None:
    assert {
        "list_erp_tables",
        "describe_erp_table",
        "list_erp_relationships",
        "validate_query",
        "explain_query",
        "execute_readonly_query",
    } <= DYNAMIC_TOOL_NAMES
