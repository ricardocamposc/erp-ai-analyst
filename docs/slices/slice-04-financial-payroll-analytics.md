# Slice 4 — Financial & Payroll Analytics

## 1. Objective
Deliver bounded deterministic Payroll Analytics and Accounting Lite and connect them through business scenarios that explain operating-expense, margin and period-result variation without turning the project into PeopleOps or a full accounting system.

## 2. Dependencies
Slices 0–3 accepted.

## 3. Scope
### Payroll Analytics
- total payroll cost;
- period comparison;
- payroll cost by cost center;
- payroll cost by concept;
- overtime-cost trend;
- fixed/variable/other aggregated components;
- contribution of payroll variation to operating expenses.

### Accounting Lite
- period summary;
- revenue, costs and expenses;
- gross margin;
- operating result;
- aggregate balance/variance by account or account group;
- cost-center expenses;
- period comparisons.

### Cross-domain finance
- payroll cost increase → operating-expense/accounting period variance;
- purchase-cost increase → gross-margin variance using deterministic results from Purchases plus Accounting Lite.

## 4. Out of scope
- Contracts, vacations, performance, disciplinary/HR decisions or individual-sensitive PeopleOps analytics.
- Journal-entry creation/modification.
- Automated close, full reconciliation, tax/statutory/legal advice.
- Free-form accounting interpretation by an LLM.
- Accounts Receivable expansion.

## 5. Files and components affected
- `backend/app/domain/payroll/`
- `backend/app/domain/accounting/`
- related repositories/schemas
- cross-domain financial composition where appropriate
- unit/integration tests

## 6. Data / contracts
Payroll capabilities should cover equivalents of:
- `get_payroll_cost_summary`
- `compare_payroll_periods`
- `get_payroll_cost_by_cost_center`
- `get_payroll_cost_by_concept`
- `get_overtime_cost_trend`

Accounting Lite capabilities should cover equivalents of:
- `get_accounting_period_summary`
- `compare_accounting_periods`
- `get_expense_variance_by_group`
- `get_cost_center_expenses`
- `get_gross_margin_summary`

Outputs must preserve period, account/group, cost-center/concept and contributing metric provenance for later evidence.

## 7. Implementation rules
- Payroll remains aggregate operational-financial analytics.
- Accounting remains read-only and aggregate analytical accounting.
- Define margin and operating-result formulas explicitly.
- Do not duplicate Purchases calculations when correlating purchase cost with margin.
- All quantitative results must be reproducible without model calls.

## 8. Synthetic scenarios
- S5 purchase-price increase → gross-margin variance.
- S6 payroll overtime/cost increase → operating-expense/accounting variance.
- S7 stable/growth controls.
- S8 requests beyond payroll/accounting boundaries must be rejectable later by the agentic layer; deterministic services should not expose forbidden operations.

## 9. Required tests
- Payroll totals, period comparisons, concepts, cost centers and overtime.
- Accounting period summaries, revenue/cost/expense, gross margin, operating result and variance.
- Ground-truth assertions for S5 and S6.
- Precision/rounding and empty-period cases.
- Boundary tests ensuring no write operations or sensitive PeopleOps services exist.

## 10. Acceptance criteria
1. Payroll and Accounting Lite figures match ground truth.
2. S5 and S6 are reproducibly explained through deterministic service composition.
3. Payroll and accounting boundaries are enforceable in the available service surface.
4. No journal/write or sensitive PeopleOps behavior exists.

## 11. Validation commands
Run payroll/accounting/cross-domain unit and integration tests plus the full quality suite.

## 12. Deliverables
A deterministic Financial & Payroll Analytics capability covering the bounded MVP scope and cross-domain financial scenarios.

## 13. Definition of Done
All six MVP domains now have deterministic analytical capabilities with passing ground-truth tests and explicit scope boundaries.

## 14. Prohibitions
Do not expand to full accounting, Accounts Receivable, tax interpretation, PeopleOps workflows or write operations.
