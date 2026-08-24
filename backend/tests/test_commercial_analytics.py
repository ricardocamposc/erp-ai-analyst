from datetime import date
from decimal import Decimal

from app.domain.commercial import investigate_sales_decline
from app.domain.common import Period
from app.domain.customers.service import (
    find_customers_with_sales_decline,
    get_customer_purchase_history,
)
from app.domain.inventory.service import get_out_of_stock_periods
from app.domain.sales.service import (
    compare_sales_periods,
    get_sales_by_customer,
    get_sales_by_product,
    get_sales_summary,
)

FEBRUARY = Period(date(2025, 2, 1), date(2025, 2, 28))
MARCH = Period(date(2025, 3, 1), date(2025, 3, 31))


def test_sales_summary_matches_ground_truth() -> None:
    assert get_sales_summary(FEBRUARY).total == Decimal("3586.00")
    assert get_sales_summary(MARCH).total == Decimal("2866.00")


def test_sales_comparison_and_product_contribution_are_deterministic() -> None:
    comparison = compare_sales_periods(MARCH, FEBRUARY)
    products = {item.key: item.total for item in get_sales_by_product(MARCH)}

    assert comparison.absolute_change == Decimal("-720.00")
    assert comparison.percentage_change == Decimal("-20.08")
    assert products["P-104"] == Decimal("416.00")
    assert (
        get_sales_by_customer(MARCH)[0].total >= get_sales_by_customer(MARCH)[-1].total
    )


def test_customer_history_and_decline_are_separate_from_stockout() -> None:
    history = get_customer_purchase_history("C-002", MARCH)
    declines = find_customers_with_sales_decline(MARCH, FEBRUARY)

    assert history.customer_key == "C-002"
    assert any(item.customer_key == "C-002" for item in declines)


def test_signature_investigation_preserves_correlation_boundary() -> None:
    result = investigate_sales_decline(MARCH, FEBRUARY)

    assert result.product_changes["P-104"] == Decimal("-1040.00")
    assert "P-104" in result.stockout_products
    assert result.relationship_type == "observed_correlation_only"


def test_stockout_period_has_no_false_customer_stockout_assignment() -> None:
    periods = get_out_of_stock_periods(MARCH)

    assert [(item.product_key, item.start) for item in periods] == [
        ("P-104", date(2025, 3, 1))
    ]
