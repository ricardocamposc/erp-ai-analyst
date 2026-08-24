"""Deterministic stock history and stockout analytics."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import text

from app.db.connection import create_database_engine
from app.domain.common import Period


@dataclass(frozen=True)
class StockPoint:
    product_key: str
    balance_date: date
    quantity: Decimal


@dataclass(frozen=True)
class StockoutPeriod:
    product_key: str
    start: date
    end: date
    duration_days: int


def get_stock_history(product_key: str, period: Period) -> list[StockPoint]:
    query = text("""SELECT p.business_key, sb.balance_date, sb.quantity FROM stock_balance sb JOIN product p ON p.id = sb.product_id
        WHERE p.business_key = :product_key AND sb.balance_date BETWEEN :start AND :end ORDER BY sb.balance_date""")
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query,
            {"product_key": product_key, "start": period.start, "end": period.end},
        ).all()
    return [
        StockPoint(str(row.business_key), row.balance_date, Decimal(row.quantity))
        for row in rows
    ]


def get_out_of_stock_periods(
    period: Period, product_key: str | None = None
) -> list[StockoutPeriod]:
    product_filter = " AND p.business_key = :product_key" if product_key else ""
    query = text(
        f"""SELECT p.business_key, sb.balance_date FROM stock_balance sb JOIN product p ON p.id = sb.product_id
        WHERE sb.quantity = 0 AND sb.balance_date BETWEEN :start AND :end{product_filter}
        ORDER BY p.business_key, sb.balance_date"""
    )
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query,
            {"start": period.start, "end": period.end, "product_key": product_key},
        ).all()
    return [
        StockoutPeriod(
            str(row.business_key),
            row.balance_date,
            period.end,
            (period.end - row.balance_date).days + 1,
        )
        for row in rows
    ]


def find_stockout_products(period: Period) -> list[str]:
    return sorted({item.product_key for item in get_out_of_stock_periods(period)})
