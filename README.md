# ERP AI Analyst

**Agentic Enterprise Analytics for ERP** — flagship portfolio project focused on AI Solutions Architecture & Agentic Enterprise Systems.

> **Current status:** MVP implementation complete through Slice 9; all six mandatory domains are synthetic, deterministic and evaluated. Slice 10 is the next authorized evolutionary improvement: agentic dynamic query execution with metadata discovery, SQL validation, read-only guardrails and audit.

## What this project demonstrates

ERP AI Analyst lets a user ask business questions in natural language over a synthetic ERP analytical store. The system interprets the request, plans a controlled multi-step analysis, selects typed tools, executes deterministic domain services, and returns traceable findings with evidence.

The public implementation is ERP-agnostic and uses only synthetic data.

## MVP

The single mandatory MVP includes:

- Sales;
- Customers;
- Inventory;
- Purchases / Procurement;
- Payroll Analytics at aggregated operational-financial level;
- Accounting Lite at bounded analytical-accounting level;
- Canonical ERP Data Model in PostgreSQL;
- deterministic domain services;
- typed tools;
- LangGraph orchestration;
- OpenAI structured/tool-based reasoning and synthesis;
- LangSmith tracing;
- structured evidence;
- evaluation against known ground truth;
- FastAPI;
- minimal web UX after backend acceptance;
- Docker-based local reproducibility.

All six domains are mandatory for MVP Definition of Done. They are implemented incrementally through the slice plan; Slice 10 is the authorized local dynamic-query evolution after the MVP, followed by real ERP adapters, BIZAG and an MCP provider.

## Architectural principles

- **ERP-agnostic.** The agentic layer does not depend on proprietary ERP schemas.
- **Read-only.** The MVP never writes business transactions.
- **Dynamic SQL is proposed by the LLM only inside Slice 10's guarded workflow.** Candidate SQL must pass AST validation, allowlists, read-only permissions, limits, timeout and audit before execution.
- **LLM reasons; code calculates.** Reproducible calculations remain deterministic.
- **No agent per ERP module.** Domains are primarily tools and services.
- **Evidence before assertion.** Quantitative claims must be traceable to tool results.
- **Correlation is not causality.** The system must not overstate conclusions.
- **Synthetic public data only.** No client data, private schemas or proprietary code.

## High-level architecture

```text
User / Conversational Web UI
        |
        v
      FastAPI
        |
        v
 LangGraph Orchestrator
        |
        +-------------------------------------------------------+
        |          |          |          |          |          |
      Sales    Customers  Inventory  Purchases   Payroll   Accounting
      Tools      Tools      Tools      Tools       Tools      Tools
        |          |          |          |          |          |
        +----------+----------+----------+----------+----------+
                              |
                 Domain Services
                        |
                 Repository Layer
                        |
                  PostgreSQL
             Canonical ERP Store

Cross-cutting:
OpenAI · LangSmith · structured logging · evidence · tests · evaluation
```

## Repository and local runtime target

The repository uses separate top-level `backend/` and `frontend/` applications. Backend operational files live inside `backend/`.

Preferred daily development:

```text
cd backend
make run
  ├── PostgreSQL -> Docker
  └── FastAPI    -> local process with reload
```

Reproducible containerized execution:

```text
cd backend
make run_docker
  ├── PostgreSQL -> Docker
  └── FastAPI    -> Docker
```

Docker Compose uses `erp-ai-analyst` as the default project/group name. OpenAI and LangSmith are external services. The frontend exists as a top-level application boundary from Slice 0 and is implemented as the conversational UX in Slice 8.

## Repository documentation

Read the project documents in this order before implementing:

1. `docs/PDD.md`
2. `docs/PRD.md`
3. `docs/SPEC.md`
4. `docs/REQ.md`
5. `docs/DATA.md`
6. `docs/CTX.md`
7. `docs/PLAN.md`
8. `docs/SLICE.md`
9. the active detailed file under `docs/slices/`
10. `docs/ADR.md` and `docs/adr/`
11. `docs/TEST.md`
12. `docs/EVAL.md`

`AGENTS.md` contains the execution rules for Codex and other coding agents.

## Implementation workflow

Implementation proceeds one reviewable slice at a time. The first action is **Slice 0 — Project Bootstrap**.

Slice 0 establishes:

- Git repository on branch `main`;
- project directory structure;
- Python project configuration;
- FastAPI `/health` endpoint;
- environment/settings baseline;
- `backend/Dockerfile`;
- `backend/docker-compose.yml` with API + PostgreSQL;
- `backend/Makefile` as the primary developer command surface;
- separate root `backend/` and `frontend/` applications;
- PostgreSQL healthcheck, volume and network;
- migration scaffold;
- pytest/lint/type-check baseline;
- `.env.example` and `.gitignore`;
- reproducible local commands.

It deliberately does **not** implement ERP domain tables, synthetic business data, LangGraph nodes, OpenAI integration or later-slice domain/business functionality.

## Development commands

The definitive commands are established by Slice 0 and documented here by Codex after the bootstrap is implemented. Expected capabilities include:

```text
start local stack
stop local stack
run migrations
run tests
run lint
run type checks
```

Do not invent or rely on commands that have not yet been implemented in the repository.

## Run the MVP locally

```bash
cd backend
cp .env.example .env
python -m pip install -e '.[dev]'
make migrate
make seed_db
make run
```

Open `http://127.0.0.1:8000/` for the minimal UX. The API contract is
`POST /api/v1/analysis` with `{"question": "...", "conversation_id": null}`.
OpenAI and optional LangSmith credentials are loaded from `.env`; they are
never committed. Run the offline regression suite with `make evaluate`.
See [`docs/RELEASE-CHECKLIST.md`](docs/RELEASE-CHECKLIST.md) for the release
path and demo questions.

## Documentation status

PDD and PRD v1.1 are the authoritative product baselines. Technical documents and ADRs translate them into executable implementation constraints. When an implementation decision changes a lasting architectural choice, record it as an ADR rather than silently changing behavior.

## Roadmap

1. MVP — Sales + Customers + Inventory + Purchases + Payroll Analytics + Accounting Lite.
2. Extended receivables.
3. Real ERP integration/reference adapter.
4. Slice 10 dynamic agentic query execution.
5. MCP provider exploration using the Slice 10 `ToolProvider` contract, only after local validation.

## Portfolio evaluation evidence

The project includes two complementary evaluation layers:

- Offline Baseline v1.2: 36 deterministic ground-truth cases across the six MVP domains,
  cross-domain workflows, guardrails and resilience scenarios.
- Agentic Evaluation v2: 108 executions (36 cases × 3 repetitions) through
  `OpenAIGateway` and the bounded LangGraph workflow, with LangSmith configured.

The official Agentic v2 result is available at
`backend/evaluation/results/latest-agentic-v2.json` and the human-readable report at
`backend/evaluation/runs/agentic-v2-official-20260824-223517.md`.

The project is production-oriented as a portfolio MVP, not production-ready. Known
limitations include unavailable token/cost metadata, no trace-level LangSmith metrics,
and no real ERP adapters, authentication or write operations.

## License

To be selected before the first public portfolio release.

## Mandatory MVP scope clarification

The MVP is complete only when **Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite** are implemented, tested and represented in evaluation. Their implementation is incremental by slice, not optional. Payroll remains aggregated operational-financial analytics; Accounting Lite remains bounded analytical accounting. **Slice 10 is the authorized local dynamic-query evolution; real ERP adapters, the BIZAG Reference Adapter and the MCP provider remain subsequent improvements.**
