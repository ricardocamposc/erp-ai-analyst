# Slice 0 — Project Bootstrap

## 1. Objective
Create a reproducible engineering baseline from an empty local directory with separate `backend/` and `frontend/` roots, backend-local development supported by Dockerized PostgreSQL, and a Makefile as the primary developer command surface.

## 2. Dependencies
None.

## 3. Scope
- Initialize Git with `git init -b main` when needed; preserve existing history otherwise.
- Create the repository structure defined in `docs/SPEC.md`, with `backend/` and `frontend/` separated at root.
- Under `backend/`, create the Python/FastAPI project, `app/`, Alembic scaffold, tests, scripts, Dockerfile, Makefile and docker-compose.yml.
- Create a minimal FastAPI `GET /health`.
- Create `frontend/README.md` as a placeholder for the conversational web application implemented in Slice 8; do not scaffold the frontend framework yet.
- Configure `backend/docker-compose.yml` with default Compose project name `erp-ai-analyst`, services `api` and `db`, PostgreSQL healthcheck, persistent named volume and project network.
- Configure local and Docker environment examples without secrets.
- Establish pytest, lint/format and type-check quality gates.
- Create `backend/Makefile` with the agreed operational targets and semantics defined in this slice.

## 4. Out of scope
ERP tables, synthetic data, domain services, typed tools, LangGraph, OpenAI, LangSmith, evaluation implementation, frontend implementation, adapters, MCP, Phoenix, LocalStack, pgvector, Redis, Celery and unrelated infrastructure.

## 5. Required repository baseline
```text
erp-ai-analyst/
├── AGENTS.md
├── README.md
├── CODEX-START.md
├── .gitignore
├── docs/
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
│   │   ├── tools/
│   │   ├── agent/
│   │   ├── evidence/
│   │   └── observability/
│   ├── scripts/
│   ├── tests/
│   ├── data/
│   └── evaluation/
└── frontend/
    └── README.md
```

## 6. Makefile contract
The Makefile lives in `backend/`. Minimum targets:

- `make run` — create/start PostgreSQL and run FastAPI locally with reload;
- `make run_docker` — run `api` + `db` containerized;
- `make migrate` — start DB if needed and apply Alembic migrations;
- `make refresh_db` — confirm destructive reset before delegating to `confirmed_refresh_db`;
- `make confirmed_refresh_db` — remove the project DB volume and recreate/migrate;
- `make test`;
- `make lint`;
- `make format`;
- `make typecheck`;
- `make check` — aggregate non-destructive quality gates.

`seed_db` and `seed_db_local` may exist as documented placeholders or be introduced in Slice 1 when synthetic data is implemented. Do not add unrelated targets or services.

## 7. Docker/Compose rules
- `name: ${COMPOSE_PROJECT_NAME:-erp-ai-analyst}`.
- `db` is PostgreSQL, exposes only the local port needed for development, has healthcheck and named volume.
- `api` builds from `backend/Dockerfile`, consumes `.env` plus Docker-specific env where appropriate and supports a reproducible container run.
- For daily development, `make run` must not require rebuilding the API container.
- OpenAI and LangSmith are external, not containers.

## 8. Required tests
- application import/startup test;
- `/health` success test;
- settings/config validation where useful;
- `docker compose config`;
- DB health/startup verification.

## 9. Acceptance criteria
1. Git is initialized on `main` or existing Git state is preserved.
2. Root contains separate `backend/` and `frontend/`.
3. Backend follows the `app/`-based structure above.
4. `backend/Makefile` exposes the agreed command surface.
5. `make run` starts DB in Docker and FastAPI locally without an API image rebuild.
6. `make run_docker` exists as an optional reproducible execution path, but it is not required to be executed during normal Slice 0 validation.
7. Compose resources are grouped under `erp-ai-analyst` by default.
8. PostgreSQL becomes healthy and `/health` succeeds with FastAPI running locally.
9. Quality gates execute successfully.
10. `docker compose config` validates the optional containerized API definition without requiring an API image build.
11. No Slice 1+ business functionality is implemented.

## 10. Validation commands
From `backend/`, validate at minimum:

```text
make test
make lint
make typecheck
make check
docker compose config
make migrate
```

Also validate `make run` in local-development mode and confirm the API is reachable. Do **not** build or start the `api` container unless explicitly requested. `make run_docker` is defined for later reproducibility checks, CI/demo or explicit container validation.

## 11. Deliverables
A clean repository bootstrap with separate backend/frontend applications, a local-first developer workflow, reproducible database infrastructure and optional containerized backend execution.

## 12. Definition of Done
All acceptance criteria pass, Makefile commands are documented, local and Docker execution both work, no secrets are committed, and no later-slice business functionality has been introduced.

## 13. Prohibitions
Do not add Phoenix, LocalStack, pgvector or unrelated infrastructure. Do not add components that are not required by the active project scope.
