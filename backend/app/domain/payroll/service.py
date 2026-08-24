"""Read-only, aggregate payroll analytics; no employee-level behavior."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import text

from app.db.connection import create_database_engine
from app.domain.common import Period


@dataclass(frozen=True)
class PayrollSummary:
    period: Period
    total_cost: Decimal
    employee_count: int


@dataclass(frozen=True)
class PayrollBreakdown:
    key: str
    name: str
    amount: Decimal


@dataclass(frozen=True)
class PayrollComparison:
    current: PayrollSummary
    previous: PayrollSummary
    absolute_change: Decimal


@dataclass(frozen=True)
class OvertimePoint:
    period_start: date
    amount: Decimal


def get_payroll_cost_summary(period: Period) -> PayrollSummary:
    query = text("""SELECT COALESCE(SUM(total_cost), 0) AS total_cost,
        COALESCE(SUM(employee_count), 0) AS employee_count FROM employee_payroll_summary
        WHERE period_start BETWEEN :start AND :end""")
    with create_database_engine().connect() as connection:
        row = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).one()
    return PayrollSummary(period, Decimal(row.total_cost), int(row.employee_count))


def compare_payroll_periods(current: Period, previous: Period) -> PayrollComparison:
    current_result = get_payroll_cost_summary(current)
    previous_result = get_payroll_cost_summary(previous)
    return PayrollComparison(
        current_result,
        previous_result,
        current_result.total_cost - previous_result.total_cost,
    )


def get_payroll_cost_by_cost_center(period: Period) -> list[PayrollBreakdown]:
    query = text("""SELECT cc.business_key, cc.name, SUM(eps.total_cost) AS amount
        FROM employee_payroll_summary eps JOIN cost_center cc ON cc.id = eps.cost_center_id
        WHERE eps.period_start BETWEEN :start AND :end GROUP BY cc.business_key, cc.name
        ORDER BY amount DESC, cc.business_key""")
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).all()
    return [
        PayrollBreakdown(str(row.business_key), str(row.name), Decimal(row.amount))
        for row in rows
    ]


def get_payroll_cost_by_concept(period: Period) -> list[PayrollBreakdown]:
    query = text("""SELECT pc.business_key, pc.name, SUM(psl.amount) AS amount
        FROM payroll_summary_line psl JOIN payroll_concept pc ON pc.id = psl.payroll_concept_id
        JOIN employee_payroll_summary eps ON eps.id = psl.payroll_summary_id
        WHERE eps.period_start BETWEEN :start AND :end GROUP BY pc.business_key, pc.name
        ORDER BY amount DESC, pc.business_key""")
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).all()
    return [
        PayrollBreakdown(str(row.business_key), str(row.name), Decimal(row.amount))
        for row in rows
    ]


def get_overtime_cost_trend(period: Period) -> list[OvertimePoint]:
    query = text("""SELECT eps.period_start, SUM(psl.amount) AS amount
        FROM payroll_summary_line psl JOIN payroll_concept pc ON pc.id = psl.payroll_concept_id
        JOIN employee_payroll_summary eps ON eps.id = psl.payroll_summary_id
        WHERE pc.component_type = 'overtime' AND eps.period_start BETWEEN :start AND :end
        GROUP BY eps.period_start ORDER BY eps.period_start""")
    with create_database_engine().connect() as connection:
        rows = connection.execute(
            query, {"start": period.start, "end": period.end}
        ).all()
    return [OvertimePoint(row.period_start, Decimal(row.amount)) for row in rows]
