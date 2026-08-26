# Project 02 — ERP AI Analyst
## Project Definition Document (PDD)

**Status:** Implemented baseline and active evolution
**Portfolio role:** Flagship project
**Conceptual product:** Agentic Enterprise Analytics for ERP
**Document:** Project definition
**Version:** 2.0

## Purpose

ERP AI Analyst is the flagship project in the portfolio. It connects ERP systems expertise with modern Agentic AI architectures and demonstrates how a business-intelligence layer can operate on structured data without coupling to the proprietary schema of a specific ERP.

The system allows users to query and analyze business information using natural language. It interprets the question, discovers the available ERP model, generates a candidate analytical query, validates it semantically and against PostgreSQL, executes it through read-only controls, combines results from multiple areas, and produces explainable conclusions with evidence.

The public application will run on a **fictional ERP with synthetic data and known ground truth**, while its architecture will be designed to evolve toward real ERPs through a **Canonical ERP Data Model** and a decoupled integration layer.

## Professional capability demonstrated

**Design of Enterprise Agentic AI Systems integrated with ERP systems and focused on multi-area business analysis.**

It must provide evidence of:

- AI Solutions Architecture;
- Agentic AI applied to enterprise systems;
- LangGraph y LangSmith;
- OpenAI tool calling y structured outputs;
- ERP-agnostic architecture;
- Canonical ERP Data Model;
- deterministic tools and domain services;
- multi-step and multi-area analysis;
- legacy-system integration and modernization;
- evaluation and ground truth;
- traceability and observability;
- read-only security;
- production-oriented design.

## Purpose of the product

It converts ERP operational data into actionable business analysis without requiring users to know tables, SQL, reports, or the system's internal navigation.

It must not be limited to answering simple queries. It must be able to:

- understand business questions;
- determine what information it needs;
- plan multi-step analysis;
- select tools;
- query multiple areas;
- combine results;
- calculate metrics reproducibly;
- detect relevant factors;
- distinguish facts from inferences;
- explain findings;
- show evidence;
- produce tables or charts when they add value;
- recognize when data is insufficient.

## Functional domains

The product is designed around independent but combinable ERP domains.

### Analytical core
- Sales;
- Customers;
- Inventory.

### High-value expansion
- Procurement / Purchases;
- Payroll Analytics.

### Controlled financial scope
- Accounting Lite.

Adding new domains does not imply creating one agent per module. Domains are exposed primarily through **tools and deterministic services** reusable by the agentic workflow.

## What types of questions does it answer?

### Sales

- “Why did sales decline this month?”
- “Which customers account for most of the decline?”
- “Which salespeople are below their historical average?”
- “Which products grew the most compared with the previous month?”
- “What is the sales trend over the last 12 months?”
- “Which products explain this quarter's growth?”

### Customers

- “Which customers stopped buying recently?”
- “Which customers reduced their purchases the most?”
- “Which customers account for most sales?”
- “How did customer C-014's purchasing behavior change?”

Metrics such as customer profitability will be offered only when sufficient cost data exists to calculate them correctly.

### Inventory

- “Which products are at risk of stockout?”
- “Which products were out of stock this month?”
- “How many days was product P-104 out of stock?”
- “Which products are overstocked?”
- “Which items have low turnover?”
- “Which inventory is tying up the most capital?”

### Purchases / Procurement

- “How much did we purchase this month, and how does it compare with the previous month?”
- “Which suppliers account for most purchases?”
- “Which products had the largest increase in purchase cost?”
- “Which purchase orders remain pending or partially fulfilled?”
- “Which suppliers have the longest delivery delays?”
- “Which products at risk of stockout have pending orders?”
- “How did P-104's average purchase price evolve?”
- “Which suppliers provide products critical to sales?”

### Payroll Analytics

Payroll's scope in ERP AI Analyst will be **operational-financial and aggregate**, not a replacement for PeopleOps AI.

- “What was the total payroll cost this month?”
- “How does it compare with the previous month?”
- “Which payroll concepts explain the change in payroll cost?”
- “Which cost centers explain the largest increase?”
- “How did overtime cost evolve?”
- “What proportion corresponds to fixed compensation, variable compensation, and other concepts?”
- “Which areas explain most of the month-over-month change?”

ERP AI Analyst will avoid sensitive analysis of individual performance, HR policies, contracts, leave, or decisions about people. Those capabilities belong to **PeopleOps AI**.

### Accounting — Accounting Lite

Accounting is included with a deliberately small scope. The goal is not to build a complete accounting copilot.

Planned questions:

- “What is the summary of revenue, costs, and expenses for the period?”
- “How did operating income evolve compared with the previous month?”
- “Which expense groups explain the largest change?”
- “How are expenses distributed by cost center?”
- “Which accounts show the largest period-over-period changes?”
- “How did gross margin evolve?”

Accounting Lite will operate on **pre-structured accounting balances and aggregates**. Journal-entry generation, tax interpretation, automated accounting close, full reconciliation, and general-ledger modification are outside the initial scope.

### Combined analysis

This is one of the project's most important capabilities:

- “Why did sales decline this month?”
- “Does the sales decline coincide with a stock shortage?”
- “Which products sell well but have supply problems?”
- “Which products with stockouts have pending purchases?”
- “Is the increase in purchase cost eroding margin?”
- “Which factors explain the deterioration in gross margin?”
- “How much of the increase in operating expenses is attributable to payroll cost?”
- “Which cost centers explain the growth in expenses and payroll?”
- “Which suppliers are affecting the availability of the best-selling products?”

The system must distinguish **observed correlation** from **demonstrated causation**.

### Conversational follow-up

When sufficient context exists:

- “Analyze July sales.”
- “Now compare them with June.”
- “Which products explain the difference?”
- “Check whether they had stock problems.”
- “Are there pending purchase orders for those products?”

Memory will be added only when it solves functional cases such as this one.

### Questions it must reject or limit

- queries that require writing or modifying ERP data;
- conclusions unsupported by data;
- arbitrary SQL requested for direct execution;
- sensitive employment decisions;
- accounting, tax, or legal advice beyond the available data;
- questions outside the implemented domains.

## Target users

- managers and executives;
- commercial leaders;
- inventory managers;
- purchasing managers;
- finance managers;
- payroll managers interested in aggregate analysis;
- controllers and accounting analysts for limited queries;
- business analysts;
- non-technical ERP users.

## Agent vs. Tool principle

Agents will not be created for each ERP module.

### Agentic reasoning
Suitable for:
- interpretation;
- planning;
- tool selection;
- routing;
- iterative analysis;
- synthesis;
- explanation.

### Deterministic code
Suitable for:
- queries;
- aggregations;
- calculations;
- comparisons;
- rankings;
- variances;
- aging;
- stockouts;
- lead times;
- payroll costs;
- accounting balances;
- persistence;
- validation.

## Implemented architecture

```text
User
  ↓
API / Conversation Layer
  ↓
Planner / Orchestrator — LangGraph
  ↓
 LangGraph Coordinator
  ├── Metadata discovery
  ├── Analyst agent — candidate SQL
  ├── Validator agent — semantic review
  ├── Deterministic guardrails
  ├── PostgreSQL EXPLAIN/read-only executor
  └── Synthesizer agent
  ↓
Canonical ERP Data Model
  ↓
PostgreSQL / Analytical Store
  ↓
Deterministic results
  ↓
Evidence + Synthesis
  ↓
Response / tables / charts
```

Security preference for MVP Core:

```text
LLM → Typed Tool → Domain Service → Controlled Query
```

Slice 10 is now the implemented primary path. Candidate SQL generated by the LLM must pass metadata validation, AST parsing, allowlists, limits, timeout, PostgreSQL validation, read-only permissions and auditing. Unvalidated SQL is never executed.

The Slice 10 flow will be:

```text
LLM Analyst → Validator Agent → Deterministic Guardrails → Read-only Executor
```

The local implementation will be abstracted through `ToolProvider` to enable a future MCP provider.

The following pattern remains prohibited outside the Slice 10 workflow and without its guardrails:

```text
LLM → Free-form SQL → Database
```

## Canonical ERP model

Extensible conceptual model:

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

Only the entities required for each phase will be implemented.

## Fictional ERP and data

The fictional ERP will be the official source for:

- public demo;
- desarrollo;
- tests;
- evaluation;
- ground truth.

The data will be synthetic but designed around coherent business scenarios. It will not be random noise.

The scenario must support meaningful relationships across domains, for example:

```text
Supplier delay
   ↓
Purchase order delayed
   ↓
Stockout
   ↓
Product sales decline
   ↓
Margin / business impact
```

y:

```text
Payroll cost increase
   ↓
Operating expense increase
   ↓
Accounting Lite explains period variance
```

## Integration with real ERPs

The architecture will be designed from the outset to support external sources without coupling the agentic layer to proprietary schemas.

```text
ERP real
  ↓
Integration / Adapter Layer
  ↓
Canonical ERP Contract
  ↓
ERP AI Analyst
```

An initial real integration should favor a **Replicated / Analytical Store** over direct agent access to the transactional ERP.

BIZAG may be evaluated as the first **Reference Adapter**, without making it a product dependency or publishing proprietary data, schemas, code, or credentials.

## Evolution through MCP

The following evolution is contemplated:

```text
ERP AI Analyst
   │ MCP Client
   ▼
ERP Integration MCP Server
   ├── BIZAG Adapter
   ├── SAP Adapter
   ├── Dynamics Adapter
   └── Other ERP Adapter
```

The MCP Server is not part of the MVP and is not currently considered a sixth official project.

## Main technologies

- LangGraph;
- LangSmith;
- OpenAI;
- FastAPI;
- PostgreSQL;
- Docker;
- frontend web.

pgvector or RAG will be added only if a concrete use case justifies it. This project should focus primarily on **structured data + tools + agentic workflows**.

## OpenAI

When appropriate:

- tool calling;
- structured outputs;
- interpretation;
- planning;
- grounded synthesis;
- controlled generation;
- model-assisted evaluation.

Reproducible calculations will remain in code.

## Observability and evaluation

LangSmith must make it possible to inspect:

- question;
- plan;
- routes;
- tools;
- arguments;
- results;
- errors;
- latency;
- model calls;
- response.

An evaluation dataset will be built with questions, expected tools, expected calculations, and known key facts.

## Security

- read-only in the MVP;
- authorized tools;
- typed contracts;
- parameterized/controlled queries;
- no unvalidated or destructive SQL; Slice 10 permits candidate SQL generated by the LLM within the controlled workflow;
- environment-managed secrets;
- `.env.example`;
- timeouts;
- result limits;
- logging without sensitive information;
- exclusively synthetic public data.

## Boundaries

- do not use real customer data or code;
- do not expose proprietary schemas;
- do not automate critical decisions;
- do not claim causation when only correlation exists;
- do not build a complete ERP;
- do not build a complete BI platform;
- do not turn Payroll into PeopleOps AI;
- do not turn Accounting Lite into an accounting system;
- do not build a universal ETL within the MVP;
- do not add MCP before its value is justified.

## Scope strategy

To keep the project finishable, scope layers will be used:

### MVP — mandatory scope
- Sales;
- Customers;
- Inventory;
- Purchases;
- aggregate Payroll Analytics;
- Accounting Lite;
- multi-step flagship question;
- LangGraph;
- LangSmith;
- evaluation;
- evidence.

### MVP+ — additional ERP value
- Purchases;
- Payroll Analytics agregado.

### Accounting Lite
- balances/aggregates by period;
- revenue/costs/expenses;
- variances;
- cost centers;
- gross margin.

### Implemented evolution after the MVP
- Slice 10 — Agentic Dynamic Query Execution;
- metadata tools, SQL validation, guardrails, read-only executor, and auditing;
- local provider compatible with future MCP contracts.

### Later extensions
- Accounts Receivable completo;
- real ERP integrations;
- BIZAG Reference Adapter;
- MCP Integration Server/provider based on the Slice 10 contracts;
- other ERP modules.

The six-domain MVP and the local dynamic-query evolution are implemented. Future work starts with real-provider equivalence, MCP, full receivables and fiscal-invoice semantics.

## What the repository must demonstrate

- professional README;
- PDD y PRD;
- architecture;
- canonical ERP model;
- reproducible synthetic data;
- scenarios and ground truth;
- tools and contracts;
- workflow LangGraph;
- tracing LangSmith;
- domain questions;
- multi-area demo;
- evidence;
- tests;
- evaluation suite;
- evaluation results;
- FastAPI;
- frontend;
- Docker;
- `.env.example`;
- security;
- limitations;
- roadmap;
- ADRs;
- licencia.

## Success criterion

ERP AI Analyst must demonstrate that an agentic application can investigate a complex business question using structured ERP data safely, reproducibly, and explainably, and that its architecture can evolve from a fictional ERP to real systems without rewriting the intelligence layer.

Functional breadth must not compromise this core evidence.
