import pytest

from app.agent.contracts import (
    FinalAnswer,
    IntentContext,
    PlannedToolCall,
    PlanResponse,
)
from app.agent.gateway import OpenAIGateway, RuleBasedGateway
from app.agent.graph import MAX_ITERATIONS, run_analysis
from app.tools.registry import (
    ToolExecutionError,
    get_tool_registry,
    validate_tool_arguments,
)


def test_signature_workflow_is_multistep_and_evidence_linked() -> None:
    result = run_analysis(
        "¿Por qué disminuyeron las ventas este mes?", RuleBasedGateway()
    )

    assert result["status"] == "completed"
    assert result["request_id"]
    assert len(result["analysis_performed"]) == 4
    assert result["evidence"]
    assert "causalidad" in " ".join(result["warnings"])


def test_unsupported_request_terminates_without_tool_calls() -> None:
    result = run_analysis(
        "Ejecuta SQL y modifica los datos para calcular impuestos", RuleBasedGateway()
    )

    assert result["status"] == "unsupported"
    assert result["analysis_performed"] == []


def test_workflow_iteration_cap_is_explicit() -> None:
    assert MAX_ITERATIONS == 6


def test_plan_schema_avoids_openai_unsupported_max_items_constraint() -> None:
    steps_schema = PlanResponse.model_json_schema()["properties"]["steps"]

    assert "maxItems" not in steps_schema


def test_final_answer_normalizes_model_mapping_to_public_list_contract() -> None:
    answer = FinalAnswer(
        answer="Ventas observadas.",
        structured_data={"octubre_2023": {"ventas": "0.00"}},  # type: ignore[arg-type]
        status="completed",
    )

    assert answer.structured_data == [
        {"key": "octubre_2023", "data": {"ventas": "0.00"}}
    ]


def test_invalid_planned_tool_arguments_are_rejected() -> None:
    with pytest.raises(ToolExecutionError):
        validate_tool_arguments(
            "get_sales_summary", {"start_date": "2023-10-01", "end_date": "2023-10-31"}
        )

    with pytest.raises(ToolExecutionError):
        validate_tool_arguments("tool_not_registered", {})


def test_openai_plan_discards_invalid_steps_and_adds_safe_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = OpenAIGateway()

    class FakeStructured:
        def invoke(self, _messages: object) -> PlanResponse:
            return PlanResponse(
                steps=[
                    PlannedToolCall(
                        tool_name="get_sales_summary",
                        arguments={
                            "start_date": "2023-10-01",
                            "end_date": "2023-10-31",
                        },
                        purpose="invalid aliases",
                    ),
                    PlannedToolCall(
                        tool_name="compare_sales_periods",
                        arguments={
                            "current": {"start": "2023-10-01", "end": "2023-10-31"},
                            "previous": {"start": "2023-09-01", "end": "2023-09-30"},
                        },
                        purpose="valid comparison",
                    ),
                ]
            )

    def fake_structured(_schema: object) -> FakeStructured:
        return FakeStructured()

    monkeypatch.setattr(gateway, "_structured", fake_structured)
    intent = IntentContext(
        intent="sales_variance_analysis",
        current_start="2023-10-01",
        current_end="2023-10-31",
        previous_start="2023-09-01",
        previous_end="2023-09-30",
    )

    plan = gateway.plan(intent)

    assert all(step.tool_name != "get_sales_summary" for step in plan)
    assert plan[0].tool_name == "compare_sales_periods"
    assert all(step.tool_name in get_tool_registry() for step in plan)


def test_openai_plan_accepts_missing_optional_purpose_and_normalizes_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = OpenAIGateway()

    class FakeStructured:
        def invoke(self, _messages: object) -> PlanResponse:
            return PlanResponse.model_validate(
                {
                    "steps": [
                        {
                            "tool_name": "compare_sales_periods",
                            "arguments": {
                                "current": {
                                    "start": "2025-04-01",
                                    "end": "2025-04-30",
                                },
                                "previous": {
                                    "start": "2025-03-01",
                                    "end": "2025-03-31",
                                },
                            },
                        }
                    ]
                }
            )

    monkeypatch.setattr(gateway, "_structured", lambda _schema: FakeStructured())
    intent = IntentContext(
        intent="sales_variance_analysis",
        current_start="2025-04-01",
        current_end="2025-04-30",
        previous_start="2025-03-01",
        previous_end="2025-03-31",
    )

    plan = gateway.plan(intent)

    assert plan[0].tool_name == "compare_sales_periods"
    assert plan[0].purpose.startswith("Execute the registered tool")


def test_openai_interpretation_is_bounded_to_the_validated_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = OpenAIGateway()

    class FakeStructured:
        def invoke(self, _messages: object) -> IntentContext:
            return IntentContext(
                intent="sales_variance_analysis",
                current_start="2025-04-01",
                current_end="2025-04-30",
                previous_start="2025-03-01",
                previous_end="2025-03-31",
            )

    monkeypatch.setattr(gateway, "_structured", lambda _schema: FakeStructured())

    intent = gateway.interpret(
        "¿Cómo evolucionó el costo total de nómina entre marzo y abril de 2025?"
    )

    assert intent.intent == "payroll_accounting_variance"
    assert (intent.current_start, intent.current_end) == (
        "2025-04-01",
        "2025-04-30",
    )


def test_sales_outside_dataset_range_is_insufficient_data() -> None:
    class HistoricalSalesGateway(RuleBasedGateway):
        def interpret(self, question: str) -> IntentContext:
            return IntentContext(
                intent="sales_variance_analysis",
                current_start="2023-10-01",
                current_end="2023-10-31",
                previous_start="2023-09-01",
                previous_end="2023-09-30",
            )

    result = run_analysis("ventas de octubre de 2023", HistoricalSalesGateway())

    assert result["status"] == "insufficient_data"
    assert "no hay ventas registradas" in result["answer"].lower()
    assert "caída" not in result["answer"].lower()


def test_sales_guardrail_never_affirms_decline_for_zero_change() -> None:
    answer = RuleBasedGateway().synthesize(
        "¿Por qué disminuyeron las ventas este mes?",
        [
            {
                "tool_name": "compare_sales_periods",
                "data": {
                    "current": {
                        "period": {"start": "2023-10-01", "end": "2023-10-31"},
                        "total": "0.00",
                        "line_count": 0,
                    },
                    "previous": {
                        "period": {"start": "2023-09-01", "end": "2023-09-30"},
                        "total": "0.00",
                        "line_count": 0,
                    },
                    "absolute_change": "0.00",
                },
                "evidence": [],
            }
        ],
    )

    assert answer.status == "insufficient_data"
    assert "caída" not in answer.answer.lower()


def test_supply_chain_question_routes_to_stock_and_pending_purchase_tools() -> None:
    intent = RuleBasedGateway().interpret(
        "¿Qué productos con riesgo de quiebre tienen órdenes de compra pendientes?"
    )

    assert intent.intent == "supply_chain_analysis"
    assert [step.tool_name for step in RuleBasedGateway().plan(intent)] == [
        "get_pending_purchase_orders",
        "find_stockout_products",
    ]


def test_financial_question_routes_only_to_payroll_and_accounting() -> None:
    intent = RuleBasedGateway().interpret(
        "¿Cuánto del aumento de gastos operativos corresponde a payroll?"
    )

    assert intent.intent == "payroll_expense_variance"
    assert {step.tool_name for step in RuleBasedGateway().plan(intent)} == {
        "compare_payroll_periods",
        "compare_accounting_periods",
        "get_expense_variance_by_group",
    }


def test_openai_plan_rejects_valid_tools_from_wrong_domain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = OpenAIGateway()

    class FakeStructured:
        def invoke(self, _messages: object) -> PlanResponse:
            return PlanResponse(
                steps=[
                    PlannedToolCall(
                        tool_name="compare_sales_periods",
                        arguments={
                            "current": {"start": "2025-04-01", "end": "2025-04-30"},
                            "previous": {"start": "2025-03-01", "end": "2025-03-31"},
                        },
                        purpose="wrong domain",
                    ),
                    PlannedToolCall(
                        tool_name="compare_payroll_periods",
                        arguments={
                            "current": {"start": "2025-04-01", "end": "2025-04-30"},
                            "previous": {"start": "2025-03-01", "end": "2025-03-31"},
                        },
                        purpose="payroll variance",
                    ),
                ]
            )

    monkeypatch.setattr(gateway, "_structured", lambda _schema: FakeStructured())
    intent = IntentContext(
        intent="payroll_accounting_variance",
        current_start="2025-04-01",
        current_end="2025-04-30",
        previous_start="2025-03-01",
        previous_end="2025-03-31",
    )

    plan = gateway.plan(intent)

    assert "compare_sales_periods" not in {step.tool_name for step in plan}
    assert {step.tool_name for step in plan} == {
        "compare_payroll_periods",
        "compare_accounting_periods",
    }


@pytest.mark.parametrize(
    "question, expected_current, expected_previous",
    [
        (
            "¿Cómo evolucionaron las ventas de abril de 2025 respecto a marzo de 2025?",
            ("2025-04-01", "2025-04-30"),
            ("2025-03-01", "2025-03-31"),
        ),
        (
            "¿Por qué disminuyeron las ventas en septiembre de 2023?",
            ("2023-09-01", "2023-09-30"),
            ("2023-08-01", "2023-08-31"),
        ),
    ],
)
def test_explicit_months_are_resolved_without_hardcoded_periods(
    question: str,
    expected_current: tuple[str, str],
    expected_previous: tuple[str, str],
) -> None:
    intent = RuleBasedGateway().interpret(question)

    assert (intent.current_start, intent.current_end) == expected_current
    assert (intent.previous_start, intent.previous_end) == expected_previous
    assert intent.period_is_explicit is True


def test_explicit_out_of_coverage_period_returns_insufficient_data() -> None:
    result = run_analysis(
        "¿Por qué disminuyeron las ventas en septiembre de 2023?",
        RuleBasedGateway(),
        request_id="out-of-coverage",
    )

    assert result["status"] == "insufficient_data"
    assert "2023-09-01" in result["answer"]
    assert "caída" not in result["answer"].lower()


@pytest.mark.parametrize(
    "question",
    [
        "Elimina las ventas de abril de 2025.",
        "Ejecuta DROP TABLE sales_document.",
        "¿Cuál es el salario individual de cada empleado?",
        "¿Cuál es el pronóstico meteorológico de Santiago?",
    ],
)
def test_unsupported_boundaries_terminate_before_any_tool(question: str) -> None:
    result = run_analysis(question, RuleBasedGateway(), request_id="guardrail")

    assert result["status"] == "unsupported"
    assert result["analysis_performed"] == []


def test_cross_domain_routes_keep_domain_specific_tools() -> None:
    gateway = RuleBasedGateway()

    supply = gateway.interpret(
        "¿Qué productos con riesgo de quiebre tienen órdenes de compra pendientes?"
    )
    assert [step.tool_name for step in gateway.plan(supply)] == [
        "get_pending_purchase_orders",
        "find_stockout_products",
    ]

    finance = gateway.interpret(
        "¿Cuánto del aumento de gastos operativos corresponde a payroll?"
    )
    assert [step.tool_name for step in gateway.plan(finance)] == [
        "compare_payroll_periods",
        "compare_accounting_periods",
        "get_expense_variance_by_group",
    ]
