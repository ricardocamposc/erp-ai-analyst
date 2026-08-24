# ERP AI Analyst — Autonomous Slice Workflow

## Purpose

This document defines the controlled multi-agent workflow used to implement ERP AI Analyst slice by slice.

The workflow is autonomous within the boundaries already defined by the project documentation. It may plan, implement, test, review, fix, and validate each slice without stopping between slices, provided that every quality gate passes and no explicit stop condition is reached.

The workflow must not change product scope, architectural decisions, or project-definition documents on its own.

## Authoritative documentation

Before working on any slice, agents must read and respect:

1. `AGENTS.md`
2. `docs/CTX.md`
3. `docs/SPEC.md`
4. `docs/PLAN.md`
5. `docs/SLICE.md`
6. the active detailed slice document under `docs/slices/`
7. applicable ADRs under `docs/adr/`
8. `PRD.md` and `PDD.md` when a requirement or boundary needs clarification

If documents conflict, the workflow must stop and request clarification rather than silently choose one interpretation.

## Execution model

Slices are implemented sequentially.

```text
Slice N
  ↓
Planner
  ↓
Implementation
  ↓
Tests
  ↓
Review
  ↓
Fix loop (when required)
  ↓
Acceptance validation
  ↓
Slice approved
  ↓
Slice N+1
```

Parallel work is allowed only inside a slice when tasks are independent and do not create conflicting edits.

Slices themselves must not be implemented in parallel.

## Agent roles

### 1. Orchestrator

Responsibilities:

- identify the active slice;
- ensure required documentation is read;
- coordinate the remaining roles;
- prevent work outside the active slice;
- evaluate quality gates;
- decide whether to advance, retry, or stop;
- maintain a concise execution log.

The Orchestrator must not redefine scope.

### 2. Planner

Responsibilities:

- read the active slice specification;
- identify files and components to create or modify;
- identify dependencies and risks;
- produce an implementation plan limited to the active slice;
- map requirements to tests and acceptance criteria.

The Planner must not add speculative features.

### 3. Implementation Agent

Responsibilities:

- implement only the active slice;
- follow the existing architecture and ADRs;
- preserve deterministic business calculations outside the LLM;
- use typed contracts where specified;
- avoid premature implementation of later slices;
- keep changes small enough to review and test.

### 4. Test Agent

Responsibilities:

- run the tests required by the slice;
- add missing tests required by the slice specification;
- validate integration behavior;
- verify migration and database behavior where applicable;
- verify API behavior when the slice requires it;
- report exact failures.

The Test Agent must not hide failing tests or weaken assertions merely to make the suite pass.

### 5. Review Agent

Responsibilities:

Review the implementation against:

- slice scope;
- PDD / PRD requirements;
- SPEC;
- CTX;
- ADRs;
- security constraints;
- read-only ERP access;
- typed tools and contracts;
- deterministic calculations;
- repository conventions;
- unnecessary complexity;
- duplicated functionality;
- accidental implementation of later slices.

The Review Agent should classify findings as:

- blocker;
- major;
- minor;
- suggestion.

Only blocker and major findings prevent slice approval.

### 6. Fix Agent

Responsibilities:

- fix test failures;
- fix blocker and major review findings;
- preserve original scope;
- avoid unrelated refactors;
- re-run affected tests after every meaningful fix.

The Fix Agent must not resolve architectural uncertainty by inventing a new decision.

### 7. Acceptance Agent

Responsibilities:

- verify every acceptance criterion in the active slice;
- verify its Definition of Done;
- confirm required artifacts exist;
- confirm required validation commands pass;
- confirm no stop condition is active.

Only the Acceptance Agent may mark a slice as complete.

## Quality gates

A slice may advance only when all of the following are true:

```text
required tests pass
AND
slice acceptance criteria pass
AND
slice Definition of Done is satisfied
AND
no blocker review findings remain
AND
no major review findings remain
AND
no unapproved scope expansion exists
AND
no stop condition is active
```

If a gate fails, the workflow must enter a fix-and-retest loop.

## Stop conditions

The workflow must stop and request user confirmation when any of the following occurs:

1. a required architectural decision is not documented;
2. project documents materially contradict each other;
3. the requested implementation would change MVP scope;
4. a change to PDD, PRD, SPEC baseline, or ADR decision is required;
5. credentials, external services, or permissions are missing and cannot be safely bypassed;
6. a destructive operation outside the documented workflow is required;
7. a migration or reset could destroy data not clearly identified as synthetic/local;
8. tests continue failing after reasonable focused repair attempts;
9. the implementation would require adding a framework or major dependency not already approved;
10. the implementation requires modifying files outside the project repository;
11. a security-sensitive decision cannot be resolved from existing documentation;
12. a later slice would need to be implemented prematurely to finish the current one.

Warnings, cosmetic issues, or minor refactors are not stop conditions unless they block acceptance.

## Documents the workflow must not redefine automatically

The workflow must not autonomously change:

- project purpose;
- MVP domain scope;
- PDD;
- PRD;
- architectural principles;
- ERP-agnostic strategy;
- read-only policy;
- Agent vs Tool boundary;
- prohibition on free-form SQL generated by the LLM;
- Payroll boundary with PeopleOps AI;
- Accounting Lite boundary;
- post-MVP adapter strategy.

If any of these require a change, stop and ask for approval.

## Development environment rules

### Database

PostgreSQL is already available on:

```text
localhost:5435
```

Connection parameters are already defined in the project `.env`.

Agents must use the existing `.env` configuration and must not replace database credentials with hard-coded values.

Do not start a second PostgreSQL instance unless the active slice explicitly requires an isolated test database and the project documentation already permits it.

### Backend development mode

Normal backend development should run FastAPI locally, not require rebuilding the backend Docker image.

Use the project's documented local command, normally through the backend Makefile.

Docker remains available for reproducible/containerized validation, CI, demo, or deployment-oriented checks.

Do not run Docker image builds unless required by the active slice or explicitly requested.

### API test server

When API tests require a live FastAPI server:

1. try port `8000`;
2. if `8000` is already in use, choose the next available TCP port (`8001`, `8002`, and so on);
3. use the selected port consistently for that test run;
4. terminate the test server after validation.

Do not stop or interfere with unrelated services already running on the machine.

## Test discipline

Tests must be proportional to the slice.

Use the project's existing categories where applicable:

- unit;
- contract;
- integration;
- agentic;
- evaluation;
- end-to-end.

Business calculations must have deterministic tests.

Tool contracts must be testable without requiring the LLM whenever possible.

Agentic tests should validate routing, tool selection, structured outputs, state transitions, and supported claims rather than exact prose.

## Failure handling

When a command fails:

1. inspect the actual error;
2. identify whether the failure is implementation, environment, configuration, or dependency related;
3. fix only the relevant issue;
4. re-run the smallest meaningful validation;
5. run the complete slice validation before approval.

Do not repeatedly retry the same failing command without changing anything.

## Scope discipline

Every slice must leave the repository in a coherent, testable state.

Do not:

- implement future slices “while already in the area”;
- add unused abstractions;
- add frameworks for portfolio keywords;
- create free-form SQL access for the LLM;
- put deterministic calculations into prompts;
- infer causal relationships that are not supported by data;
- silently weaken tests;
- modify product-definition documents to match an implementation shortcut.

## Slice completion report

At the end of every slice, produce a concise report containing:

```text
Slice:
Status:
Implemented:
Tests executed:
Acceptance criteria:
Review findings:
Fixes applied:
Known limitations:
Files changed:
Next slice:
```

If the slice passes all gates, continue automatically to the next slice.

If a stop condition applies, stop after the report and request the minimum clarification necessary.

## Final workflow completion

The workflow is complete only when the final MVP slice passes its quality gates.

The final report must summarize:

- slices completed;
- test status;
- evaluation status;
- known limitations;
- unresolved non-blocking findings;
- commands required to run the application;
- any explicit follow-up items that belong to post-MVP work.

ERP adapters, the BIZAG Reference Adapter, MCP integration, and other post-MVP extensions must not be implemented by this workflow unless separately authorized.
