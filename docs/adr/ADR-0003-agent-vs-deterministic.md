# ADR-0003 — Agentic Reasoning vs Deterministic Services

**Status:** Accepted

## Decision
Use LLM/agentic logic for interpretation, planning, routing, selecting tools, deciding whether additional analysis is needed, synthesis, and explanation.

Use deterministic code for queries, aggregations, comparisons, rankings, variations, stockouts, lead times, payroll totals, account balances, margins, persistence, and validation when those domains exist.

## Consequences
The graph orchestrates; it does not become the business-calculation engine. Domain services must be independently testable without an LLM.
