"""Model gateways: OpenAI production boundary and deterministic test gateway."""

from typing import Any, Protocol, cast

from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from app.agent.contracts import (
    FinalAnswer,
    IntentContext,
    PlannedToolCall,
    PlanResponse,
)
from app.core.config import get_settings
from app.tools.registry import (
    ToolExecutionError,
    validate_tool_arguments,
)


class ModelGateway(Protocol):
    def interpret(self, question: str) -> IntentContext: ...

    def plan(self, intent: IntentContext) -> list[PlannedToolCall]: ...

    def synthesize(
        self, question: str, results: list[dict[str, Any]]
    ) -> FinalAnswer: ...


def _default_periods() -> dict[str, str]:
    return {
        "current_start": "2025-03-01",
        "current_end": "2025-03-31",
        "previous_start": "2025-02-01",
        "previous_end": "2025-02-28",
    }


def _tool_names(steps: list[PlannedToolCall]) -> set[str]:
    return {step.tool_name for step in steps}


def _sales_decline_guardrail(
    answer: FinalAnswer, question: str, results: list[dict[str, Any]]
) -> FinalAnswer:
    """Prevent synthesis from asserting a decline absent deterministic evidence."""

    comparison = next(
        (
            result.get("data", {})
            for result in results
            if result.get("tool_name") == "compare_sales_periods"
        ),
        None,
    )
    if not isinstance(comparison, dict):
        return answer

    current = comparison.get("current", {})
    previous = comparison.get("previous", {})
    try:
        current_total = float(current.get("total", 0))
        previous_total = float(previous.get("total", 0))
        absolute_change = float(comparison.get("absolute_change", 0))
    except (TypeError, ValueError):
        return answer

    if absolute_change < 0:
        return answer

    current_period = current.get("period", {})
    previous_period = previous.get("period", {})
    no_rows = not current.get("line_count") and not previous.get("line_count")
    if no_rows:
        message = (
            "No se puede determinar una variación: no hay ventas registradas para "
            f"{current_period.get('start')}–{current_period.get('end')} ni "
            f"para el período anterior ({previous_period.get('start')}–"
            f"{previous_period.get('end')})."
        )
        return answer.model_copy(
            update={
                "answer": message,
                "key_findings": [message],
                "status": "insufficient_data",
                "warnings": list(
                    dict.fromkeys(
                        answer.warnings
                        + [
                            "El período consultado está fuera del rango de datos de ventas disponible."
                        ]
                    )
                ),
            }
        )

    message = (
        "No se observa una disminución de ventas en los datos determinísticos: "
        f"current={current_total:.2f}, previous={previous_total:.2f}, "
        f"absolute_change={absolute_change:.2f}."
    )
    return answer.model_copy(update={"answer": message, "key_findings": [message]})


class RuleBasedGateway:
    """Deterministic gateway used for offline tests and safe local fallback."""

    def interpret(self, question: str) -> IntentContext:
        lowered = question.lower()
        periods = _default_periods()
        if (
            ("payroll" in lowered or "nómina" in lowered)
            and ("gasto" in lowered or "operativo" in lowered or "aumento" in lowered)
        ) or "horas extra" in lowered:
            periods = {
                "current_start": "2025-04-01",
                "current_end": "2025-04-30",
                "previous_start": "2025-03-01",
                "previous_end": "2025-03-31",
            }
            intent = "payroll_accounting_variance"
        elif (
            "quiebre" in lowered or "stock" in lowered or "inventario" in lowered
        ) and (
            "orden" in lowered
            or "compra" in lowered
            or "pendiente" in lowered
            or "inbound" in lowered
            or "abastecimiento" in lowered
        ):
            intent = "supply_chain_analysis"
        elif "nómina" in lowered or "payroll" in lowered:
            periods = {
                "current_start": "2025-04-01",
                "current_end": "2025-04-30",
                "previous_start": "2025-03-01",
                "previous_end": "2025-03-31",
            }
            intent = "payroll_accounting_variance"
        elif (
            "margen" in lowered
            or "gastos operativos" in lowered
            or "resultado operativo" in lowered
        ):
            intent = "accounting_variance"
        elif "stock" in lowered or "inventario" in lowered or "quiebre" in lowered:
            intent = "inventory_analysis"
        elif "cliente" in lowered or "clientes" in lowered:
            intent = "customer_analysis"
        elif (
            "compra" in lowered or "proveedor" in lowered or "abastecimiento" in lowered
        ):
            intent = "supply_chain_analysis"
        elif (
            "impuesto" in lowered
            or "contrato" in lowered
            or "modifica" in lowered
            or "sql" in lowered
        ):
            intent = "unsupported_request"
        else:
            intent = "sales_variance_analysis"
        return IntentContext(
            intent=intent,
            **periods,
            supported=intent != "unsupported_request",
            warning="La evidencia permite observar relaciones, no demostrar causalidad."
            if intent != "unsupported_request"
            else "La solicitud está fuera del alcance read-only analítico.",
        )

    def plan(self, intent: IntentContext) -> list[PlannedToolCall]:
        period = {"start": intent.current_start, "end": intent.current_end}
        previous = {"start": intent.previous_start, "end": intent.previous_end}
        if not intent.supported:
            return []
        if intent.intent == "payroll_accounting_variance":
            return [
                PlannedToolCall(
                    tool_name="compare_payroll_periods",
                    arguments={"current": period, "previous": previous},
                    purpose="comparar coste agregado de nómina",
                ),
                PlannedToolCall(
                    tool_name="compare_accounting_periods",
                    arguments={"current": period, "previous": previous},
                    purpose="comparar resultado operativo agregado",
                ),
            ]
        if intent.intent == "accounting_variance":
            return [
                PlannedToolCall(
                    tool_name="compare_accounting_periods",
                    arguments={"current": period, "previous": previous},
                    purpose="comparar resultado operativo agregado",
                ),
                PlannedToolCall(
                    tool_name="get_gross_margin_summary",
                    arguments=period,
                    purpose="revisar margen bruto agregado",
                ),
            ]
        if intent.intent == "inventory_analysis":
            return [
                PlannedToolCall(
                    tool_name="get_stock_history",
                    arguments={**period, "entity_key": "P-104"},
                    purpose="revisar historial de stock",
                ),
                PlannedToolCall(
                    tool_name="find_stockout_products",
                    arguments=period,
                    purpose="identificar quiebres observados",
                ),
            ]
        if intent.intent == "customer_analysis":
            return [
                PlannedToolCall(
                    tool_name="get_customer_purchase_history",
                    arguments={**period, "entity_key": "C-002"},
                    purpose="revisar historial del cliente",
                ),
                PlannedToolCall(
                    tool_name="find_customers_with_sales_decline",
                    arguments={"current": period, "previous": previous},
                    purpose="identificar reducciones de compra",
                ),
            ]
        if intent.intent == "supply_chain_analysis":
            return [
                PlannedToolCall(
                    tool_name="get_pending_purchase_orders",
                    arguments=period,
                    purpose="revisar inbound pendiente",
                ),
                PlannedToolCall(
                    tool_name="find_stockout_products",
                    arguments=period,
                    purpose="revisar disponibilidad observada",
                ),
            ]
        return [
            PlannedToolCall(
                tool_name="compare_sales_periods",
                arguments={"current": period, "previous": previous},
                purpose="medir la variación de ventas",
            ),
            PlannedToolCall(
                tool_name="get_sales_by_product",
                arguments=period,
                purpose="identificar contribución por producto",
            ),
            PlannedToolCall(
                tool_name="get_sales_by_customer",
                arguments=period,
                purpose="identificar contribución por cliente",
            ),
            PlannedToolCall(
                tool_name="find_stockout_products",
                arguments=period,
                purpose="inspeccionar coincidencias de stockout",
            ),
        ]

    @staticmethod
    def allowed_tools(intent: IntentContext) -> set[str]:
        """Return the tools belonging to the deterministic route for an intent."""

        return _tool_names(RuleBasedGateway().plan(intent))

    def synthesize(self, question: str, results: list[dict[str, Any]]) -> FinalAnswer:
        if not results:
            return FinalAnswer(
                answer="No hay evidencia suficiente para responder con seguridad.",
                status="insufficient_data",
                warnings=["No se ejecutaron tools compatibles."],
            )
        findings: list[str] = []
        evidence: list[dict[str, Any]] = []
        for result in results:
            evidence.extend(result.get("evidence", []))
            data = result.get("data", {})
            if result.get("tool_name") == "compare_sales_periods":
                findings.append(
                    f"La variación observada de ventas es {data.get('absolute_change')}."
                )
            elif result.get("tool_name") == "find_stockout_products":
                findings.append(
                    f"Productos con stockout observado: {', '.join(data) if data else 'ninguno'}."
                )
            elif result.get("tool_name") == "compare_payroll_periods":
                findings.append(
                    f"La variación agregada de nómina es {data.get('absolute_change')}."
                )
        answer = FinalAnswer(
            answer="; ".join(findings)
            or "Se completó el análisis con evidencia estructurada.",
            key_findings=findings,
            evidence=evidence,
            analysis_performed=[item.get("tool_name", "") for item in results],
            structured_data=[
                {"tool_name": item.get("tool_name", ""), "data": item.get("data", {})}
                for item in results
            ],
            warnings=[
                "Las coincidencias entre dominios son observaciones; no prueban causalidad."
            ],
            status="completed",
        )
        return _sales_decline_guardrail(answer, question, results)


class OpenAIGateway:
    """OpenAI structured-output gateway; calculations remain in registered tools."""

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self.model = model or settings.openai_model
        self.api_key = settings.openai_api_key

    def _structured(self, schema: type[Any]) -> Any:
        return ChatOpenAI(
            model=self.model,
            temperature=0,
            api_key=self.api_key,
        ).with_structured_output(schema, method="function_calling")

    def interpret(self, question: str) -> IntentContext:
        prompt = "Extract intent and ISO periods for a read-only ERP analytics question. Reject write actions, SQL, tax/legal advice and individual PeopleOps analysis."
        result = self._structured(IntentContext).invoke(
            [("system", prompt), ("human", question)]
        )
        return cast(IntentContext, result)

    def plan(self, intent: IntentContext) -> list[PlannedToolCall]:
        fallback_steps = RuleBasedGateway().plan(intent)
        allowed_tools = sorted(_tool_names(fallback_steps))
        prompt = (
            "Create a bounded plan for this intent using only the allowed tools "
            f"{allowed_tools}. Do not use tools from another ERP domain. "
            "Never write SQL. Use no more than 6 calls."
        )
        result = self._structured(PlanResponse).invoke(
            [("system", prompt), ("human", intent.model_dump_json())]
        )
        model_steps = cast(PlanResponse, result).steps
        valid_model_steps: list[PlannedToolCall] = []
        for step in model_steps:
            try:
                validate_tool_arguments(step.tool_name, step.arguments)
            except ToolExecutionError:
                continue
            if step.tool_name in allowed_tools:
                valid_model_steps.append(step)
        # Preserve a bounded multi-step investigation when the model returns a
        # prematurely short plan; the fallback adds only registered tools.
        merged = valid_model_steps
        seen = {step.tool_name for step in merged}
        for step in fallback_steps:
            if step.tool_name not in seen and len(merged) < 6:
                merged.append(step)
                seen.add(step.tool_name)
        return merged

    def synthesize(self, question: str, results: list[dict[str, Any]]) -> FinalAnswer:
        prompt = "Synthesize only from deterministic tool results. Preserve all numeric values. Separate facts from observed correlations and never claim unsupported causality."
        try:
            result = self._structured(FinalAnswer).invoke(
                [
                    ("system", prompt),
                    ("human", f"Question: {question}\nResults: {results}"),
                ]
            )
            return _sales_decline_guardrail(
                cast(FinalAnswer, result), question, results
            )
        except (ValidationError, ValueError):
            # A malformed model envelope must not turn a valid deterministic
            # tool run into a 502. The fallback preserves the tool evidence.
            return RuleBasedGateway().synthesize(question, results)
