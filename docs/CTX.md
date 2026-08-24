# ERP AI Analyst — Implementation Context for Codex

## 1. Mission

Build the flagship portfolio project **ERP AI Analyst**, demonstrating AI Solutions Architecture & Agentic Enterprise Systems over structured ERP data.

## 2. Source hierarchy

When implementation choices conflict, use this order:
1. `docs/PDD.md` — project definition and boundaries.
2. `docs/PRD.md` — product requirements and acceptance criteria.
3. `docs/SPEC.md` — implementation baseline.
4. `docs/REQ.md` — traceable requirements.
5. accepted ADRs — architectural decisions.
6. current slice instructions.

Do not silently expand scope.

## 3. Current scope

Implement the single mandatory MVP incrementally through Slices 0–9. The MVP includes:
- Sales;
- Customers;
- Inventory;
- Purchases / Procurement;
- Payroll Analytics at aggregated operational-financial level;
- Accounting Lite at bounded analytical-accounting level;
- Canonical ERP model;
- deterministic domain services;
- typed tools;
- LangGraph multi-step orchestration;
- OpenAI structured/tool-based reasoning and synthesis;
- LangSmith tracing;
- evidence;
- evaluation;
- FastAPI;
- minimal UX in Slice 8;
- Docker and reproducible local setup (`api` + PostgreSQL `db` for Slice 0 bootstrap).

The fact that a capability belongs to the MVP does not authorize Codex to implement it before its detailed slice.

## 4. Hard constraints

- No free-form SQL generated/executed by the LLM.
- No write operations against ERP data.
- No agent-per-module architecture.
- No pgvector/RAG unless a later use case explicitly justifies it.
- No real client data, proprietary schemas, credentials, or private code.
- No MCP or real ERP adapter before the six-domain MVP is complete.
- No Phoenix in the MVP baseline; LangSmith is the agent/workflow tracing platform.
- No Redis, Celery, pgvector, Nginx, Adminer or other infrastructure without an explicit requirement/ADR.
- OpenAI and LangSmith are external services, not local containers.
- Do not claim causal relationships when only correlation is observed.
- Do not call the project production-ready; use production-oriented where justified.

## 5. Coding rules

- Prefer small typed Python modules.
- Keep business formulas outside prompts and graph nodes.
- Graph nodes coordinate; domain services calculate.
- Repositories own controlled database access.
- Tools adapt typed agent requests to domain services.
- Use Pydantic models at boundaries.
- Add tests with each behavior, not after all implementation.
- Avoid framework wrappers that obscure the architectural evidence.
- Keep prompts versioned as files/modules and concise.

## 6. Git, repository structure, and local runtime

- Slice 0 initializes Git on branch `main` if the directory is not already a Git repository.
- Never reinitialize an existing Git repository.
- Do not create remotes, commits, pushes or history rewrites unless explicitly requested.
- Slice 0 creates the directory structure defined in `SPEC.md`; future implementation code remains deferred to its slice.
- Slice 0 Docker Compose starts with `api` + `db` only.
- `db` must have a healthcheck, named volume and project-local network.
- `api` is built from the `backend/Dockerfile` and configured by environment variables.
- Frontend containerization is deferred until the UX slice.

## 7. Local workflow expected from Codex

For every slice:
1. read PDD, PRD, SPEC, REQ, CTX, `docs/SLICE.md`, relevant ADRs, and the active detailed file under `docs/slices/`;
2. inspect current repository state;
3. state a short implementation plan;
4. implement only the slice scope;
5. run formatting/lint/type/tests required by the repository;
6. fix failures caused by the change;
7. update docs/ADRs if a decision changed;
8. report files changed, commands run, test results, and remaining risks;
9. stop at the slice boundary.

## 8. Decision discipline

If an unresolved choice materially affects architecture or business semantics, do not bury it in code. Create/propose an ADR. Examples: ORM/data-access strategy, exact canonical key strategy, comparison-period semantics, stockout formula, OpenAI model/config policy, graph termination policy.

## 9. Definition of safe completion

A slice is complete only when its acceptance checks pass locally and no out-of-scope feature was introduced.

## Mandatory MVP scope clarification

The MVP is complete only when **Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite** are implemented, tested and represented in evaluation. Their implementation is incremental by slice, not optional. Payroll remains aggregated operational-financial analytics; Accounting Lite remains bounded analytical accounting. **Real ERP adapters, the BIZAG Reference Adapter and MCP are post-MVP improvements.**
