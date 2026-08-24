"""Controlled deterministic procurement analytics."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import text

from app.db.connection import create_database_engine
from app.domain.common import Period


@dataclass(frozen=True)
class PurchaseSummary:
    period: Period
    total: Decimal
    order_count: int


@dataclass(frozen=True)
class PurchaseBreakdown:
    key: str
    name: str
    total: Decimal
    quantity: Decimal


@dataclass(frozen=True)
class PurchasePricePoint:
    product_key: str
    period_start: date
    average_unit_cost: Decimal


@dataclass(frozen=True)
class PendingPurchaseOrder:
    order_key: str
    supplier_key: str
    product_key: str
    status: str
    ordered_quantity: Decimal
    received_quantity: Decimal
    outstanding_quantity: Decimal
    expected_date: date


@dataclass(frozen=True)
class SupplierDeliveryPerformance:
    supplier_key: str
    order_count: int
    late_order_count: int
    average_delay_days: Decimal


@dataclass(frozen=True)
class InboundSupply:
    product_key: str
    order_key: str
    supplier_key: str
    outstanding_quantity: Decimal
    expected_date: date
    status: str


def get_purchase_summary(period: Period) -> PurchaseSummary:
    query = text("""SELECT COALESCE(SUM(pol.ordered_quantity * pol.unit_cost), 0) AS total,
        COUNT(DISTINCT po.id) AS order_count FROM purchase_order po
        JOIN purchase_order_line pol ON pol.purchase_order_id = po.id
        WHERE po.order_date BETWEEN :start AND :end AND po.status <> 'cancelled'""")
    with create_database_engine().connect() as connection:
        row = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).one()
    return PurchaseSummary(period, Decimal(row.total), int(row.order_count))


def _breakdown(period: Period, dimension: str) -> list[PurchaseBreakdown]:
    selected = {
        "supplier": ("s.business_key", "s.name"),
        "product": ("p.business_key", "p.name"),
    }
    if dimension not in selected:
        raise ValueError(f"unsupported purchase breakdown: {dimension}")
    key, name = selected[dimension]
    join = (
        "JOIN supplier s ON s.id = po.supplier_id"
        if dimension == "supplier"
        else "JOIN product p ON p.id = pol.product_id"
    )
    query = text(f"""SELECT {key} AS business_key, {name} AS name,
        SUM(pol.ordered_quantity * pol.unit_cost) AS total, SUM(pol.ordered_quantity) AS quantity
        FROM purchase_order po JOIN purchase_order_line pol ON pol.purchase_order_id = po.id {join}
        WHERE po.order_date BETWEEN :start AND :end AND po.status <> 'cancelled'
        GROUP BY {key}, {name} ORDER BY total DESC, business_key""")
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).all()
    return [
        PurchaseBreakdown(
            str(row.business_key),
            str(row.name),
            Decimal(row.total),
            Decimal(row.quantity),
        )
        for row in rows
    ]


def get_purchases_by_supplier(period: Period) -> list[PurchaseBreakdown]:
    return _breakdown(period, "supplier")


def get_purchases_by_product(period: Period) -> list[PurchaseBreakdown]:
    return _breakdown(period, "product")


def get_purchase_price_history(
    product_key: str, period: Period
) -> list[PurchasePricePoint]:
    query = text("""SELECT date_trunc('month', po.order_date)::date AS period_start,
        AVG(pol.unit_cost) AS average_unit_cost FROM purchase_order po
        JOIN purchase_order_line pol ON pol.purchase_order_id = po.id JOIN product p ON p.id = pol.product_id
        WHERE p.business_key = :product_key AND po.order_date BETWEEN :start AND :end
        GROUP BY period_start ORDER BY period_start""")
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query,
            {"product_key": product_key, "start": period.start, "end": period.end},
        ).all()
    return [
        PurchasePricePoint(
            product_key,
            row.period_start,
            Decimal(row.average_unit_cost).quantize(Decimal("0.01")),
        )
        for row in rows
    ]


def get_pending_purchase_orders(period: Period) -> list[PendingPurchaseOrder]:
    query = text("""SELECT po.business_key AS order_key, s.business_key AS supplier_key,
        p.business_key AS product_key, po.status, pol.ordered_quantity,
        COALESCE(SUM(grl.received_quantity), 0) AS received_quantity, po.expected_date
        FROM purchase_order po JOIN supplier s ON s.id = po.supplier_id
        JOIN purchase_order_line pol ON pol.purchase_order_id = po.id JOIN product p ON p.id = pol.product_id
        LEFT JOIN goods_receipt_line grl ON grl.purchase_order_line_id = pol.id
        WHERE po.expected_date BETWEEN :start AND :end AND po.status IN ('open', 'partial')
        GROUP BY po.business_key, s.business_key, p.business_key, po.status, pol.ordered_quantity, po.expected_date
        ORDER BY po.expected_date, po.business_key""")
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).all()
    return [
        PendingPurchaseOrder(
            str(row.order_key),
            str(row.supplier_key),
            str(row.product_key),
            str(row.status),
            Decimal(row.ordered_quantity),
            Decimal(row.received_quantity),
            Decimal(row.ordered_quantity - row.received_quantity),
            row.expected_date,
        )
        for row in rows
    ]


def get_supplier_delivery_performance(
    period: Period,
) -> list[SupplierDeliveryPerformance]:
    query = text("""SELECT s.business_key AS supplier_key, COUNT(DISTINCT po.id) AS order_count,
        COUNT(DISTINCT po.id) FILTER (WHERE gr.receipt_date > po.expected_date) AS late_order_count,
        COALESCE(AVG(GREATEST((gr.receipt_date - po.expected_date), 0)), 0) AS average_delay_days
        FROM purchase_order po JOIN supplier s ON s.id = po.supplier_id
        LEFT JOIN goods_receipt gr ON gr.purchase_order_id = po.id
        WHERE po.order_date BETWEEN :start AND :end AND po.status <> 'cancelled'
        GROUP BY s.business_key ORDER BY late_order_count DESC, average_delay_days DESC, supplier_key""")
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).all()
    return [
        SupplierDeliveryPerformance(
            str(row.supplier_key),
            int(row.order_count),
            int(row.late_order_count),
            Decimal(row.average_delay_days),
        )
        for row in rows
    ]


def get_product_inbound_supply(product_key: str, period: Period) -> list[InboundSupply]:
    pending = get_pending_purchase_orders(period)
    return [
        InboundSupply(
            item.product_key,
            item.order_key,
            item.supplier_key,
            item.outstanding_quantity,
            item.expected_date,
            item.status,
        )
        for item in pending
        if item.product_key == product_key
    ]
