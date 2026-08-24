from datetime import date
from decimal import Decimal

from app.domain.common import Period
from app.domain.purchases.service import (
    get_pending_purchase_orders,
    get_product_inbound_supply,
    get_purchase_price_history,
    get_purchase_summary,
    get_purchases_by_supplier,
    get_supplier_delivery_performance,
)
from app.domain.supply_chain import investigate_product_supply

FEBRUARY = Period(date(2025, 2, 1), date(2025, 2, 28))
MARCH = Period(date(2025, 3, 1), date(2025, 3, 31))


def test_purchase_summary_and_supplier_breakdown() -> None:
    assert get_purchase_summary(MARCH).total == Decimal("2835.00")
    assert get_purchases_by_supplier(MARCH)[0].key == "SUP-001"


def test_purchase_price_history_and_pending_partial_order() -> None:
    prices = get_purchase_price_history(
        "P-104", Period(date(2025, 1, 1), date(2025, 4, 30))
    )
    pending = get_pending_purchase_orders(MARCH)

    assert [(item.period_start, item.average_unit_cost) for item in prices] == [
        (date(2025, 1, 1), Decimal("20.00")),
        (date(2025, 2, 1), Decimal("20.00")),
        (date(2025, 3, 1), Decimal("28.00")),
        (date(2025, 4, 1), Decimal("28.00")),
    ]
    assert [(item.order_key, item.outstanding_quantity) for item in pending] == [
        ("PO-02-P-104", Decimal("25"))
    ]


def test_supplier_delay_and_inbound_relationship_are_reproducible() -> None:
    performance = get_supplier_delivery_performance(
        Period(date(2025, 2, 1), date(2025, 2, 28))
    )
    inbound = get_product_inbound_supply("P-104", MARCH)
    finding = investigate_product_supply("P-104", MARCH, FEBRUARY)

    assert any(
        item.supplier_key == "SUP-002" and item.late_order_count == 1
        for item in performance
    )
    assert [(item.order_key, item.outstanding_quantity) for item in inbound] == [
        ("PO-02-P-104", Decimal("25"))
    ]
    assert finding.sales_change == Decimal("-1040.00")
    assert finding.stockout_observed is True
    assert finding.relationship_type == "observed_timing_relationship"
