"""Cross-domain deterministic supply-chain investigation."""

from dataclasses import dataclass
from decimal import Decimal

from app.domain.common import Period
from app.domain.inventory.service import get_out_of_stock_periods
from app.domain.purchases.service import InboundSupply, get_product_inbound_supply
from app.domain.sales.service import get_sales_by_product


@dataclass(frozen=True)
class SupplyChainFinding:
    product_key: str
    sales_change: Decimal
    stockout_observed: bool
    inbound_supply: list[InboundSupply]
    relationship_type: str


def investigate_product_supply(
    product_key: str, current: Period, previous: Period
) -> SupplyChainFinding:
    current_sales = {item.key: item.total for item in get_sales_by_product(current)}
    previous_sales = {item.key: item.total for item in get_sales_by_product(previous)}
    stockout = any(
        item.product_key == product_key
        for item in get_out_of_stock_periods(current, product_key)
    )
    return SupplyChainFinding(
        product_key,
        current_sales.get(product_key, Decimal("0"))
        - previous_sales.get(product_key, Decimal("0")),
        stockout,
        get_product_inbound_supply(product_key, current),
        "observed_timing_relationship",
    )
