# ADR-0004 — Single MVP scope includes six ERP domains

**Status:** Accepted

## Decision
The portfolio MVP requires Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite. Implementation remains slice-based, but Purchases, Payroll and Accounting Lite are not post-MVP enhancements.

Payroll is restricted to aggregated operational-financial analytics. Accounting Lite is restricted to pre-structured analytical balances/aggregates and excludes write operations, tax/statutory interpretation, automated close and full reconciliation.

## Consequences
MVP Definition of Done and evaluation must include cross-domain scenarios spanning purchases→inventory→sales, purchase cost→margin, and payroll→operating expenses/accounting variance. Post-MVP evolution begins with real ERP adapters, including a possible BIZAG Reference Adapter, and MCP exploration.
