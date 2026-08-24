# AGENTS.md — ERP AI Analyst

This file defines repository-wide instructions for Codex and other coding agents.

## Mission

Build ERP AI Analyst as a portfolio-grade, production-oriented demonstration of agentic analytics over structured ERP data. Preserve the architecture and scope defined by the project documents; do not optimize for feature count.

## Authoritative reading order

Before implementing a slice, read:

1. `docs/PDD.md`
2. `docs/PRD.md`
3. `docs/SPEC.md`
4. `docs/REQ.md`
5. `docs/DATA.md`
6. `docs/CTX.md`
7. `docs/PLAN.md`
8. `docs/SLICE.md`
9. `docs/ADR.md` and all Accepted ADRs relevant to the slice
10. the active detailed file under `docs/slices/`
11. `docs/TEST.md`
12. `docs/EVAL.md`

If documents conflict, follow the hierarchy in `docs/CTX.md`. Do not silently reconcile material conflicts; report them.

## Current scope

The single mandatory MVP includes:

- Sales;
- Customers;
- Inventory;
- Purchases / Procurement;
- Payroll Analytics at aggregated operational-financial level;
- Accounting Lite at bounded analytical-accounting level;
- Canonical ERP analytical model;
- deterministic domain services;
- typed tools;
- LangGraph orchestration;
- OpenAI for agentic reasoning/synthesis;
- LangSmith tracing;
- evidence;
- evaluation;
- FastAPI;
- minimal UX when Slice 8 is reached;
- Docker-based local development.

These capabilities are introduced only in their authorized slice. Do not implement a later domain or layer early merely because it belongs to the MVP. Real ERP adapters, BIZAG Reference Adapter, MCP, full Accounts Receivable, RAG/pgvector and unrelated infrastructure remain post-MVP unless an accepted project change says otherwise.

## Architectural invariants

- Never allow the LLM to generate and execute arbitrary SQL.
- ERP operations are read-only.
- Business calculations belong in deterministic domain services, not prompts or graph nodes.
- Repository/database access must use controlled, parameterized queries through the chosen data-access layer.
- Agentic reasoning is for interpretation, planning, routing, iterative investigation and synthesis.
- Do not create one agent per ERP module.
- Typed schemas validate tool inputs and outputs.
- Important quantitative claims must be traceable to evidence/tool results.
- Do not present correlation as proven causality.
- Use only synthetic/public-safe data.
- Never commit secrets, tokens or real customer information.

## Slice discipline

For every requested slice:

1. inspect the repository state and current branch;
2. read the required documents and relevant ADRs;
3. state a short implementation plan;
4. implement **only** that slice;
5. add/update tests for the behavior introduced;
6. run all applicable quality checks;
7. update documentation only where the slice materially changes it;
8. report changed files, commands, checks, decisions and risks;
9. stop at the slice boundary.

Do not opportunistically implement later slices.

## Git rules

For Slice 0, if the working directory is not already a Git repository:

```text
git init -b main
```

If Git already exists, do not reinitialize it; preserve history and report the current branch/status.

Do not create remotes, push, force-push, rewrite history or create commits unless explicitly requested. Never commit `.env`, credentials, generated secrets or local database files.

## Docker and Makefile rules

Follow the accepted local-development model:

- repository roots are `backend/` and `frontend/`;
- backend operational files live under `backend/`;
- `backend/Makefile` is the primary command surface;
- `make run` starts PostgreSQL in Docker and FastAPI locally with reload;
- `make run_docker` runs the backend stack containerized;
- Compose default project/group name is `erp-ai-analyst`;
- Compose initially contains only `api` and `db`.

Do not add Phoenix, LocalStack, pgvector, Redis, Celery, Adminer or Nginx without a later accepted requirement/ADR. LangSmith and OpenAI remain external integrations.

## Project structure rule

Slice 0 must create the `backend/` + `frontend/` structure defined in `docs/SPEC.md`, including placeholders only where useful. Empty future directories may use `.gitkeep` or a small README only when necessary; do not populate future domain/agent code before its slice.

## Quality gates

A slice is not complete until its documented acceptance criteria and applicable checks pass. The repository must establish commands for at least:

- tests;
- lint/format verification;
- type checking;
- application startup checks; containerized API startup is optional unless explicitly requested by the active slice or user.

If the project tooling choice is unresolved, create/propose an ADR before locking a broad dependency/tooling decision into the repository.

## Dependency discipline

Prefer the minimum dependencies needed for the active slice. Every significant framework must have a clear architectural role. Do not introduce technology merely to broaden the stack shown in the portfolio.

## ADR discipline

Create/propose an ADR when a choice has broad or lasting impact, including data-access strategy, Python packaging/tooling, business-period semantics, evidence contract, graph termination, model configuration or deployment architecture.

Do not create ADRs for trivial code-level choices.

## End-of-slice report

Always report:

1. implementation summary;
2. files created/changed;
3. commands executed;
4. tests/lint/type/startup checks and results;
5. ADRs created, accepted or still required;
6. risks/blockers;
7. explicit confirmation that no later slice was implemented.

## Mandatory MVP scope clarification

The MVP is complete only when **Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite** are implemented, tested and represented in evaluation. Their implementation is incremental by slice, not optional. Payroll remains aggregated operational-financial analytics; Accounting Lite remains bounded analytical accounting. **Real ERP adapters, the BIZAG Reference Adapter and MCP are post-MVP improvements.**

## When running in autonomous slice mode:
- implement only one slice at a time;
- do not advance until all acceptance gates pass;
- do not modify scope-defining documents;
- stop and ask for approval only on defined blockers.