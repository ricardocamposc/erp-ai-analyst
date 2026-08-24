# ERP AI Analyst — Documentation Pack

This package converts PDD v1.1 and PRD v1.1 into an implementation-ready baseline for a new local repository. It is designed to be handed to Codex and executed one slice at a time.

## Root files

- `README.md` — project-facing README created before implementation.
- `AGENTS.md` — repository-wide instructions and guardrails for Codex/coding agents.
- `CODEX-START.md` — exact first instruction for Codex: execute Slice 0 only.

## Project documents

- `docs/PDD.md` — project definition (authoritative source baseline).
- `docs/PRD.md` — product requirements (authoritative source baseline).
- `docs/SPEC.md` — technical specification, exact repository structure and local runtime baseline.
- `docs/REQ.md` — traceable functional/non-functional requirements.
- `docs/DATA.md` — canonical six-domain MVP data and synthetic scenario design.
- `docs/CTX.md` — persistent implementation context/rules for Codex.
- `docs/PLAN.md` — phased implementation plan.
- `docs/SLICE.md` — master index, dependency order and status map for the 10 implementation slices.
- `docs/slices/` — detailed executable specification for each Slice 0–9.
- `docs/TEST.md` — test strategy.
- `docs/EVAL.md` — evaluation dataset and metrics design.
- `docs/ADR.md` — ADR index.
- `docs/adr/` — accepted/proposed architecture decisions.

## Infrastructure decision for MVP

The Slice 0 local runtime is deliberately small:

```text
docker compose
├── api   FastAPI
└── db    PostgreSQL
```

It includes a DB healthcheck, persistent named volume, internal application network and environment-driven configuration. OpenAI and LangSmith are external services used in later slices. Phoenix is intentionally not part of ERP AI Analyst because LangSmith is the selected agent/workflow tracing platform.

## Recommended start

1. Create an empty directory for the project.
2. Copy/extract this complete package into it.
3. Open the directory in Codex.
4. Give Codex the instruction in `CODEX-START.md`.
5. Allow Codex to execute **only Slice 0**.
6. Review the resulting repository and checks before authorizing Slice 1.
7. For each later slice, make Codex read the corresponding detailed file under `docs/slices/` and implement only that slice.

Slice 0 itself initializes Git on branch `main` when necessary, creates the project structure, and establishes Docker/FastAPI/PostgreSQL/testing/tooling.


## Repository pattern

The implementation baseline uses separate `backend/` and `frontend/` applications, with backend-local Makefile/Docker/Compose. `make run` is the preferred daily-development path: PostgreSQL runs in Docker while FastAPI runs locally with reload. `make run_docker` is available only for explicit reproducibility/container validation and is not part of the normal development loop.
