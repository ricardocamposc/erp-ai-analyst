"""Model gateways: OpenAI production boundary and deterministic test gateway."""

import calendar
import re
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


_SPANISH_MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}


def _month_period(year: int, month: int) -> tuple[str, str]:
    last_day = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}"


def _default_periods() -> dict[str, str]:
    return {
        "current_start": "2025-04-01",
        "current_end": "2025-04-30",
        "previous_start": "2025-03-01",
        "previous_end": "2025-03-31",
    }


def _resolve_explicit_periods(question: str) -> dict[str, str]:
    """Resolve explicit Spanish month/year references into exact boundaries."""

    lowered = question.lower()
    month_pattern = (
        r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
        r"septiembre|setiembre|octubre|noviembre|diciembre"
    )
    pair = re.search(
        rf"entre\s+({month_pattern})\s+y\s+({month_pattern})\s+(?:de\s+)?(20\d{{2}})",
        lowered,
    )
    if pair:
        previous_start, previous_end = _month_period(
            int(pair.group(3)), _SPANISH_MONTHS[pair.group(1)]
        )
        current_start, current_end = _month_period(
            int(pair.group(3)), _SPANISH_MONTHS[pair.group(2)]
        )
        return {
            "current_start": current_start, "current_end": current_end,
            "previous_start": previous_start, "previous_end": previous_end,
        }

    matches = list(re.finditer(rf"({month_pattern})\s+(?:de\s+)?(20\d{{2}})", lowered))
    if not matches:
        return _default_periods()
    current_year = int(matches[0].group(2))
    current_month = _SPANISH_MONTHS[matches[0].group(1)]
    current_start, current_end = _month_period(current_year, current_month)
    if len(matches) > 1:
        previous_start, previous_end = _month_period(
            int(matches[1].group(2)), _SPANISH_MONTHS[matches[1].group(1)]
        )
    else:
        previous_year, previous_month = (
            (current_year - 1, 12) if current_month == 1 else (current_year, current_month - 1)
        )
        previous_start, previous_end = _month_period(previous_year, previous_month)
    return {
        "current_start": current_start, "current_end": current_end,
        "previous_start": previous_start, "previous_end": previous_end,
    }


def _has_explicit_period(question: str) -> bool:
    return bool(re.search(r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)\s+(?:de\s+)?20\d{2}", question.lower()))


def _range_bounds(question: str) -> tuple[str, str] | None:
    lowered = question.lower()
    month_pattern = "|".join(_SPANISH_MONTHS)
    match = re.search(
        rf"entre\s+({month_pattern})\s+y\s+({month_pattern})\s+(?:de\s+)?(20\d{{2}})",
        lowered,
    )
    if not match:
        return None
    start, _ = _month_period(int(match.group(3)), _SPANISH_MONTHS[match.group(1)])
    _, end = _month_period(int(match.group(3)), _SPANISH_MONTHS[match.group(2)])
    return start, end


def _unsupported_intent(question: str) -> IntentContext | None:
    lowered = question.lower()
    if re.search(r"\b(elimina|eliminar|borrar|borra|actualiza|modifica|inserta|crear|crea|delete|drop|truncate|update|insert|alter)\b", lowered):
        warning = "Las operaciones de escritura no están permitidas."
    elif re.search(r"\b(drop\s+table|select\s+.*from|insert\s+into|update\s+\w+|sql)\b", lowered):
        warning = "La ejecución de SQL arbitrario no está permitida."
    elif re.search(r"salario\s+individual|salarios\s+individuales|por empleado|cada empleado", lowered):
        warning = "El análisis de payroll está limitado a datos agregados y no sensibles."
    elif re.search(r"pronóstico meteorológico|pronostico meteorologico|clima|weather|meteorología|meteorologia", lowered):
        warning = "La solicitud está fuera del alcance de ERP AI Analyst."
    else:
        return None
    return IntentContext(
        intent="unsupported_request", **_resolve_explicit_periods(question),
        period_is_explicit=_has_explicit_period(question),
        range_start=(_range_bounds(question) or (None, None))[0],
        range_end=(_range_bounds(question) or (None, None))[1],
        supported=False, warning=warning,
    )


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
        unsupported = _unsupported_intent(question)
        if unsupported:
            return unsupported
        periods = _resolve_explicit_periods(question)
        if ("cliente" in lowered or "clientes" in lowered) and (
            "inventario" in lowered or "stock" in lowered
        ):
            intent = "customer_inventory_analysis"
        elif "stockout" in lowered or "causó" in lowered or "causo" in lowered:
            intent = "sales_variance_analysis"
        elif "analiza ventas" in lowered and "inventario" in lowered and "compras" in lowered:
            intent = "sales_supply_chain_analysis"
        elif "retraso" in lowered or "retrasos" in lowered:
            intent = "supplier_delivery_analysis"
        elif "cuánto" in lowered and "gastos" in lowered and ("payroll" in lowered or "nómina" in lowered):
            intent = "payroll_expense_variance"
        elif (
            ("payroll" in lowered or "nómina" in lowered)
            and ("gasto" in lowered or "operativo" in lowered or "aumento" in lowered)
            and "conceptos" not in lowered
            and "centros de costo" not in lowered
            and "centro de costo" not in lowered
        ) or "horas extra" in lowered:
            intent = "payroll_accounting_variance"
        elif ("costo de compra" in lowered or "precio de compra" in lowered) and "margen" in lowered:
            intent = "purchase_accounting_analysis"
        elif "costo de compra" in lowered or "precio de compra" in lowered:
            intent = "purchase_price_analysis"
        elif "conceptos" in lowered and ("nómina" in lowered or "payroll" in lowered):
            intent = "payroll_concept_analysis"
        elif ("centros de costo" in lowered or "centro de costo" in lowered) and ("nómina" in lowered or "payroll" in lowered):
            intent = "payroll_cost_center_analysis"
        elif "grupo" in lowered and "gastos" in lowered:
            intent = "accounting_expense_analysis"
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
            intent = "payroll_accounting_variance"
        elif (
            "margen" in lowered
            or "gastos operativos" in lowered
            or "resultado operativo" in lowered
        ) and not ("grupo" in lowered and "gastos" in lowered):
            intent = "accounting_variance"
        elif "stock" in lowered or "inventario" in lowered or "quiebre" in lowered:
            intent = "inventory_analysis"
        elif ("qué clientes" in lowered or "que clientes" in lowered) and ("aportó" in lowered or "aporto" in lowered or "ventas" in lowered):
            intent = "customer_sales_breakdown"
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
            period_is_explicit=_has_explicit_period(question),
            range_start=(_range_bounds(question) or (None, None))[0],
            range_end=(_range_bounds(question) or (None, None))[1],
            supported=intent != "unsupported_request",
            warning="La evidencia permite observar relaciones, no demostrar causalidad; cualquier correlation es sólo observada."
            if intent != "unsupported_request"
            else "La solicitud está fuera del alcance read-only analítico.",
        )

    def plan(self, intent: IntentContext) -> list[PlannedToolCall]:
        period = {"start": intent.current_start, "end": intent.current_end}
        previous = {"start": intent.previous_start, "end": intent.previous_end}
        covered_data = {"start": "2025-01-01", "end": "2025-04-30"}
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
        if intent.intent == "payroll_expense_variance":
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
                PlannedToolCall(
                    tool_name="get_expense_variance_by_group",
                    arguments={"current": period, "previous": previous},
                    purpose="aislar la variación del gasto de payroll",
                ),
            ]
        if intent.intent in {"payroll_concept_analysis", "payroll_cost_center_analysis"}:
            steps = [
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
            if intent.intent == "payroll_concept_analysis":
                steps.append(
                    PlannedToolCall(
                        tool_name="get_payroll_cost_by_concept",
                        arguments=period,
                        purpose="desglosar conceptos agregados de nómina",
                    )
                )
            else:
                steps.append(
                    PlannedToolCall(
                        tool_name="get_payroll_cost_by_cost_center",
                        arguments=period,
                        purpose="desglosar nómina por centro de costo",
                    )
                )
            return steps
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
        if intent.intent == "accounting_expense_analysis":
            return [
                PlannedToolCall(
                    tool_name="compare_accounting_periods",
                    arguments={"current": period, "previous": previous},
                    purpose="comparar resultado operativo agregado",
                ),
                PlannedToolCall(
                    tool_name="get_expense_variance_by_group",
                    arguments={"current": period, "previous": previous},
                    purpose="identificar grupo de gasto con mayor variación",
                ),
            ]
        if intent.intent == "purchase_accounting_analysis":
            return [
                PlannedToolCall(
                    tool_name="get_purchase_price_history",
                    arguments={**period, "entity_key": "P-104"},
                    purpose="revisar variación del precio de compra",
                ),
                PlannedToolCall(
                    tool_name="get_gross_margin_summary",
                    arguments=period,
                    purpose="revisar margen bruto observado",
                ),
            ]
        if intent.intent == "purchase_price_analysis":
            price_period = period if intent.period_is_explicit else covered_data
            return [
                PlannedToolCall(
                    tool_name="get_purchase_price_history",
                    arguments={**price_period, "entity_key": "P-104"},
                    purpose="revisar evolución del precio de compra",
                )
            ]
        if intent.intent == "supplier_delivery_analysis":
            supply_period = period if intent.period_is_explicit else covered_data
            return [
                PlannedToolCall(
                    tool_name="get_supplier_delivery_performance",
                    arguments=supply_period,
                    purpose="medir retrasos observados por proveedor",
                ),
                PlannedToolCall(
                    tool_name="get_product_inbound_supply",
                    arguments={**supply_period, "entity_key": "P-104"},
                    purpose="revisar inbound pendiente del producto crítico",
                ),
            ]
        if intent.intent == "inventory_analysis":
            inventory_period = (
                {"start": intent.range_start, "end": intent.range_end}
                if intent.range_start and intent.range_end
                else period if intent.period_is_explicit else covered_data
            )
            return [
                PlannedToolCall(
                    tool_name="get_stock_history",
                    arguments={**inventory_period, "entity_key": "P-104"},
                    purpose="revisar historial de stock",
                ),
                PlannedToolCall(
                    tool_name="find_stockout_products",
                    arguments=inventory_period,
                    purpose="identificar quiebres observados",
                ),
            ]
        if intent.intent == "customer_analysis":
            history_period = period if intent.period_is_explicit else covered_data
            return [
                PlannedToolCall(
                    tool_name="get_customer_purchase_history",
                    arguments={**history_period, "entity_key": "C-002"},
                    purpose="revisar historial del cliente",
                ),
                PlannedToolCall(
                    tool_name="find_customers_with_sales_decline",
                    arguments={"current": period, "previous": previous},
                    purpose="identificar reducciones de compra",
                ),
            ]
        if intent.intent == "customer_sales_breakdown":
            return [
                PlannedToolCall(
                    tool_name="get_sales_by_customer",
                    arguments=period,
                    purpose="desglosar ventas por cliente",
                )
            ]
        if intent.intent == "customer_inventory_analysis":
            analysis_period = (
                {"start": intent.range_start, "end": intent.range_end}
                if intent.range_start and intent.range_end
                else period if intent.period_is_explicit else covered_data
            )
            return [
                PlannedToolCall(
                    tool_name="get_customer_purchase_history",
                    arguments={**analysis_period, "entity_key": "C-002"},
                    purpose="revisar historial del cliente",
                ),
                PlannedToolCall(
                    tool_name="find_customers_with_sales_decline",
                    arguments={"current": period, "previous": previous},
                    purpose="identificar reducción de compra",
                ),
                PlannedToolCall(
                    tool_name="get_stock_history",
                    arguments={**analysis_period, "entity_key": "P-104"},
                    purpose="revisar historial del producto relacionado",
                ),
                PlannedToolCall(
                    tool_name="find_stockout_products",
                    arguments=analysis_period,
                    purpose="identificar quiebres observados",
                ),
            ]
        if intent.intent == "supply_chain_analysis":
            supply_period = period if intent.period_is_explicit else covered_data
            return [
                PlannedToolCall(
                    tool_name="get_pending_purchase_orders",
                    arguments=supply_period,
                    purpose="revisar inbound pendiente",
                ),
                PlannedToolCall(
                    tool_name="find_stockout_products",
                    arguments=supply_period,
                    purpose="revisar disponibilidad observada",
                ),
            ]
        if intent.intent == "sales_supply_chain_analysis":
            return [
                PlannedToolCall(
                    tool_name="compare_sales_periods",
                    arguments={"current": period, "previous": previous},
                    purpose="medir desempeño comercial",
                ),
                PlannedToolCall(
                    tool_name="get_sales_by_product",
                    arguments=period,
                    purpose="identificar contribución de P-104",
                ),
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
            elif result.get("tool_name") == "get_gross_margin_summary":
                findings.append(f"El margen bruto (gross margin) observado es {data}.")
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
        unsupported = _unsupported_intent(question)
        if unsupported:
            return unsupported
        prompt = "Extract intent and ISO periods for a read-only ERP analytics question. Reject write actions, SQL, tax/legal advice and individual PeopleOps analysis."
        result = self._structured(IntentContext).invoke(
            [("system", prompt), ("human", question)]
        )
        model_intent = cast(IntentContext, result)

        # Keep the LLM in the reasoning path, but constrain routing to the
        # deterministic route already covered by the offline ground truth. A
        # wrong broad intent can otherwise expose the generic sales tools to a
        # payroll, accounting, purchasing, inventory or cross-domain question.
        bounded_intent = RuleBasedGateway().interpret(question)
        if (
            model_intent.intent != bounded_intent.intent
            or model_intent.supported != bounded_intent.supported
        ):
            return model_intent.model_copy(
                update={
                    "intent": bounded_intent.intent,
                    "current_start": bounded_intent.current_start,
                    "current_end": bounded_intent.current_end,
                    "previous_start": bounded_intent.previous_start,
                    "previous_end": bounded_intent.previous_end,
                    "period_is_explicit": bounded_intent.period_is_explicit,
                    "range_start": bounded_intent.range_start,
                    "range_end": bounded_intent.range_end,
                    "supported": bounded_intent.supported,
                    "warning": bounded_intent.warning,
                }
            )
        return model_intent

    def plan(self, intent: IntentContext) -> list[PlannedToolCall]:
        fallback_steps = RuleBasedGateway().plan(intent)
        allowed_tools = sorted(_tool_names(fallback_steps))
        prompt = (
            "Create a bounded plan for this intent using only the allowed tools "
            f"{allowed_tools}. Do not use tools from another ERP domain. "
            "Never write SQL. Use no more than 6 calls. Include a short purpose "
            "for each step when possible; purpose is optional and must never block "
            "a valid tool plan."
        )
        result = self._structured(PlanResponse).invoke(
            [("system", prompt), ("human", intent.model_dump_json())]
        )
        # Keep the model-facing schema portable; enforce the workflow bound in
        # application code instead of emitting unsupported JSON Schema limits.
        model_steps = cast(PlanResponse, result).steps[:6]
        valid_model_steps: list[PlannedToolCall] = []
        model_seen: set[str] = set()
        for step in model_steps:
            try:
                validate_tool_arguments(step.tool_name, step.arguments)
            except ToolExecutionError:
                continue
            if step.tool_name in allowed_tools and step.tool_name not in model_seen:
                if not step.purpose.strip():
                    step = step.model_copy(
                        update={
                            "purpose": (
                                "Execute the registered tool for deterministic "
                                f"evidence: {step.tool_name}"
                            )
                        }
                    )
                valid_model_steps.append(step)
                model_seen.add(step.tool_name)
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
