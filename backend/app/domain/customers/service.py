"""Deterministic customer purchase analytics."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import text

from app.db.connection import create_database_engine
from app.domain.common import Period


@dataclass(frozen=True)
class CustomerPurchase:
    customer_key: str
    customer_name: str
    total: Decimal
    quantity: Decimal


@dataclass(frozen=True)
class CustomerDecline:
    customer_key: str
    customer_name: str
    current_total: Decimal
    previous_total: Decimal
    absolute_change: Decimal
    percentage_change: Decimal | None


def get_customer_purchase_history(
    customer_key: str, period: Period
) -> CustomerPurchase:
    query = text("""SELECT c.business_key, c.name, COALESCE(SUM(sdl.quantity * sdl.unit_price * (1 - sdl.discount)), 0) AS total, COALESCE(SUM(sdl.quantity), 0) AS quantity
        FROM customer c LEFT JOIN sales_document sd ON sd.customer_id = c.id AND sd.status = 'posted' AND sd.document_date BETWEEN :start AND :end
        LEFT JOIN sales_document_line sdl ON sdl.sales_document_id = sd.id WHERE c.business_key = :customer_key GROUP BY c.business_key, c.name""")
    with create_database_engine().connect() as connection:
        row = connection.execute(
            query,
            {"customer_key": customer_key, "start": period.start, "end": period.end},
        ).one_or_none()
    if row is None:
        raise ValueError(f"unknown customer: {customer_key}")
    return CustomerPurchase(
        str(row.business_key), str(row.name), Decimal(row.total), Decimal(row.quantity)
    )


def find_customers_with_sales_decline(
    current: Period,
    previous: Period,
    minimum_absolute_change: Decimal = Decimal("0.01"),
) -> list[CustomerDecline]:
    query = text("""WITH period_totals AS (SELECT c.business_key, c.name,
        COALESCE(SUM(CASE WHEN sd.document_date BETWEEN :current_start AND :current_end THEN sdl.quantity * sdl.unit_price * (1 - sdl.discount) ELSE 0 END), 0) AS current_total,
        COALESCE(SUM(CASE WHEN sd.document_date BETWEEN :previous_start AND :previous_end THEN sdl.quantity * sdl.unit_price * (1 - sdl.discount) ELSE 0 END), 0) AS previous_total
        FROM customer c LEFT JOIN sales_document sd ON sd.customer_id = c.id AND sd.status = 'posted'
        LEFT JOIN sales_document_line sdl ON sdl.sales_document_id = sd.id GROUP BY c.business_key, c.name)
        SELECT * FROM period_totals WHERE current_total - previous_total <= -:minimum_change ORDER BY current_total - previous_total, business_key""")
    params = {
        "current_start": current.start,
        "current_end": current.end,
        "previous_start": previous.start,
        "previous_end": previous.end,
        "minimum_change": minimum_absolute_change,
    }
    with create_database_engine().connect() as connection:
        rows = connection.execute(query, params).all()
    result: list[CustomerDecline] = []
    for row in rows:
        current_total, previous_total = (
            Decimal(row.current_total),
            Decimal(row.previous_total),
        )
        change = current_total - previous_total
        percentage = (
            None
            if previous_total == 0
            else (change / previous_total * 100).quantize(Decimal("0.01"))
        )
        result.append(
            CustomerDecline(
                str(row.business_key),
                str(row.name),
                current_total,
                previous_total,
                change,
                percentage,
            )
        )
    return result
