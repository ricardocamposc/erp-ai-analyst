# ERP AI Analyst — Data Design

## 1. Goal
Create one deterministic synthetic Canonical ERP dataset for the complete MVP: Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite. Data must encode deliberate cross-domain business stories rather than random noise.

## 2. Mandatory MVP canonical entities
- Customer
- Product
- Salesperson
- SalesDocument
- SalesDocumentLine
- InventoryMovement
- StockBalance
- Supplier
- PurchaseOrder
- PurchaseOrderLine
- GoodsReceipt
- GoodsReceiptLine (physical helper when needed)
- EmployeePayrollSummary (synthetic and aggregated analytical use)
- PayrollConcept
- PayrollSummaryLine (or equivalent fact structure)
- CostCenter
- AccountingPeriod
- AccountBalance

Accounts Receivable entities are reserved for post-MVP unless a minimal non-product dependency is strictly required.

## 3. Physical model principles
- stable business keys plus internal IDs;
- explicit currency, timezone, units and period semantics;
- parameterized/controlled repository queries;
- no schema names from proprietary ERPs;
- accounting works from pre-structured balances/aggregates, not journal automation;
- payroll data supports aggregate financial analysis, not sensitive people decisions.

## 4. Required relationships
Sales lines reference products/customers; inventory movements/snapshots reference products; PO lines reference suppliers/products; receipts reference POs/products; payroll summaries reference periods/concepts/cost centers; account balances reference accounting periods/account groups/accounts and optionally cost centers.

## 5. Mandatory synthetic scenarios

### S1 — Sales decline + mixed explanation
A target month declines versus comparison month. A small set of products/customers explains the variance.

### S2 — Stockout coincidence
At least one declining product has a stockout overlapping the period. Language must remain correlation-aware.

### S3 — Customer-driven decline control
A major customer reduces purchases without stockout so the system cannot explain every decline via inventory.

### S4 — Supplier delay → PO/receipt → stockout → sales decline
A known supplier delay produces delayed inbound supply and a stockout overlapping a sales decline.

### S5 — Purchase price increase → gross-margin variance
At least one important product has increased purchase cost reflected coherently in Accounting Lite cost/margin aggregates.

### S6 — Payroll overtime → operating-expense variance
Overtime or another payroll component increases payroll cost for known cost centers and contributes to an operating-expense increase represented in Accounting Lite.

### S7 — Stable/growth controls
Include products/customers/suppliers/cost centers that remain stable or improve.

### S8 — Insufficient evidence
Questions requiring unsupported causality, tax advice, write actions, sensitive PeopleOps analysis or absent domains must be rejected/limited.

## 6. Ground truth
Keep independently reviewable artifacts under `data/ground_truth/` such as `scenarios.yaml`, `expected_metrics.yaml`, `expected_cross_domain.yaml`, and `README.md`. Expected values must not be computed by calling the same production service being tested.

## 7. Deterministic generation
Use fixed seed, stable keys, baseline activity, explicit scenario injection and validation. Data-quality checks must cover uniqueness, FK integrity, valid quantities/statuses, sales arithmetic, PO/receipt consistency, stock consistency, payroll aggregate consistency, accounting equation/period invariants appropriate to Accounting Lite, and period coverage.

## 8. Evidence
Every quantitative service/tool result must expose provenance: tool, arguments, period, metric, value, contributing business keys, repository/query identifier and row-count/sample references when useful. This is application evidence, not chain-of-thought.
