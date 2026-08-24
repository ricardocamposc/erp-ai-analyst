"""Bounded payroll/accounting cross-domain composition."""

from dataclasses import dataclass
from decimal import Decimal

from app.domain.accounting.service import (
    AccountingComparison,
    compare_accounting_periods,
)
from app.domain.common import Period
from app.domain.payroll.service import PayrollComparison, compare_payroll_periods


@dataclass(frozen=True)
class FinancialInvestigation:
    payroll: PayrollComparison
    accounting: AccountingComparison
    overtime_contribution: Decimal
    relationship_type: str


def investigate_payroll_expense(
    current: Period, previous: Period
) -> FinancialInvestigation:
    payroll = compare_payroll_periods(current, previous)
    accounting = compare_accounting_periods(current, previous)
    overtime_contribution = payroll.current.total_cost - payroll.previous.total_cost
    return FinancialInvestigation(
        payroll,
        accounting,
        overtime_contribution,
        "observed_operating_expense_contribution",
    )
