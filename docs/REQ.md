# ERP AI Analyst — Requirements Baseline

**Scope:** single mandatory MVP. The MVP is not complete until all six domains below are implemented and evaluated.

## 1. Mandatory MVP domains

1. Sales
2. Customers
3. Inventory
4. Purchases / Procurement
5. Payroll Analytics — aggregated operational-financial scope only
6. Accounting Lite — bounded analytical accounting scope only

Accounts Receivable, real ERP adapters, BIZAG Reference Adapter and MCP remain post-MVP.

## 2. Functional requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR-001 | Accept natural-language ERP business questions. | API tests. |
| FR-002 | Extract intent, period, entities and restrictions with structured output. | Schema + tests. |
| FR-003 | Build/adapt bounded multi-step analysis plans. | LangGraph traces. |
| FR-004 | Invoke only registered typed tools. | Registry + negative tests. |
| FR-005 | Validate tool arguments before execution. | Contract tests. |
| FR-006 | Execute calculations in deterministic domain services. | Unit/integration tests against ground truth. |
| FR-007 | Combine results across mandatory MVP domains. | Cross-domain evaluation cases. |
| FR-008 | Preserve deterministic figures during synthesis. | Quantitative claim checks. |
| FR-009 | Link important quantitative findings to evidence. | Evidence contract tests. |
| FR-010 | Produce structured data for tables/charts. | Response schema tests. |
| FR-011 | Recognize insufficient data and unsupported questions. | Negative cases. |
| FR-012 | Handle tool failures/timeouts with bounded retries. | Fault-injection tests. |
| FR-013 | Maintain request/execution ID end-to-end. | API/log/trace assertions. |
| FR-014 | Run reproducibly with a synthetic ERP only. | Fresh setup + seed + demo. |
| FR-015 | Distinguish facts, inferences, correlations and warnings. | Evaluation. |
| FR-016 | Support conversational context only when functionally justified. | Explicit follow-up cases. |
| FR-017 | Analyze purchases, suppliers, pending/partial orders, receipts, cost evolution and delivery performance. | Purchases tests/evals. |
| FR-018 | Analyze payroll totals, period variance, concepts, overtime and cost centers only at aggregated analytical level. | Payroll tests/evals. |
| FR-019 | Analyze Accounting Lite period summaries, revenue, costs, expenses, gross margin, operating result, account/group variance and cost centers. | Accounting tests/evals. |
| FR-020 | Support purchases → inventory → sales cross-domain analysis. | Signature scenario. |
| FR-021 | Support payroll → operating expenses / accounting variance analysis. | Signature scenario. |
| FR-022 | Support purchase-cost → gross-margin analysis without asserting unsupported causality. | Cross-domain evaluation. |

## 3. Domain requirements

### Sales
Totals, comparisons, trends, customer/product/salesperson breakdowns and contribution to variance.

### Customers
Purchase history, concentration, reduction/abandonment and contribution to change.

### Inventory
Stock, movements, stockouts, stockout duration, rotation/overstock/risk only through documented deterministic rules.

### Purchases
Purchases by period/supplier/product; purchase price evolution; pending/partial purchase orders; receipts; lead time/delivery delays; inbound supply; supplier delivery performance.

### Payroll Analytics
Total payroll cost; period comparison; cost by cost center; cost by concept; overtime trend; fixed/variable/other aggregated components; contribution to operating-expense variation. No contracts, vacations, performance, individual-sensitive decisioning or PeopleOps workflows.

### Accounting Lite
Period summaries; revenue/costs/expenses; gross margin; operating result; aggregate balances by account/group; period variance; cost-center expenses. No journal-entry creation, automated close, full reconciliation, tax/statutory interpretation or write operations.

## 4. Mandatory cross-domain scenarios

1. Sales decline → products/customers → stockout inspection.
2. Supplier delay → delayed PO/receipt → stockout → sales decline.
3. Purchase-cost increase → gross-margin deterioration/variance.
4. Payroll overtime/cost increase → operating-expense increase → Accounting Lite period variance.
5. Negative/insufficient-evidence cases that prevent false causal claims.

## 5. Non-functional requirements

- NFR-001 Read-only analytics.
- NFR-002 No LLM-generated free-form SQL execution.
- NFR-003 Reproducible local environment with Docker Compose.
- NFR-004 Environment-based configuration and `.env.example`; no secrets committed.
- NFR-005 Unit, contract, integration, agentic and evaluation tests.
- NFR-006 LangSmith tracing configurable by environment.
- NFR-007 Structured logging with request ID.
- NFR-008 Controlled timeouts, retries, result limits and graph iteration limits.
- NFR-009 Synthetic/public-safe data only.
- NFR-010 ERP-agnostic architecture above repository/integration boundary.
- NFR-011 Safe error handling.
- NFR-012 Documented lint/format/type-check quality gates.

## 6. Explicitly post-MVP

- real ERP adapters;
- BIZAG Reference Adapter;
- MCP client/server and adapter ecosystem;
- complete Accounts Receivable;
- write operations;
- arbitrary NL-to-SQL;
- full BI product;
- RAG/pgvector without a justified use case.
