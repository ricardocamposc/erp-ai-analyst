"""Bounded registry and execution boundary for all analytical tools."""

from collections.abc import Callable
from dataclasses import asdict, is_dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ValidationError

from app.domain.accounting import service as accounting
from app.domain.common import Period
from app.domain.customers import service as customers
from app.domain.inventory import service as inventory
from app.domain.payroll import service as payroll
from app.domain.purchases import service as purchases
from app.domain.sales import service as sales
from app.tools.contracts import (
    ComparisonRequest,
    EntityPeriodRequest,
    PeriodRequest,
    ToolResponse,
)


class ToolExecutionError(ValueError):
    """Safe normalized failure at the typed tool boundary."""


def _period(request: Any) -> Period:
    return Period(request.start, request.end)


def _json_value(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _json_value(item) for key, item in asdict(value).items()}  # type: ignore[arg-type]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, Decimal):
        whole, _, fraction = format(value, "f").partition(".")
        return f"{whole}.{fraction.rstrip('0').ljust(2, '0')}"
    if isinstance(value, date):
        return str(value)
    return value


def _response(name: str, domain: str, value: Any, request: Any) -> ToolResponse:
    data = _json_value(value)
    if isinstance(data, list):
        data = data[: request.limit]
    evidence = [
        {
            "tool_name": name,
            "query_id": f"{domain}.{name}.v1",
            "period_start": request.start,
            "period_end": request.end,
            "metric": name,
            "contributing_keys": [],
        }
    ]
    return ToolResponse(tool_name=name, domain=domain, data=data, evidence=evidence)


def _execute(
    name: str,
    domain: str,
    model: type[BaseModel],
    payload: dict[str, Any],
    handler: Callable[[Any], Any],
) -> ToolResponse:
    try:
        request = model.model_validate(payload)
        value = handler(request)
        period = request.current if isinstance(request, ComparisonRequest) else request
        return _response(name, domain, value, period)
    except (ValidationError, ValueError) as error:
        raise ToolExecutionError(
            f"{name}: invalid request or execution failure"
        ) from error


def _comparison(
    request: ComparisonRequest, operation: Callable[[Period, Period], Any]
) -> Any:
    return operation(_period(request.current), _period(request.previous))


def _build_specs() -> dict[str, tuple[str, type[BaseModel], Callable[[Any], Any]]]:
    period = PeriodRequest
    entity = EntityPeriodRequest
    comparison = ComparisonRequest
    return {
        "get_sales_summary": (
            "sales",
            period,
            lambda r: sales.get_sales_summary(_period(r)),
        ),
        "compare_sales_periods": (
            "sales",
            comparison,
            lambda r: _comparison(r, sales.compare_sales_periods),
        ),
        "get_sales_by_customer": (
            "sales",
            period,
            lambda r: sales.get_sales_by_customer(_period(r)),
        ),
        "get_sales_by_product": (
            "sales",
            period,
            lambda r: sales.get_sales_by_product(_period(r)),
        ),
        "get_sales_by_salesperson": (
            "sales",
            period,
            lambda r: sales.get_sales_by_salesperson(_period(r)),
        ),
        "get_customer_purchase_history": (
            "customers",
            entity,
            lambda r: customers.get_customer_purchase_history(r.entity_key, _period(r)),
        ),
        "find_customers_with_sales_decline": (
            "customers",
            comparison,
            lambda r: customers.find_customers_with_sales_decline(
                _period(r.current), _period(r.previous)
            ),
        ),
        "get_stock_history": (
            "inventory",
            entity,
            lambda r: inventory.get_stock_history(r.entity_key, _period(r)),
        ),
        "get_out_of_stock_periods": (
            "inventory",
            period,
            lambda r: inventory.get_out_of_stock_periods(_period(r)),
        ),
        "find_stockout_products": (
            "inventory",
            period,
            lambda r: inventory.find_stockout_products(_period(r)),
        ),
        "get_purchase_summary": (
            "purchases",
            period,
            lambda r: purchases.get_purchase_summary(_period(r)),
        ),
        "get_purchases_by_supplier": (
            "purchases",
            period,
            lambda r: purchases.get_purchases_by_supplier(_period(r)),
        ),
        "get_purchases_by_product": (
            "purchases",
            period,
            lambda r: purchases.get_purchases_by_product(_period(r)),
        ),
        "get_purchase_price_history": (
            "purchases",
            entity,
            lambda r: purchases.get_purchase_price_history(r.entity_key, _period(r)),
        ),
        "get_pending_purchase_orders": (
            "purchases",
            period,
            lambda r: purchases.get_pending_purchase_orders(_period(r)),
        ),
        "get_supplier_delivery_performance": (
            "purchases",
            period,
            lambda r: purchases.get_supplier_delivery_performance(_period(r)),
        ),
        "get_product_inbound_supply": (
            "purchases",
            entity,
            lambda r: purchases.get_product_inbound_supply(r.entity_key, _period(r)),
        ),
        "get_payroll_cost_summary": (
            "payroll",
            period,
            lambda r: payroll.get_payroll_cost_summary(_period(r)),
        ),
        "compare_payroll_periods": (
            "payroll",
            comparison,
            lambda r: _comparison(r, payroll.compare_payroll_periods),
        ),
        "get_payroll_cost_by_cost_center": (
            "payroll",
            period,
            lambda r: payroll.get_payroll_cost_by_cost_center(_period(r)),
        ),
        "get_payroll_cost_by_concept": (
            "payroll",
            period,
            lambda r: payroll.get_payroll_cost_by_concept(_period(r)),
        ),
        "get_overtime_cost_trend": (
            "payroll",
            period,
            lambda r: payroll.get_overtime_cost_trend(_period(r)),
        ),
        "get_accounting_period_summary": (
            "accounting",
            period,
            lambda r: accounting.get_accounting_period_summary(_period(r)),
        ),
        "compare_accounting_periods": (
            "accounting",
            comparison,
            lambda r: _comparison(r, accounting.compare_accounting_periods),
        ),
        "get_expense_variance_by_group": (
            "accounting",
            comparison,
            lambda r: accounting.get_expense_variance_by_group(
                _period(r.current), _period(r.previous)
            ),
        ),
        "get_cost_center_expenses": (
            "accounting",
            period,
            lambda r: accounting.get_cost_center_expenses(_period(r)),
        ),
        "get_gross_margin_summary": (
            "accounting",
            period,
            lambda r: accounting.get_gross_margin_summary(_period(r)),
        ),
    }


_SPECS = _build_specs()


def get_tool_registry() -> dict[str, dict[str, str]]:
    return {
        name: {"domain": spec[0], "input_model": spec[1].__name__}
        for name, spec in _SPECS.items()
    }


def validate_tool_arguments(name: str, payload: dict[str, Any]) -> None:
    """Validate a planned call before it is allowed into the workflow."""

    if name not in _SPECS:
        raise ToolExecutionError(f"unknown tool: {name}")
    try:
        _SPECS[name][1].model_validate(payload)
    except ValidationError as error:
        raise ToolExecutionError(
            f"{name}: invalid request or execution failure"
        ) from error


def execute_tool(name: str, payload: dict[str, Any]) -> ToolResponse:
    if name not in _SPECS:
        raise ToolExecutionError(f"unknown tool: {name}")
    domain, model, handler = _SPECS[name]
    return _execute(name, domain, model, payload, handler)
