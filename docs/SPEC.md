# ERP AI Analyst — Technical Specification

**Status:** Implemented baseline and active evolution
**Scope:** MVP  
**Authoritative inputs:** `PDD.md`, `PRD.md`

## 1. Purpose

Define the implementation baseline for ERP AI Analyst: an ERP-agnostic, read-only, agentic analytics application over a Canonical ERP Data Model. The MVP implements **Sales + Customers + Inventory + Purchases + Payroll Analytics + Accounting Lite** and must demonstrate multi-step analysis, typed tools, deterministic calculations, cross-domain evidence, evaluation, and observability.

## 2. Architectural invariants

1. The LLM never executes arbitrary or unvalidated SQL; it may generate candidate SQL only inside Slice 10's guarded workflow.
2. The LLM reasons; deterministic code calculates.
3. Domain capabilities are exposed through metadata-driven query tools and retained typed domain tools backed by domain services.
4. PostgreSQL is the canonical analytical store for the synthetic ERP.
5. LangGraph orchestrates state, routing, tool execution, iteration, error handling, and synthesis.
6. OpenAI is used explicitly for structured interpretation/planning/tool use/synthesis, not reproducible calculations.
7. LangSmith traces model calls, plans, tool calls, arguments, results, errors, latency, and final answers.
8. Every important quantitative claim must be traceable to tool evidence.
9. The public repository uses only synthetic data.
10. The six-domain MVP and local Slice 10 are implemented; real ERP adapters, the BIZAG Reference Adapter, Accounts Receivable expansion and MCP remain future increments.

## 3. MVP capabilities

The system shall support:
- natural-language ERP questions;
- intent/period/entity extraction;
- multi-step planning;
- conditional tool routing;
- Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite analysis;
- commercial, supply-chain and financial/payroll cross-domain investigation;
- deterministic comparisons, rankings, variations, and stockout calculations;
- structured answers with findings, evidence, analysis performed, and warnings;
- insufficient-data handling;
- request/execution IDs;
- controlled retries and iteration limits;
- reproducible synthetic scenarios and ground truth;
- evaluation regression runs.

## 4. Signature scenario

Primary acceptance question:

> Why did sales decline this month?

The synthetic data must contain at least one explainable cross-domain pattern in which the workflow can discover a sales decline, identify contributing products/customers, inspect inventory, and report observed relationships without claiming unsupported causality.

## 5. Logical components

```text
Client / Minimal UI
        |
        v
FastAPI Conversation API
        |
        v
LangGraph Orchestrator
  | intent/context
  | planner
  | conditional routing
  | tool execution loop
  | synthesis
        |
        +-------------------------------------------------------+
        |          |          |          |          |          |
     Sales     Customer   Inventory  Purchases   Payroll   Accounting
      Tools      Tools       Tools      Tools      Tools      Tools
        |          |          |          |          |          |
        +----------+----------+----------+----------+----------+
                              |
                       Domain Services
                     |
              Repository Layer
                     |
          Canonical PostgreSQL

Cross-cutting: Pydantic contracts, evidence, logging, LangSmith, config,
error policy, tests, evaluation dataset.
```

## 6. Proposed repository structure

The repository is a monorepo with backend and frontend as separate top-level applications. Slice 0 establishes both roots immediately, while only the backend and database become executable in the bootstrap slice.

```text
erp-ai-analyst/
├── AGENTS.md
├── README.md
├── CODEX-START.md
├── .gitignore
├── docs/
│   ├── PDD.md
│   ├── PRD.md
│   ├── SPEC.md
│   ├── REQ.md
│   ├── DATA.md
│   ├── CTX.md
│   ├── PLAN.md
│   ├── SLICE.md
│   ├── TEST.md
│   ├── EVAL.md
│   ├── ADR.md
│   ├── adr/
│   ├── slices/
│   └── implementation/
├── backend/
│   ├── .env.example
│   ├── .env.docker.example
│   ├── Dockerfile
│   ├── Makefile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── domain/
│   │   │   ├── sales/
│   │   │   ├── customers/
│   │   │   ├── inventory/
│   │   │   ├── purchases/
│   │   │   ├── payroll/
│   │   │   └── accounting/
│   │   ├── tools/
│   │   ├── agent/
│   │   ├── evidence/
│   │   └── observability/
│   ├── scripts/
│   ├── tests/
│   ├── data/
│   └── evaluation/
└── frontend/
    ├── README.md
    └── (application scaffold is introduced in Slice 8)
```

Do not populate later-slice business code merely to fill directories. The structure is reserved early; implementation remains slice-bound.

### 6.1 Local runtime pattern

The development workflow supports two explicit modes:

```text
make run
  ├── PostgreSQL -> Docker
  └── FastAPI    -> local Python process with reload

make run_docker
  ├── PostgreSQL -> Docker
  └── FastAPI    -> Docker
```

The Compose project/group name is fixed by default as:

```yaml
name: ${COMPOSE_PROJECT_NAME:-erp-ai-analyst}
```

This groups the project containers, network and volumes under a stable Compose project name while still allowing override through `COMPOSE_PROJECT_NAME`.

The initial `backend/docker-compose.yml` contains only:

- `api` — FastAPI container for reproducible/containerized execution;
- `db` — PostgreSQL analytical store with healthcheck and persistent volume.

OpenAI and LangSmith are external integrations. Phoenix, LocalStack and pgvector are not part of this project's MVP architecture.

### 6.2 Makefile baseline

`backend/Makefile` is the primary developer command surface. Keep targets simple, explicit and project-specific. Minimum baseline:

- `run` — create/start `db`, then run FastAPI locally;
- `run_docker` — optional reproducible backend execution through Docker Compose; do not run it during normal development unless explicitly requested;
- `migrate` — ensure `db` is available and apply Alembic migrations;
- `refresh_db` / `confirmed_refresh_db` — destructive local reset with confirmation;
- `test` — run backend tests;
- `seed_db` / `seed_db_local` — introduced when Slice 1 adds synthetic ERP data;
- `lint`, `format`, `typecheck`, `check` — quality gates adapted to the selected Python toolchain.

Additional targets may be added only when they reduce a real recurring workflow.

### 6.3 Git bootstrap baseline

Slice 0 must initialize the local repository when necessary using branch `main` with `git init -b main`. If Git already exists, preserve the repository/history. Slice 0 does not create remotes, push, rewrite history or create commits unless explicitly instructed.

## 7. Initial API contract

### `POST /api/v1/analysis`
Input:
```json
{
  "question": "Why did sales decline this month?",
  "conversation_id": null
}
```

Output concept:
```json
{
  "request_id": "uuid",
  "answer": "...",
  "key_findings": [],
  "evidence": [],
  "analysis_performed": [],
  "warnings": [],
  "status": "completed"
}
```

### `GET /health`
Process health only. Database/model readiness may be exposed separately if useful.

## 8. Tool baseline

Representative commercial tools from PRD (the complete MVP tool catalog is frozen in Slice 5):
- `get_sales_summary`
- `compare_sales_periods`
- `get_sales_by_customer`
- `get_sales_by_product`
- `get_customer_purchase_history`
- `find_customers_with_sales_decline`
- `get_stock_history`
- `get_out_of_stock_periods`
- `find_stockout_products`

Exact tool schemas are frozen during Slice 5 after all six domain-service contracts exist.

## 9. Agent state baseline

State should minimally carry:
- request ID;
- user question;
- normalized intent/context;
- plan/remaining steps;
- tool-call history;
- deterministic tool results;
- evidence items;
- warnings/errors;
- iteration count;
- final structured answer.

Do not persist conversational memory in the first slice unless required by an acceptance case.

## 10. Error and safety policy

- Reject write/update/delete ERP operations.
- Reject arbitrary SQL execution.
- Validate every tool input with typed schemas.
- Parameterize controlled queries.
- Apply result-size limits and timeouts.
- Cap graph/tool iterations.
- Return explicit insufficient-data warnings when evidence is inadequate.
- Never transform correlation into causal certainty.
- Keep secrets outside source control.

## 11. Definition of MVP complete

MVP is complete only when the mandatory six-domain scope is demonstrably met: synthetic ERP, canonical model, deterministic services/tools for Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite, LangGraph multi-step workflow, required cross-domain scenarios, evidence, LangSmith, evaluation suite, tests, API/minimal UX, Docker, `.env.example`, and public-safe synthetic data.

## Mandatory MVP scope clarification

The MVP is complete only when **Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite** are implemented, tested and represented in evaluation. Their implementation is incremental by slice, not optional. Payroll remains aggregated operational-financial analytics; Accounting Lite remains bounded analytical accounting. **Real ERP adapters, the BIZAG Reference Adapter and MCP are post-MVP improvements.**
