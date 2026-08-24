# Slice 2 — Commercial Analytics

## 1. Objective
Deliver a deterministic commercial analytics layer across Sales, Customers and Inventory capable of explaining observed sales variation using reproducible calculations before any LLM is introduced.

## 2. Dependencies
Slices 0–1 accepted; canonical schema, seeded synthetic ERP and ground truth are available.

## 3. Scope
### Sales
- sales totals by period;
- period comparison and trends;
- breakdowns by customer, product and salesperson;
- contribution to variance.

### Customers
- purchase history;
- sales concentration;
- customers with meaningful purchase decline/abandonment using documented deterministic rules;
- contribution to period change.

### Inventory
- stock history/balance;
- stockout periods and duration;
- deterministic stock-risk/rotation/overstock calculations only where explicitly specified;
- relationship between product availability and observed sales periods.

### Commercial cross-domain analysis
Provide deterministic service composition supporting the analytical chain:
`sales decline → product/customer contribution → inventory availability/stockout inspection`.

## 4. Out of scope
- Purchases functionality beyond existing seeded data.
- Payroll/Accounting analytics.
- Typed LLM tools.
- LangGraph/OpenAI.
- Natural-language synthesis or causal claims.
- Frontend.

## 5. Files and components affected
- `backend/app/domain/sales/`
- `backend/app/domain/customers/`
- `backend/app/domain/inventory/`
- controlled repository implementations required by these services
- related schemas/results/evidence primitives as deterministic metadata only
- unit and integration tests

## 6. Data / contracts
Service contracts must expose typed deterministic inputs/outputs with period/entity filters and provenance sufficient for later tool evidence.

Expected service capabilities include equivalents of:
- `get_sales_summary`
- `compare_sales_periods`
- `get_sales_by_customer`
- `get_sales_by_product`
- `get_customer_purchase_history`
- `find_customers_with_sales_decline`
- `get_stock_history`
- `get_out_of_stock_periods`
- `find_stockout_products`

Names may be refined, but semantics must remain documented and stable before Slice 5.

## 7. Implementation rules
- All calculations are deterministic and testable without an LLM.
- Queries remain controlled/parameterized.
- Variance/contribution formulas must be explicit and documented.
- Stock-risk/rotation rules must not be hidden inside prompts.
- Correlation between stockout and sales decline is reported as an observed relationship only.

## 8. Synthetic scenarios
Must correctly resolve:
- S1 sales decline with mixed product/customer contribution;
- S2 stockout overlap;
- S3 customer-driven decline without stockout;
- S7 stable/growth controls.

## 9. Required tests
- Unit tests for each calculation.
- Repository integration tests against seeded PostgreSQL.
- Ground-truth assertions for S1–S3/S7.
- Boundary periods and empty/no-data cases.
- Result-ordering/ranking and numeric precision tests.
- Tests demonstrating no stockout is falsely assigned to S3.

## 10. Acceptance criteria
1. Signature commercial analysis can be reproduced without LLM involvement.
2. Sales/customer/inventory figures match ground truth.
3. Mixed explanations remain distinct.
4. Stockout coincidence never becomes unsupported causal certainty.
5. Typed deterministic service outputs are stable and covered by tests.

## 11. Validation commands
Run targeted commercial unit/integration tests plus full project tests, lint/format and type checks.

## 12. Deliverables
A deterministic Commercial Analytics capability suitable for direct demonstration and later exposure through typed tools.

## 13. Definition of Done
The seeded signature sales-decline scenario can be investigated end-to-end through domain services with correct, reproducible figures and provenance.

## 14. Prohibitions
Do not introduce OpenAI/LangGraph or natural-language interpretation. Do not implement later financial/supply-chain domains prematurely.
