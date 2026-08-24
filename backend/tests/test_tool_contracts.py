from datetime import date

import pytest

from app.tools.registry import ToolExecutionError, execute_tool, get_tool_registry

PERIOD = {"start": date(2025, 3, 1), "end": date(2025, 3, 31)}


def test_registry_covers_all_six_domains_without_write_or_sql_tools() -> None:
    registry = get_tool_registry()
    domains = {item["domain"] for item in registry.values()}

    assert domains == {
        "sales",
        "customers",
        "inventory",
        "purchases",
        "payroll",
        "accounting",
    }
    assert not any(
        "sql" in name or name.startswith(("create_", "update_", "delete_"))
        for name in registry
    )


def test_tool_validates_input_and_returns_evidence() -> None:
    result = execute_tool("get_sales_summary", PERIOD)

    assert result.tool_name == "get_sales_summary"
    assert result.domain == "sales"
    assert result.evidence[0]["query_id"] == "sales.get_sales_summary.v1"
    assert isinstance(result.data, dict)
    assert result.data["total"] == "2866.00"


def test_tool_enforces_result_limit_and_unknown_tool_error() -> None:
    result = execute_tool("get_sales_by_product", {**PERIOD, "limit": 1})

    assert len(result.data) == 1
    with pytest.raises(ToolExecutionError):
        execute_tool("run_sql", PERIOD)


def test_invalid_period_and_extra_arguments_are_rejected() -> None:
    with pytest.raises(ToolExecutionError):
        execute_tool(
            "get_sales_summary", {"start": date(2025, 4, 1), "end": date(2025, 3, 1)}
        )
    with pytest.raises(ToolExecutionError):
        execute_tool("get_sales_summary", {**PERIOD, "sql": "SELECT 1"})
