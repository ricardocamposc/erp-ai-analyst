# ADR-0005 — Repository, Local Development and Containerization Baseline

**Status:** Accepted  
**Scope:** MVP repository and local development  
**Decision date:** 2026-08-24

## Context
ERP AI Analyst needs a fast daily-development workflow while retaining a reproducible Docker execution path for integration validation, CI, demos and deployment-oriented checks. The project also benefits from a clear separation between backend and frontend applications.

## Decision

### Repository
Use top-level `backend/` and `frontend/`. The Python package uses `backend/app/`. Backend operational files (`Dockerfile`, `docker-compose.yml`, `Makefile`, Alembic configuration) live under `backend/`.

### Makefile
`backend/Makefile` is the primary developer command surface. Minimum operational targets are:

- `run` — ensure PostgreSQL is running in Docker, then run FastAPI locally with reload;
- `run_docker` — optional reproducible execution of `api` + `db` in Docker;
- `migrate`;
- `refresh_db`;
- `confirmed_refresh_db`;
- `test`;
- `lint`;
- `format`;
- `typecheck`;
- `check`;
- seed targets when synthetic data exists.

### Preferred local runtime
`make run` is the default daily-development mode. It starts PostgreSQL in Docker and FastAPI as a local Python process with reload. It must **not** build or start the API container and must not require an API image rebuild after code changes.

### Optional containerized runtime
`make run_docker` exists only for explicit reproducibility/container validation, CI/demo or deployment-oriented checks. It is not part of the mandatory developer loop and is not required for ordinary Slice 0 acceptance unless explicitly requested.

The `api` service may still be declared in `backend/docker-compose.yml` so the reproducible mode is defined from the start. `docker compose config` is sufficient to validate that definition during normal Slice 0 work.

### Compose project/group name
Use:

```yaml
name: ${COMPOSE_PROJECT_NAME:-erp-ai-analyst}
```

This provides a stable project/group name for containers, networks and volumes while allowing overrides.

### Components not included
Phoenix, LocalStack, pgvector and unrelated RAG/vector infrastructure are not part of the ERP AI Analyst MVP. LangSmith and OpenAI remain external services.

## Consequences

### Positive
- fast local backend iteration with reload;
- no API image rebuild during ordinary development;
- reproducible Docker execution remains available when needed;
- clear backend/frontend separation;
- stable Makefile command surface;
- stable Compose resource grouping.

### Trade-offs
- developers need local Python tooling plus Docker for PostgreSQL;
- two execution modes must remain consistent;
- frontend containerization remains deferred until Slice 8.

## Implementation impact
Slice 0 must create/refactor the repository according to `docs/SPEC.md` and `docs/slices/slice-00-project-bootstrap.md`. Normal Slice 0 validation must exercise the local mode and validate Compose configuration without requiring an API image build.
