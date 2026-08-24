# ADR-0002 — No LLM-Generated Free-Form SQL

**Status:** Accepted

## Context
Direct natural-language-to-SQL would increase security, correctness, schema-coupling, and evaluation risk and would weaken the project's typed-tool architecture.

## Decision
The execution path is:

```text
LLM -> Typed Tool -> Domain Service -> Controlled/Parameterized Query -> PostgreSQL
```

The LLM may select tools and provide validated arguments but may not submit arbitrary SQL for execution.

## Consequences
- Smaller attack/error surface.
- Business calculations remain testable.
- Tool catalog must intentionally expose supported analytical capabilities.
- Unsupported questions are limited/rejected rather than solved with arbitrary SQL.
