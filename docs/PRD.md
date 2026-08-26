# Project 02 — ERP AI Analyst
## Product Requirements Document (PRD)

**Status:** Implemented baseline and active evolution
**Portfolio role:** Flagship project
**Conceptual product:** Agentic Enterprise Analytics for ERP
**Version:** 2.0

## 1. Product Vision

ERP AI Analyst is an agentic business-analysis platform built on a **Canonical ERP Data Model**. It accepts natural-language questions and runs controlled workflows that discover metadata, generate candidate SQL, validate it semantically and through PostgreSQL, execute it read-only, combine ERP domains, and produce traceable conclusions.

The public application will be reproducible with a fictional ERP and synthetic data. The architecture will be ready to integrate real ERPs through a decoupled layer and, potentially, MCP.

## 2. Objectives

1. Demonstrate Agentic AI applied to ERP systems.
2. Solve multi-step and multi-area analysis.
3. Separate LLM reasoning from deterministic calculation.
4. Provide evidence for figures and conclusions.
5. Evaluate the system against ground truth.
6. Keep the agentic layer independent of the ERP's proprietary schema.
7. Incrementally add domains with real business value without turning the project into a complete ERP or BI system.

## 3. Users

- management/executives;
- sales;
- inventory;
- purchasing;
- finance;
- payroll for aggregate analysis;
- controllers/accounting for Accounting Lite;
- business analysts;
- non-technical ERP users.

## 4. Principles

- ERP-agnostic.
- Read-only.
- The LLM may generate candidate SQL only inside the Slice 10 workflow. It is never free-form execution: AST parsing, metadata allowlists, PostgreSQL validation, limits, timeout, read-only permissions and auditing are mandatory.
- The LLM reasons; code calculates.
- Do not create one agent per module.
- Evidence before assertion.
- Synthetic data in the public repository.
- Correlation will not be presented as causation.
- Real extensions must not delay MVP Core.

## 5. Scope layers

### 5.1 MVP — mandatory for the first public version

**Sales + Customers + Inventory + Purchases + Payroll Analytics + Accounting Lite**

It must support the flagship question:

> “Why did sales decline this month?”

and related multi-step analysis.

### 5.2 Internal MVP sequence

**Purchases + Payroll Analytics** will be implemented after Sales + Customers + Inventory are stabilized, but remain mandatory parts of the same MVP.

### 5.3 Accounting Lite — mandatory and controlled MVP scope

Accounting is limited to analysis of:

- revenue;
- costs;
- expenses;
- operating result;
- gross margin;
- aggregated balances by account/group;
- period variances;
- cost centers.

It does not include:

- journal-entry generation/modification;
- automated close;
- full reconciliation;
- taxes;
- tax interpretation;
- full statutory accounting.

### 5.4 Later extensions

- full Accounts Receivable;
- other modules;
- real ERP adapters;
- BIZAG Reference Adapter;
- MCP Integration Server.

## 6. Cross-cutting functional requirements

- **RF-01:** accept business questions in natural language.
- **RF-02:** structure intent, period, entities, and constraints.
- **RF-03:** build/adapt a multi-step plan.
- **RF-04:** select only authorized tools.
- **RF-05:** validate arguments through typed schemas.
- **RF-06:** perform calculations through deterministic domain services.
- **RF-07:** combine results from multiple domains.
- **RF-08:** synthesize findings without changing figures.
- **RF-09:** associate evidence with quantitative findings.
- **RF-10:** produce structured data for tables/charts.
- **RF-11:** recognize insufficient data.
- **RF-12:** handle tool failures, timeouts, and limited retries.
- **RF-13:** preserve request/execution ID.
- **RF-14:** support a reproducible demo without a real ERP.
- **RF-15:** distinguish facts, inferences, and warnings.
- **RF-16:** support conversational context only when functionally necessary.

## 7. Domain requirements

### Sales
- sales by period;
- comparison;
- trend;
- customer;
- product;
- salesperson;
- contribution to variances.

### Customers
- history;
- concentration;
- purchase reduction/churn;
- contribution to changes.

### Inventory
- stock;
- movements;
- stockout;
- turnover;
- overstock;
- stockout risk.

### Purchases
- purchases by period;
- purchases by supplier/product;
- cost trends;
- pending/partial orders;
- receipts;
- lead time/delays;
- purchases–inventory relationship.

### Payroll Analytics
- total payroll cost;
- period variance;
- cost by cost center/area;
- aggregate payroll concepts;
- overtime;
- fixed/variable components;
- payroll contribution to operating expenses.

Payroll in this project will not cover contracts, leave, policies, performance, or sensitive individual decisions; that boundary belongs to PeopleOps AI.

### Accounting Lite
- aggregated balances by period;
- revenue/costs/expenses;
- gross margin;
- operating result;
- variances;
- cost centers.

## 8. Functional acceptance questions

The product suite must include, among others:

- “Why did sales decline this month?”
- “Does the decline in P-104 coincide with a stock shortage?”
- “Which products at risk of stockout have pending purchase orders?”
- “Which suppliers have the longest delays?”
- “How did the purchase cost of P-104 evolve?”
- “What was the total payroll cost, and which concepts explain the change?”
- “Which cost centers explain the increase in payroll?”
- “How much of the increase in operating expenses is attributable to payroll?”
- “Which expense groups explain the change in operating result?”
- “Does the increase in purchase cost coincide with deterioration in gross margin?”

## 9. Canonical ERP model

Conceptual model:

```text
Customer
Product
Salesperson
SalesDocument
SalesDocumentLine
InventoryMovement
StockBalance
Supplier
PurchaseOrder
PurchaseOrderLine
GoodsReceipt
EmployeePayrollSummary
PayrollConcept
CostCenter
AccountingPeriod
AccountBalance
```

Only entities required by the active phase will be implemented.

## 10. Fictional ERP and synthetic business scenario

The fictional ERP will be the official source for development, tests, demo, and evaluation.

The data must contain deliberate patterns and cross-domain relationships.

Ejemplo:

```text
Supplier delay
→ Purchase order delayed
→ Stockout
→ Sales decline
```

Ejemplo financiero:

```text
Payroll overtime increase
→ Payroll cost increase
→ Operating expenses increase
→ Accounting Lite period variance
```

Known scenarios will form the ground truth.

## 11. Implemented architecture

```text
User
 ↓
FastAPI / Conversation Layer
 ↓
Intent + Context
 ↓
Planner / Orchestrator — LangGraph
 ↓
Dynamic Agentic Query Workflow
 ├─ Metadata discovery
 ├─ Analyst agent
 ├─ Validator agent
 ├─ Deterministic guardrails
 ├─ PostgreSQL validation/execution
 └─ Synthesis
 ↓
Canonical PostgreSQL
 ↓
Deterministic Results
 ↓
Evidence / State
 ↓
Synthesis
 ↓
Structured Answer
 ↓
LangSmith + Logs
```

## 12. Agent vs. Tool

### Agentic / LLM
- interpretation;
- planning;
- routing;
- tool selection;
- decision to perform additional analysis;
- synthesis;
- explanation.

### Deterministic
- SQL/access control;
- aggregations;
- variances;
- rankings;
- stockouts;
- lead times;
- aging;
- payroll totals;
- account balances;
- margins;
- persistence.

## 13. Tools disponibles

### Core
```text
get_sales_summary(...)
compare_sales_periods(...)
get_sales_by_customer(...)
get_sales_by_product(...)
get_customer_purchase_history(...)
find_customers_with_sales_decline(...)
get_stock_history(...)
get_out_of_stock_periods(...)
find_stockout_products(...)
```

### Purchases
```text
get_purchase_summary(...)
get_purchases_by_supplier(...)
get_purchase_price_history(...)
get_pending_purchase_orders(...)
get_supplier_delivery_performance(...)
get_product_inbound_supply(...)
```

### Payroll
```text
get_payroll_cost_summary(...)
compare_payroll_periods(...)
get_payroll_cost_by_cost_center(...)
get_payroll_cost_by_concept(...)
get_overtime_cost_trend(...)
```

### Accounting Lite
```text
get_accounting_period_summary(...)
compare_accounting_periods(...)
get_expense_variance_by_group(...)
get_cost_center_expenses(...)
get_gross_margin_summary(...)
```

The original domain tools remain available for compatibility and regression. The primary Slice 10 tools expose metadata discovery, available periods, allowed metrics/dimensions, data classification, query validation, query explanation and read-only execution. They are reusable capabilities rather than one tool per question.

## 14. Structured response

It must separate:

- answer;
- key findings;
- evidence;
- analysis performed;
- warnings/limitations.

Every important figure must be linked to tool results.

## 15. LangGraph

It must demonstrate:

- state;
- conditional routing;
- tool execution;
- multi-step workflow;
- result-based iteration;
- iteration limits;
- error handling;
- controlled retries.

It will not be a wrapper around a single model call.

## 16. OpenAI

Explicitly used for:

- tool calling;
- structured outputs;
- intent;
- planning;
- synthesis;
- controlled generation;
- assisted evaluation when appropriate.

It will not be used for reproducible calculations.

## 17. LangSmith and observability

Record/inspect:

- input;
- plan;
- routing;
- tool calls;
- arguments;
- results;
- errors;
- latency;
- model calls;
- final answer.

## 18. Evaluation

ERP Analysis Evaluation Dataset:

```text
question
expected_intent
expected_tools
expected_key_facts
expected_calculations
expected_answer_characteristics
difficulty
category
```

Candidate metrics:

- tool selection accuracy;
- calculation correctness;
- key fact coverage;
- unsupported quantitative claim rate;
- unnecessary tool-call rate;
- successful workflow rate;
- latency;
- token/cost metrics.

There must be negative cases and tool failures.

## 19. Security

- read-only;
- typed tools;
- controlled/parameterized queries;
- no unvalidated or destructive SQL; Slice 10 permits candidate SQL generated by the LLM under deterministic guardrails;
- environment-managed secrets;
- result limits;
- timeouts;
- secure logs;
- public synthetic data.

Payroll must be treated as a sensitive domain even in synthetic demos; a future real connection will require specific authorization controls.

## 20. Real ERP integration

Outside MVP Core, but an extensibility requirement:

```text
ERP
 ↓
Integration / Adapter Layer
 ↓
Canonical ERP Contract
 ↓
ERP AI Analyst
```

The first recommended strategy will be a **Replicated / Analytical Store** with an initial load, data quality checks, and incremental synchronization.

## 21. Configurable mappings

An integration must map source ERP entities to the canonical model without introducing proprietary names into the agentic layer.

The specific format will be decided later.

## 22. BIZAG Reference Adapter

BIZAG may be the first reference adapter after the MVP, without publishing:

- proprietary schema;
- customer data;
- private code;
- credentials;
- sensitive configurations.

## 23. MCP

Possible evolution:

```text
ERP AI Analyst — MCP Client
        ↓
ERP Integration MCP Server
        ├─ BIZAG Adapter
        ├─ SAP Adapter
        ├─ Dynamics Adapter
        └─ Other Adapter
```

It is not part of the MVP and is not currently a sixth official project.

## 24. Non-functional requirements

- security;
- reproducibility;
- testability;
- observability;
- environment-based configuration;
- resilience;
- extensibility;
- documentation;
- Docker;
- production orientation without claiming production readiness.

## 25. Testing

- unit tests for domain services/calculations;
- tool contract tests;
- integration tests;
- agentic routing/tool-selection tests;
- evaluation regression suite.

## 26. UX

Minimal interface:

- question;
- response;
- key findings;
- table/chart when appropriate;
- evidence;
- analysis performed;
- warnings.

It will not be a complete BI platform.

## 27. Acceptance criteria — MVP Core

1. Runnable demo without a real ERP.
2. Sales + Customers + Inventory implementados.
3. Canonical model.
4. Deterministic tools.
5. No unvalidated free-form SQL in MVP Core. Slice 10 permits candidate SQL generated by the LLM under deterministic guardrails.
6. Workflow LangGraph multi-step.
7. Multi-area flagship question.
8. Ground truth and correct calculations.
9. Evidence.
10. LangSmith.
11. Evaluation suite.
12. Tests.
13. Minimal FastAPI/UX.
14. Docker y `.env.example`.
15. Exclusively synthetic data.

## 28. Acceptance criteria — MVP+

### Purchases
- at least one purchases → inventory → sales scenario;
- order, supplier, and cost tools;
- cross-domain evaluation.

### Payroll
- aggregate costs;
- variances;
- concepts;
- cost centers;
- at least one payroll → operating expenses scenario;
- without entering PeopleOps scope.

### Accounting Lite
- summary by period;
- revenue/costs/expenses;
- gross margin;
- variances;
- cost centers;
- no accounting writes or close automation.

## 29. Roadmap

### Phase 0 — Design
PDD/PRD, fictional company, canonical model, scenarios, tools, LangGraph, and evaluation design.

### Phase 1 — Synthetic ERP Core
Sales + Customers + Inventory data, services, and tests.

### Phase 2 — Core Tools
Typed and deterministic tools.

### Phase 3 — Agentic Core
LangGraph + OpenAI.

### Phase 4 — Evaluation & Observability
LangSmith, dataset, metrics, and regression.

### Phase 5 — API/UX
FastAPI, frontend, evidence, and visualizations.

### Phase 6 — Portfolio Release
Docker, README, ADRs, screenshots, demo, and results.

### Phase 7 — Purchases
Model, data, tools, and cross-domain scenario.

### Phase 8 — Payroll Analytics
Aggregate model, tools, security, and financial scenario.

### Phase 9 — Accounting Lite
Balances/aggregates, margin, expenses, and cost centers.

### Phase 10 — ERP Integration
Contract, analytical store, mappings, and possible BIZAG adapter.

### Phase 11 — Agentic Dynamic Query Execution — implemented
Metadata discovery, candidate SQL generated by agents, validator agent, deterministic guardrails, read-only execution, auditing, and local provider.

### Phase 12 — MCP Exploration
MCP Client/Server and adapters implementing the Slice 10 contracts.

## 30. Portfolio Definition of Done

The public local MVP includes Sales, Customers, Inventory, Purchases, Payroll Analytics, Accounting Lite and the implemented Slice 10 dynamic workflow. Real ERP adapters, the BIZAG Reference Adapter, full receivables and MCP come after the local provider.

## 31. Decisions pending before implementation

1. fictional company and industry;
2. period, currency, and units;
3. Core scenarios;
4. Purchases scenarios;
5. Payroll scenarios;
6. minimum Accounting Lite scenario;
7. canonical physical model;
8. Core tool catalog and schemas;
9. future Purchases/Payroll/Accounting schemas;
10. LangGraph design;
11. state;
12. evidence format;
13. evaluation dataset;
14. metrics;
15. UX;
16. physical/repository architecture;
17. sensitive-data policy for future real integration.

## 32. Boundary with PeopleOps AI

Payroll appears in both projects with different objectives.

**ERP AI Analyst:** payroll as an operational-financial dimension of the ERP: costs, concepts, cost centers, variances, and relationship to results.

**PeopleOps AI:** HR domain: employees, contracts, attendance, leave, policies, documents, and sensitive workflows with Human-in-the-loop.

This boundary must remain explicit to avoid duplication.

## 33. Final scope statement

The product will evolve in layers:

> **MVP:** Agentic ERP Analytics sobre Sales + Customers + Inventory + Purchases + Payroll Analytics + Accounting Lite.

> Purchases, Payroll, and Accounting Lite were implemented incrementally within the MVP. Slice 10 adds the current local dynamic-query architecture; real ERP adapters and MCP come later.

The architecture will remain ERP-agnostic and ready for real integrations, but adapters and MCP must not delay the project's primary evidence.
