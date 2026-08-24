# Slice 3 — Supply Chain Analytics

## 1. Objective
Add deterministic Purchases/Procurement analytics and connect it to existing Inventory and Sales capabilities so the system can investigate supplier and inbound-supply factors behind product availability and commercial performance.

## 2. Dependencies
Slices 0–2 accepted.

## 3. Scope
### Purchases
- purchases by period, supplier and product;
- purchase-price history/evolution;
- pending and partially fulfilled purchase orders;
- goods-receipt status;
- lead-time and delivery-delay calculations;
- supplier delivery performance;
- product inbound supply.

### Cross-domain supply chain
Compose deterministic analysis for:
- supplier → purchase order → receipt;
- pending/delayed inbound supply → inventory availability;
- inventory availability → observed sales period relationships;
- products at stock risk with pending inbound supply.

## 4. Out of scope
- Payroll/Accounting services except seeded data dependencies.
- Agentic planning or causal inference.
- Real supplier/ERP integrations.
- Typed LLM tools and UI.

## 5. Files and components affected
- `backend/app/domain/purchases/`
- repositories and schemas for supplier/PO/receipt analysis
- extensions to cross-domain service/composition layer as architecturally appropriate
- tests for Purchases and cross-domain supply chain analysis

## 6. Data / contracts
Deterministic capabilities should cover equivalents of:
- `get_purchase_summary`
- `get_purchases_by_supplier`
- `get_purchase_price_history`
- `get_pending_purchase_orders`
- `get_supplier_delivery_performance`
- `get_product_inbound_supply`

Cross-domain outputs must retain contributing supplier/product/order/receipt/period identifiers for later evidence.

## 7. Implementation rules
- Define lead-time and late-delivery semantics explicitly.
- Pending/partial order logic must be deterministic and status/quantity based.
- Reuse Inventory/Sales services instead of duplicating their calculations.
- Report relationships and timing; do not claim supplier delay caused sales decline unless the dataset provides sufficient explicit evidence and the product contract permits that wording.

## 8. Synthetic scenarios
Primary scenario S4:
`Supplier delay → delayed PO/receipt → stockout → sales decline`.

Also validate S7 controls so suppliers/products with stable performance are not falsely flagged.

## 9. Required tests
- Purchase totals and supplier/product breakdowns.
- Purchase-price history.
- PO pending/partial fulfillment.
- Receipt timing and lead-time calculations.
- Supplier-performance ranking.
- Inbound-supply queries.
- Ground-truth test for S4 across purchases, inventory and sales.
- Negative/control tests for non-delayed suppliers/products.

## 10. Acceptance criteria
1. Purchases domain figures match ground truth.
2. The complete S4 relationship can be reconstructed deterministically.
3. Cross-domain services reuse existing domain logic.
4. No unsupported causal language is encoded in deterministic outputs.

## 11. Validation commands
Run targeted purchases/supply-chain unit and integration tests plus the full quality suite.

## 12. Deliverables
A deterministic Supply Chain Analytics capability that links procurement performance to inbound supply, inventory and observed sales outcomes.

## 13. Definition of Done
Known delayed-supplier and control scenarios are reproducibly distinguished with correct PO/receipt, inventory and sales evidence.

## 14. Prohibitions
Do not add ERP adapters, external supplier APIs, LLM planning or duplicate commercial calculations.
