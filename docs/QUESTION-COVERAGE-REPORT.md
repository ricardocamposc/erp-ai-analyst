# Conversational coverage report

## What was validated

The previous Agentic v2 suite validated 36 frozen questions and their
repetitions. This expansion adds a catalog of 300 questions (50 for each of
the six areas), a capability matrix, and an explicit suite for simple and
conceptual questions.

The checks executed in this expansion were:

- 58 automated backend tests: all passing.
- Ruff: no errors.
- Mypy: no errors.
- Tools against the synthetic database: payroll, sales documents, top product,
  purchase orders, and ERP concepts.
- Real OpenAI + LangGraph workflow for five new questions.

## End-to-end evidence

| Question | Observed result | Tool |
|---|---|---|
| How many employees are on payroll? | 33 employees | `get_payroll_cost_summary` |
| How many purchase orders were issued? | 4 non-cancelled orders | `get_purchase_order_count` |
| Which product has the highest sales? | Premium Filter | `get_top_sales_product` |
| How is cost of sales calculated? | Opening inventory + net purchases - closing inventory | `get_erp_concept` |
| How is minimum stock determined? | Demand during lead time + safety stock | `get_erp_concept` |

## Gaps that remain intentional

1. **Tax invoices:** the schema only contains `sales_document` with `posted`
   and `cancelled` statuses; it has no tax-invoice entity, series, folio, taxes,
   or document type. The application may count posted sales documents, but it
   must not call them invoices without a data-model decision.
2. **Orders by area or cost center:** `purchase_order` has no relationship to
   `cost_center` or `area`. No fictitious grouping was implemented. The data
   model and synthetic data must be extended first.
3. **Strategic questions:** the catalog defines them, but a recommendation is
   valid only when sufficient facts, comparable periods, and relevant
   dimensions exist. The model must separate evidence, observation, and
   recommendation without claiming causality.
4. **Advanced ERP metrics:** turnover, coverage, numeric safety stock,
   product margin, and per-employee unit cost require new measures or
   additional data; conceptual explanations are available.

## Correct interpretation

Coverage is not demonstrated by the number of registered tools. It is
demonstrated by acceptance questions covering each intent, arguments, response,
period, evidence, and behavior when data is missing. The catalog and matrix are
now the basis for expanding Agentic v2 evaluation without confusing a closed
evaluation with full product coverage.
