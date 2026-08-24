"""Deterministic composition for the commercial signature investigation."""

from dataclasses import dataclass
from decimal import Decimal

from app.domain.common import Period
from app.domain.customers.service import (
    CustomerDecline,
    find_customers_with_sales_decline,
)
from app.domain.inventory.service import find_stockout_products
from app.domain.sales.service import (
    PeriodComparison,
    compare_sales_periods,
    get_sales_by_product,
)


@dataclass(frozen=True)
class CommercialInvestigation:
    comparison: PeriodComparison
    product_changes: dict[str, Decimal]
    customer_declines: list[CustomerDecline]
    stockout_products: list[str]
    relationship_type: str


def investigate_sales_decline(
    current: Period, previous: Period
) -> CommercialInvestigation:
    comparison = compare_sales_periods(current, previous)
    current_products = {item.key: item.total for item in get_sales_by_product(current)}
    previous_products = {
        item.key: item.total for item in get_sales_by_product(previous)
    }
    product_changes = {
        key: current_products.get(key, Decimal("0"))
        - previous_products.get(key, Decimal("0"))
        for key in sorted(set(current_products) | set(previous_products))
    }
    return CommercialInvestigation(
        comparison=comparison,
        product_changes=product_changes,
        customer_declines=find_customers_with_sales_decline(current, previous),
        stockout_products=find_stockout_products(current),
        relationship_type="observed_correlation_only",
    )
