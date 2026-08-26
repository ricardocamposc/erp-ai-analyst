# Intent and capability matrix

The matrix is the contract between natural language, deterministic tools, and
responses. `Implemented` means that a query and a test exist; `Partial` means
that some data exists but a dimension or dedicated response is missing;
`Pending` means that the response must not be invented.

| ID | Intent | Level | Main tool | Status |
|---|---|---|---|---|
| SALES-TOTAL | total sales for the period | O | `get_sales_summary` | Implemented |
| SALES-DOC-COUNT | issued sales documents | O | `get_sales_document_count` | Implemented |
| SALES-TOP-PRODUCT | top-selling product | O/G | `get_top_sales_product` | Implemented |
| SALES-VARIANCE | observed variance and explanation | G | `compare_sales_periods`, breakdowns | Implemented |
| SALES-BY-DIMENSION | sales by customer/product/salesperson | O/G | breakdown tools | Implemented |
| CUSTOMER-HISTORY | customer history | O/G | `get_customer_purchase_history` | Implemented |
| INVENTORY-STOCK | stock and history | O | `get_stock_history` | Implemented |
| INVENTORY-STOCKOUT | stockouts and observable risk | O/G | stockout tools | Implemented |
| INVENTORY-MINIMUM | minimum-stock method | O | `get_erp_concept` | Implemented (conceptual) |
| PURCHASE-TOTAL | purchase amount | O | `get_purchase_summary` | Implemented |
| PURCHASE-ORDER-COUNT | purchase order count | O | `get_purchase_order_count` | Implemented |
| PURCHASE-BY-DIMENSION | purchases by supplier/product | O/G | purchase breakdown tools | Implemented |
| PURCHASE-BY-AREA | orders by area/cost center | O/G | — | Pending: the schema does not relate POs to areas |
| PURCHASE-DELIVERY | delays and receiving | G | delivery/inbound tools | Implemented |
| PAYROLL-EMPLOYEE-COUNT | aggregated payroll employees | O | `get_payroll_cost_summary` | Implemented |
| PAYROLL-COST | payroll cost | O/G | payroll summary/comparison | Implemented |
| PAYROLL-BREAKDOWN | payroll by component/center | O/G | payroll breakdown tools | Implemented |
| ACCOUNTING-SUMMARY | revenue, costs, expenses, and result | O | accounting summary | Implemented |
| ACCOUNTING-VARIANCE | result trend | G | accounting comparison | Implemented |
| ACCOUNTING-COST-OF-SALES | conceptual definition and calculation | O | `get_erp_concept` | Implemented (conceptual) |
| ERP-CONCEPT | explanation of ERP concepts | O | `get_erp_concept` | Implemented |
| STRATEGIC-RECOMMENDATION | strategic recommendation | E | evidence tools + LLM | Partial: requires sufficient data and does not prove causality |
| INVOICE-COUNT | issued tax invoices | O | — | Pending: the model only has `sales_document` |

## Coverage rules

- A quantitative response must include the tool used and its period.
- A conceptual question must not execute a fictitious query or invent company
  figures.
- An invoice question must not be answered as a sales-document question until
  an entity or explicit policy establishes that equivalence.
- Orders by area or cost center will not be implemented until the data model
  has a verifiable relationship.
- Strategic questions must distinguish facts, observations, and
  recommendations; they must not claim causality without experimental
  evidence.
