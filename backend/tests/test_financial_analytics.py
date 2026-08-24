from datetime import date
from decimal import Decimal

from app.domain.accounting.service import (
    compare_accounting_periods,
    get_accounting_period_summary,
    get_cost_center_expenses,
    get_expense_variance_by_group,
    get_gross_margin_summary,
)
from app.domain.common import Period
from app.domain.financial import investigate_payroll_expense
from app.domain.payroll.service import (
    compare_payroll_periods,
    get_overtime_cost_trend,
    get_payroll_cost_by_concept,
    get_payroll_cost_by_cost_center,
)

FEBRUARY = Period(date(2025, 2, 1), date(2025, 2, 28))
MARCH = Period(date(2025, 3, 1), date(2025, 3, 31))
APRIL = Period(date(2025, 4, 1), date(2025, 4, 30))


def test_payroll_totals_concepts_centers_and_overtime() -> None:
    comparison = compare_payroll_periods(APRIL, MARCH)
    concepts = {item.key: item.amount for item in get_payroll_cost_by_concept(APRIL)}
    trend = get_overtime_cost_trend(Period(date(2025, 1, 1), APRIL.end))

    assert comparison.absolute_change == Decimal("1653.00")
    assert concepts["PC-OT"] == Decimal("2199.00")
    assert len(get_payroll_cost_by_cost_center(APRIL)) == 3
    assert trend[-1].amount > trend[-2].amount


def test_accounting_summary_margin_result_and_variance() -> None:
    march = get_accounting_period_summary(MARCH)
    comparison = compare_accounting_periods(MARCH, FEBRUARY)

    assert march.revenue == Decimal("2866.00")
    assert march.costs == Decimal("-1164.00")
    assert march.gross_margin == Decimal("1702.00")
    assert comparison.operating_result_change < 0
    assert get_gross_margin_summary(MARCH) == Decimal("1702.00")
    assert get_expense_variance_by_group(MARCH, FEBRUARY)[0].key == "6100"
    assert get_cost_center_expenses(MARCH)[0].key == "CC-OPS"


def test_payroll_to_accounting_composition_is_bounded() -> None:
    result = investigate_payroll_expense(APRIL, MARCH)

    assert result.overtime_contribution == Decimal("1653.00")
    assert result.relationship_type == "observed_operating_expense_contribution"
    assert not hasattr(result, "employee_details")
