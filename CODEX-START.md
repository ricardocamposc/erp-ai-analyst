# Codex Start Instructions — ERP AI Analyst

## Objective

Start ERP AI Analyst from an empty local directory and execute **only Slice 0 — Repository & Engineering Bootstrap**.

## Before changing anything

Read in this order:

1. `AGENTS.md`
2. `README.md`
3. `docs/PDD.md`
4. `docs/PRD.md`
5. `docs/SPEC.md`
6. `docs/REQ.md`
7. `docs/DATA.md`
8. `docs/CTX.md`
9. `docs/PLAN.md`
10. `docs/SLICE.md`
11. `docs/slices/slice-00-project-bootstrap.md`
12. `docs/ADR.md` and Accepted ADRs, especially ADR-0001 through ADR-0005
13. `docs/TEST.md` and `docs/EVAL.md`

The project scope and architectural boundaries in those documents are authoritative.

## Execute Slice 0 only

### Git

- inspect whether the directory is already a Git repository;
- if not, initialize it with `git init -b main`;
- if it already is, preserve history and report current branch/status;
- do not create remotes, commits or pushes unless explicitly requested.

### Structure

Create the repository structure defined in `docs/SPEC.md`. Do not populate future domain/agent directories with premature implementation.

### Engineering baseline

Implement:

- Python project configuration;
- FastAPI application;
- `GET /health`;
- settings/environment handling;
- `.env.example`;
- `.gitignore`;
- migration scaffold;
- pytest baseline;
- formatter/linter configuration;
- type-check configuration;
- `backend/Makefile` with the command contract defined in `docs/SPEC.md` and Slice 0.

### Docker baseline

Create the Docker definitions, but treat the backend container as an **optional reproducibility path**, not the normal development runtime. Create:

- `backend/Dockerfile`;
- `backend/docker-compose.yml` with default project name `erp-ai-analyst` and only:
  - `api`;
  - PostgreSQL `db`.

Required Docker characteristics:

- database healthcheck;
- named persistent database volume;
- project-local application network;
- `api` service configured to build from `backend/Dockerfile` **when `make run_docker` is explicitly used**;
- API/database configuration from environment variables;
- API dependency on healthy DB where supported;
- no hard-coded secrets.

Do **not** add Phoenix, pgvector, Redis, Celery, Adminer, Nginx, a frontend container, local LangSmith, or any local OpenAI service. LangSmith and OpenAI are later external integrations.

## Explicitly forbidden in Slice 0

Do not implement:

- ERP business tables;
- synthetic ERP business data;
- Sales/Customers/Inventory services;
- typed ERP tools;
- LangGraph nodes/graph;
- OpenAI calls;
- LangSmith tracing;
- evaluation cases;
- frontend UX;
- Purchases, Payroll, Accounting Lite, adapters or MCP.

## Validation

Run every applicable Slice 0 acceptance check from `docs/slices/slice-00-project-bootstrap.md`, including Git status, tests, lint/format, type checks, PostgreSQL startup/health and `docker compose config`. Validate the application using the preferred local mode (`make run`): PostgreSQL in Docker + FastAPI locally with reload.

**Do not run `docker compose up --build`, `docker compose build`, `make run_docker`, or otherwise build/start the API container unless the user explicitly requests containerized validation.** The existence of `backend/Dockerfile` and the Compose `api` service is required, but building that image is not part of normal Slice 0 completion.

## End-of-slice report

Return:

1. implementation summary;
2. files created/changed;
3. commands executed;
4. test/lint/type-check results;
5. Docker database/config/health results; if the optional API container was not explicitly requested, state that no API image build was performed;
6. Git branch/status;
7. ADRs created/decisions still pending;
8. risks or blockers;
9. explicit confirmation that Slice 1 or later was not implemented.

Then stop.

## Mandatory MVP scope clarification

The MVP is complete only when **Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite** are implemented, tested and represented in evaluation. Their implementation is incremental by slice, not optional. Payroll remains aggregated operational-financial analytics; Accounting Lite remains bounded analytical accounting. **Real ERP adapters, the BIZAG Reference Adapter and MCP are post-MVP improvements.**
