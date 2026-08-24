"""Read-only aggregate accounting calculations."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import text

from app.db.connection import create_database_engine
from app.domain.common import Period


@dataclass(frozen=True)
class AccountingSummary:
    period: Period
    revenue: Decimal
    costs: Decimal
    expenses: Decimal
    gross_margin: Decimal
    operating_result: Decimal


@dataclass(frozen=True)
class AccountingComparison:
    current: AccountingSummary
    previous: AccountingSummary
    operating_result_change: Decimal


@dataclass(frozen=True)
class AccountingBreakdown:
    key: str
    name: str
    amount: Decimal


def get_accounting_period_summary(period: Period) -> AccountingSummary:
    query = text("""SELECT COALESCE(SUM(amount) FILTER (WHERE account_group = 'revenue'), 0) AS revenue,
        COALESCE(SUM(amount) FILTER (WHERE account_group = 'cost'), 0) AS costs,
        COALESCE(SUM(amount) FILTER (WHERE account_group = 'expense'), 0) AS expenses
        FROM account_balance ab JOIN accounting_period ap ON ap.id = ab.accounting_period_id
        WHERE ap.period_start BETWEEN :start AND :end""")
    with create_database_engine().connect() as connection:
        row = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).one()
    revenue, costs, expenses = (
        Decimal(row.revenue),
        Decimal(row.costs),
        Decimal(row.expenses),
    )
    gross_margin = revenue + costs
    return AccountingSummary(
        period, revenue, costs, expenses, gross_margin, gross_margin + expenses
    )


def compare_accounting_periods(
    current: Period, previous: Period
) -> AccountingComparison:
    current_result = get_accounting_period_summary(current)
    previous_result = get_accounting_period_summary(previous)
    return AccountingComparison(
        current_result,
        previous_result,
        current_result.operating_result - previous_result.operating_result,
    )


def get_expense_variance_by_group(
    current: Period, previous: Period
) -> list[AccountingBreakdown]:
    query = text("""SELECT ab.account_code, ab.account_name,
        COALESCE(SUM(ab.amount) FILTER (WHERE ap.period_start BETWEEN :current_start AND :current_end), 0) AS current_amount,
        COALESCE(SUM(ab.amount) FILTER (WHERE ap.period_start BETWEEN :previous_start AND :previous_end), 0) AS previous_amount
        FROM account_balance ab JOIN accounting_period ap ON ap.id = ab.accounting_period_id
        WHERE ab.account_group = 'expense' AND (ap.period_start BETWEEN :current_start AND :current_end OR ap.period_start BETWEEN :previous_start AND :previous_end)
        GROUP BY ab.account_code, ab.account_name ORDER BY ABS(SUM(ab.amount)) DESC, ab.account_code""")
    params = {
        "current_start": current.start,
        "current_end": current.end,
        "previous_start": previous.start,
        "previous_end": previous.end,
    }
    with create_database_engine().connect() as connection:
        rows = connection.execute(query, params).all()
    return [
        AccountingBreakdown(
            str(row.account_code),
            str(row.account_name),
            Decimal(row.current_amount) - Decimal(row.previous_amount),
        )
        for row in rows
    ]


def get_cost_center_expenses(period: Period) -> list[AccountingBreakdown]:
    query = text("""SELECT COALESCE(cc.business_key, 'UNASSIGNED') AS business_key,
        COALESCE(cc.name, 'Unassigned') AS name, SUM(ab.amount) AS amount
        FROM account_balance ab JOIN accounting_period ap ON ap.id = ab.accounting_period_id
        LEFT JOIN cost_center cc ON cc.id = ab.cost_center_id
        WHERE ab.account_group = 'expense' AND ap.period_start BETWEEN :start AND :end
        GROUP BY cc.business_key, cc.name ORDER BY amount, business_key""")
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).all()
    return [
        AccountingBreakdown(str(row.business_key), str(row.name), Decimal(row.amount))
        for row in rows
    ]


def get_gross_margin_summary(period: Period) -> Decimal:
    return get_accounting_period_summary(period).gross_margin
