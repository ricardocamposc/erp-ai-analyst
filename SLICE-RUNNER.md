# ERP AI Analyst — Autonomous Slice Runner

## Goal

Continue ERP AI Analyst implementation from the first unfinished slice through the authorized evolutionary roadmap. Slice 10 is explicitly enabled after the MVP release.

Work slice by slice without asking for confirmation between successful slices.

For each slice:

1. read the authoritative project documentation;
2. plan the slice;
3. implement only that slice;
4. run its required tests;
5. perform an architecture/scope review;
6. fix failures and blocker/major findings;
7. validate acceptance criteria and Definition of Done;
8. produce a concise slice completion report;
9. automatically continue to the next slice when all gates pass.

Stop only when a defined stop condition requires user confirmation.

## Required reading before execution

Read these files before changing code:

- `AGENTS.md`
- `docs/WORKFLOW.md`
- `docs/CTX.md`
- `docs/SPEC.md`
- `docs/PLAN.md`
- `docs/SLICE.md`
- all applicable ADRs
- the detailed document for the active slice under `docs/slices/`

Consult `PDD.md` and `PRD.md` whenever scope, requirements, or boundaries need clarification.

Do not rely on conversation history when the repository documentation provides the authoritative answer.

## Starting point

Slices 0-9 have been implemented/released as the MVP baseline. Slice 10 is the next active evolutionary slice.

Start with Slice 10 unless the repository status or user explicitly selects another active slice.

Do not reimplement Slice 0 unless a later slice exposes a real bootstrap defect that must be corrected.

## Slice execution loop

For each active slice, execute this loop:

```text
READ
  ↓
PLAN
  ↓
IMPLEMENT
  ↓
TEST
  ↓
REVIEW
  ↓
FIX (if needed)
  ↓
RETEST
  ↓
ACCEPTANCE
  ↓
PASS → NEXT SLICE
FAIL → FIX LOOP
BLOCKED → STOP AND ASK
```

Never implement multiple slices as one undifferentiated change.

A slice may contain multiple internal tasks, but the slice boundary remains the acceptance boundary.

## Roles to emulate or delegate

Use distinct reasoning/review roles even if the environment does not expose named subagents:

### Planner
Creates the slice-limited plan and requirement-to-test mapping.

### Implementer
Writes the production code for the active slice.

### Tester
Runs required tests and adds missing tests required by the slice.

### Reviewer
Checks architecture, security, scope, ADR compliance, deterministic calculations, contracts, and premature future-slice work.

### Fixer
Repairs failures and blocker/major review findings.

### Acceptance
Checks every acceptance criterion and the Definition of Done.

Do not allow the same implementation assumption to pass unchallenged merely because one role introduced it.

## Automatic continuation policy

Advance automatically when:

- all required tests pass;
- all acceptance criteria pass;
- Definition of Done passes;
- no blocker finding remains;
- no major finding remains;
- no stop condition is active.

Do not ask for confirmation merely to move from one successful slice to the next.

## Mandatory stop conditions

Stop and ask for confirmation only when:

- a new architectural decision is required and is not covered by accepted ADR-0006;
- authoritative documents materially conflict;
- MVP scope would change;
- an ADR must be created or an accepted ADR outside Slice 10 must change;
- required credentials or external permissions are unavailable;
- an unsafe/destructive operation is required;
- there is risk of deleting non-synthetic/non-local data;
- a major dependency/framework not already approved is required;
- repeated focused repair attempts cannot make the slice pass;
- work outside the repository is required;
- a security-sensitive ambiguity cannot be resolved from documentation;
- the current slice cannot be completed without implementing a later slice prematurely.

When stopping, state:

1. active slice;
2. exact blocker;
3. evidence;
4. options;
5. recommended option;
6. the minimum confirmation needed.

## Local database configuration

Use the existing PostgreSQL instance.

```text
Host:     as configured in .env
Port:     5435
Database: as configured in .env
User:     as configured in .env
Password: as configured in .env
```

The project `.env` already contains the connection parameters.

Rules:

- load connection settings from `.env`;
- do not hard-code credentials;
- do not overwrite valid `.env` values;
- do not start another PostgreSQL container just because a Compose file exists;
- do not reset or recreate the database unless the active slice explicitly requires it and the operation is safe for synthetic/local data.

If database connectivity fails, verify `.env`, port `5435`, and the existing PostgreSQL service before changing application code.

## API server rule for tests

When a test requires a live FastAPI server:

1. attempt to bind to port `8000`;
2. if port `8000` is occupied, probe sequentially for the next free port:
   - `8001`
   - `8002`
   - `8003`
   - continue until a free port is found;
3. start the API on that port;
4. configure the test client/base URL to use the selected port;
5. run the required validation;
6. shut down only the server process started by this workflow.

Never terminate an unrelated process just to free port `8000`.

Example intent:

```bash
# preferred
uvicorn app.main:app --host 127.0.0.1 --port 8000

# if occupied
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Use the actual project entry point if it differs.

## Backend execution policy

The normal development path is:

```text
PostgreSQL → existing local service on port 5435
FastAPI    → local Python environment with reload when needed
```

Do not assume that the API must run in Docker.

The backend Dockerfile and Compose service exist for reproducibility and optional containerized validation.

Unless the active slice explicitly requires container validation, do not execute:

```bash
docker compose build
docker compose up --build
make run_docker
```

Prefer the local Makefile workflow and local Python execution.

If a Docker validation is explicitly required, perform it as an additional check rather than replacing the normal local workflow.

## Makefile usage

Prefer documented Makefile targets over long ad-hoc command sequences when an equivalent target exists.

Typical backend workflow may include targets such as:

```bash
make run
make migrate
make test
make lint
make format
make typecheck
make check
```

Use only targets that actually exist in the repository.

Do not invent a Make target and assume it exists.

When a slice adds a required operational capability, update the Makefile only if that change is within the slice scope or required by its acceptance criteria.

## Git policy

Preserve the existing Git repository.

Do not:

- create a new remote;
- push changes;
- rewrite history;
- force-reset branches;
- create tags/releases;
- commit automatically unless project instructions explicitly authorize it.

Git may be used to inspect:

- current branch;
- working tree;
- diffs;
- changed files.

Avoid discarding user changes.

## Implementation invariants

These rules are mandatory throughout all slices:

- ERP access remains read-only.
- The LLM must not execute arbitrary/free-form SQL.
- Use typed tools and controlled queries.
- Business calculations remain deterministic.
- The LLM may interpret, plan, select tools, iterate, and synthesize.
- Quantitative claims must be grounded in tool results.
- Do not present correlation as proven causality.
- Use synthetic/public-safe data only.
- Payroll remains aggregated operational-financial analytics.
- Do not expand Payroll into PeopleOps functionality.
- Accounting Lite remains intentionally bounded.
- Do not implement ERP adapters, BIZAG adapter, or MCP as part of this MVP workflow.
- Do not add RAG unless the project documentation is explicitly changed to require it.
- Do not add technologies merely for portfolio keywords.

## Testing policy

Run the smallest relevant tests during implementation, then the complete tests required by the active slice before acceptance.

Where applicable, validate:

- unit tests;
- repository/service integration;
- tool contracts;
- migrations;
- data consistency;
- API contracts;
- LangGraph state/routing;
- OpenAI structured outputs/tool calls;
- evidence linking;
- negative cases;
- evaluation dataset;
- regression suite.

Never mark a slice complete because “the code looks correct.”

## Review policy

Before acceptance, explicitly check for:

- scope creep;
- hidden implementation of later slices;
- duplication;
- unused abstractions;
- free-form SQL exposure;
- calculations delegated to the LLM;
- unsupported quantitative claims;
- missing evidence;
- unsafe database behavior;
- missing error handling;
- missing type/schema validation;
- tests that do not actually assert the intended behavior;
- documentation that contradicts the implementation.

Classify findings:

```text
BLOCKER
MAJOR
MINOR
SUGGESTION
```

BLOCKER and MAJOR findings must be fixed before advancing.

MINOR findings may be fixed immediately when safe and small, or recorded as non-blocking technical debt.

## Per-slice completion report

After every slice, output:

```text
Slice: <number and name>
Status: PASS | BLOCKED
Implemented:
- ...

Tests:
- command → result
- ...

Acceptance:
- criterion → PASS/FAIL

Review:
- blocker: 0
- major: 0
- minor: ...
- suggestions: ...

Fixes:
- ...

Known limitations:
- ...

Files changed:
- ...

Next:
- Slice N+1
```

If `Status: PASS`, continue automatically.

If `Status: BLOCKED`, stop and request the minimum necessary confirmation.

## Final completion report

After the final MVP slice passes, stop and provide:

- MVP completion status;
- slices completed;
- complete test summary;
- evaluation summary;
- known limitations;
- non-blocking technical debt;
- local run instructions;
- API run instructions;
- frontend run instructions;
- database assumptions;
- post-MVP items explicitly excluded from this workflow.

Do not begin adapters, MCP, BIZAG integration, or other post-MVP work automatically.
