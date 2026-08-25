"""Controlled, deterministic Sales analytics."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import text

from app.db.connection import create_database_engine
from app.domain.common import Period, Provenance


@dataclass(frozen=True)
class SalesSummary:
    period: Period
    total: Decimal
    line_count: int
    provenance: Provenance


@dataclass(frozen=True)
class SalesDocumentCount:
    period: Period
    document_count: int


@dataclass(frozen=True)
class TopSalesProduct:
    period: Period
    product_key: str | None
    product_name: str | None
    total: Decimal
    quantity: Decimal


@dataclass(frozen=True)
class SalesBreakdown:
    key: str
    name: str
    total: Decimal
    quantity: Decimal
    contribution: Decimal


@dataclass(frozen=True)
class PeriodComparison:
    current: SalesSummary
    previous: SalesSummary
    absolute_change: Decimal
    percentage_change: Decimal | None


def get_sales_summary(period: Period) -> SalesSummary:
    query = text("""SELECT COALESCE(SUM(sdl.quantity * sdl.unit_price * (1 - sdl.discount)), 0) AS total, COUNT(*) AS line_count
        FROM sales_document sd JOIN sales_document_line sdl ON sdl.sales_document_id = sd.id
        WHERE sd.status = 'posted' AND sd.document_date BETWEEN :start AND :end""")
    with create_database_engine().connect() as connection:
        row = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).one()
    return SalesSummary(
        period,
        Decimal(row.total),
        int(row.line_count),
        Provenance("sales.summary.v1", period.start, period.end, int(row.line_count)),
    )


def get_sales_document_count(period: Period) -> SalesDocumentCount:
    query = text("""SELECT COUNT(*) AS document_count FROM sales_document
        WHERE status = 'posted' AND document_date BETWEEN :start AND :end""")
    with create_database_engine().connect() as connection:
        row = connection.execute(query, {"start": period.start, "end": period.end}).one()
    return SalesDocumentCount(period, int(row.document_count))


def compare_sales_periods(current: Period, previous: Period) -> PeriodComparison:
    current_result = get_sales_summary(current)
    previous_result = get_sales_summary(previous)
    change = current_result.total - previous_result.total
    percentage = (
        None
        if previous_result.total == 0
        else (change / previous_result.total * 100).quantize(Decimal("0.01"))
    )
    return PeriodComparison(current_result, previous_result, change, percentage)


def _breakdown(period: Period, dimension: str) -> list[SalesBreakdown]:
    columns = {
        "customer": (
            "c.business_key",
            "c.name",
            "sdl.quantity * sdl.unit_price * (1 - sdl.discount)",
        ),
        "product": (
            "p.business_key",
            "p.name",
            "sdl.quantity * sdl.unit_price * (1 - sdl.discount)",
        ),
        "salesperson": (
            "sp.business_key",
            "sp.name",
            "sdl.quantity * sdl.unit_price * (1 - sdl.discount)",
        ),
    }
    if dimension not in columns:
        raise ValueError(f"unsupported sales breakdown: {dimension}")
    key, name, amount = columns[dimension]
    joins = {
        "customer": "JOIN customer c ON c.id = sd.customer_id",
        "product": "JOIN product p ON p.id = sdl.product_id",
        "salesperson": "JOIN salesperson sp ON sp.id = sd.salesperson_id",
    }[dimension]
    query = text(f"""SELECT {key} AS business_key, {name} AS name, SUM({amount}) AS total, SUM(sdl.quantity) AS quantity
        FROM sales_document sd JOIN sales_document_line sdl ON sdl.sales_document_id = sd.id {joins}
        WHERE sd.status = 'posted' AND sd.document_date BETWEEN :start AND :end
        GROUP BY {key}, {name} ORDER BY total DESC, business_key""")
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).all()
    total = sum((Decimal(row.total) for row in rows), Decimal("0"))
    return [
        SalesBreakdown(
            str(row.business_key),
            str(row.name),
            Decimal(row.total),
            Decimal(row.quantity),
            (Decimal(row.total) / total * 100).quantize(Decimal("0.01"))
            if total
            else Decimal("0"),
        )
        for row in rows
    ]


def get_sales_by_customer(period: Period) -> list[SalesBreakdown]:
    return _breakdown(period, "customer")


def get_sales_by_product(period: Period) -> list[SalesBreakdown]:
    return _breakdown(period, "product")


def get_top_sales_product(period: Period) -> TopSalesProduct:
    items = get_sales_by_product(period)
    if not items:
        return TopSalesProduct(period, None, None, Decimal("0"), Decimal("0"))
    item = items[0]
    return TopSalesProduct(period, item.key, item.name, item.total, item.quantity)


def get_sales_by_salesperson(period: Period) -> list[SalesBreakdown]:
    return _breakdown(period, "salesperson")
