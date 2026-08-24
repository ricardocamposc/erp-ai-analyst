# ERP AI Analyst — Evaluation Baseline v1.0

Total cases: 36
Distribution: 18 single-domain, 10 cross-domain, 6 guardrail, 2 resilience.

## Metrics
- tool_selection_accuracy: 0.8056
- calculation_correctness: 0.9444
- key_fact_coverage: 0.6181
- unsupported_quantitative_claim_rate: 0.0
- unnecessary_tool_call_rate: 0.2222
- successful_workflow_rate: 0.7222
- guardrail_success_rate: 0.0
- cross_domain_success_rate: 0.6

## Operational
- Average latency: 179.979 ms
- Model calls: 0
- Tool calls: 86
- Token usage: not available in offline deterministic mode
- Estimated cost: not available in offline deterministic mode

## Failures and regressions
- `EVAL-SALES-001`: {"id": "EVAL-SALES-001", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.25, "unnecessary_tools": []}
- `EVAL-SALES-002`: {"id": "EVAL-SALES-002", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.5, "unnecessary_tools": []}
- `EVAL-CUSTOMERS-002`: {"id": "EVAL-CUSTOMERS-002", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.5, "unnecessary_tools": []}
- `EVAL-CUSTOMERS-003`: {"id": "EVAL-CUSTOMERS-003", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.5, "unnecessary_tools": []}
- `EVAL-INVENTORY-002`: {"id": "EVAL-INVENTORY-002", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.5, "unnecessary_tools": []}
- `EVAL-PURCHASES-002`: {"id": "EVAL-PURCHASES-002", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.25, "unnecessary_tools": []}
- `EVAL-PURCHASES-003`: {"id": "EVAL-PURCHASES-003", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.75, "unnecessary_tools": []}
- `EVAL-PAYROLL-002`: {"id": "EVAL-PAYROLL-002", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.0, "unnecessary_tools": []}
- `EVAL-PAYROLL-003`: {"id": "EVAL-PAYROLL-003", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.0, "unnecessary_tools": []}
- `EVAL-ACCOUNTING-001`: {"id": "EVAL-ACCOUNTING-001", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.3333, "unnecessary_tools": []}
- `EVAL-ACCOUNTING-002`: {"id": "EVAL-ACCOUNTING-002", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.0, "unnecessary_tools": []}
- `EVAL-ACCOUNTING-003`: {"id": "EVAL-ACCOUNTING-003", "category": "single_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.0, "unnecessary_tools": []}
- `EVAL-CROSS-001`: {"id": "EVAL-CROSS-001", "category": "cross_domain", "status_match": true, "tool_selection_match": false, "key_fact_coverage": 0.5, "unnecessary_tools": ["get_stock_history"]}
- `EVAL-CROSS-005`: {"id": "EVAL-CROSS-005", "category": "cross_domain", "status_match": true, "tool_selection_match": false, "key_fact_coverage": 0.0, "unnecessary_tools": ["compare_accounting_periods"]}
- `EVAL-CROSS-006`: {"id": "EVAL-CROSS-006", "category": "cross_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.6667, "unnecessary_tools": []}
- `EVAL-CROSS-007`: {"id": "EVAL-CROSS-007", "category": "cross_domain", "status_match": true, "tool_selection_match": true, "key_fact_coverage": 0.5, "unnecessary_tools": []}
- `EVAL-CROSS-008`: {"id": "EVAL-CROSS-008", "category": "cross_domain", "status_match": true, "tool_selection_match": false, "key_fact_coverage": 0.5, "unnecessary_tools": ["get_pending_purchase_orders"]}
- `EVAL-CROSS-010`: {"id": "EVAL-CROSS-010", "category": "cross_domain", "status_match": true, "tool_selection_match": false, "key_fact_coverage": 0.5, "unnecessary_tools": []}
- `EVAL-GUARD-001`: {"id": "EVAL-GUARD-001", "category": "guardrail", "status_match": false, "tool_selection_match": false, "key_fact_coverage": 1.0, "unnecessary_tools": ["compare_sales_periods", "find_stockout_products", "get_sales_by_customer", "get_sales_by_product"]}
- `EVAL-GUARD-002`: {"id": "EVAL-GUARD-002", "category": "guardrail", "status_match": false, "tool_selection_match": false, "key_fact_coverage": 1.0, "unnecessary_tools": ["compare_sales_periods", "find_stockout_products", "get_sales_by_customer", "get_sales_by_product"]}
- `EVAL-GUARD-003`: {"id": "EVAL-GUARD-003", "category": "guardrail", "status_match": false, "tool_selection_match": true, "key_fact_coverage": 1.0, "unnecessary_tools": ["compare_sales_periods", "find_stockout_products", "get_sales_by_customer", "get_sales_by_product"]}
- `EVAL-GUARD-004`: {"id": "EVAL-GUARD-004", "category": "guardrail", "status_match": true, "tool_selection_match": false, "key_fact_coverage": 0.0, "unnecessary_tools": ["get_stock_history"]}
- `EVAL-GUARD-005`: {"id": "EVAL-GUARD-005", "category": "guardrail", "status_match": false, "tool_selection_match": true, "key_fact_coverage": 1.0, "unnecessary_tools": ["compare_sales_periods", "find_stockout_products", "get_sales_by_customer", "get_sales_by_product"]}
- `EVAL-GUARD-006`: {"id": "EVAL-GUARD-006", "category": "guardrail", "status_match": false, "tool_selection_match": true, "key_fact_coverage": 0.0, "unnecessary_tools": []}

## Method
The run uses RuleBasedGateway, typed tools, and the PostgreSQL database from backend/.env. It performs no OpenAI calls and no writes.
