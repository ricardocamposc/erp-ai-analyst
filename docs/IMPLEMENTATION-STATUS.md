# ERP AI Analyst — Current Implementation Status

**Status:** Current reference for the implemented portfolio release
**Last reviewed:** 2026-08-26

## What is implemented

The project contains a six-domain synthetic ERP MVP and the local implementation of
Slice 10, Agentic Dynamic Query Execution. Slice 10 is the primary analytical path for
the dynamic API; the earlier static tools remain available for compatibility and
regression.

The implemented workflow is:

```text
Natural-language question
  → LangGraph coordinator
  → ERP metadata discovery
  → analyst agent generates candidate SQL
  → semantic review + deterministic AST guardrails
  → PostgreSQL EXPLAIN/read-only validation
  → bounded read-only execution
  → evidence-backed synthesis
```

The LLM does not receive unrestricted database access. Candidate SQL is an intermediate
artifact. Only a query that passes the catalog, AST, security, resource, PostgreSQL and
read-only checks can reach the executor.

## Agent responsibilities

- Coordinator: owns typed state, sequencing, retries and final API response.
- Analyst: interprets the business question and proposes tables, columns, joins, metrics,
  periods and candidate SQL.
- Validator: reviews semantic alignment and requests bounded corrections.
- Guardrails/executor: validate and execute only safe read-only SQL.
- Synthesizer: turns results and evidence into a grounded answer without inventing data.

## Dynamic tool contract

The provider exposes reusable capabilities for tables, columns, relationships, indexes,
row estimates, available periods, metrics, dimensions, data classification, SQL
validation, SQL explanation and read-only execution. A new question does not require a
new tool.

The local provider implements the contract against PostgreSQL. A future MCP provider may
implement the same operations, but MCP compatibility is not claimed until an external
provider is tested for authentication, schema equivalence, errors, limits and evidence.

## Implemented data scope

The canonical local model covers sales, customers, inventory, purchases, suppliers,
aggregate payroll and bounded Accounting Lite. Accounting Lite uses accounting periods and
aggregate account balances; it is not a complete accounting module. Payroll is aggregate by
period and cost center; there is no employee-level identity analysis. Sales documents are
not automatically fiscal invoices. Accounts Receivable, fiscal invoicing and real ERP
adapters are not implemented and remain future scope.

## Evidence

- Agentic Evaluation v2 official: 108 executions (36 cases × 3 repetitions).
- 84/84 analytical executions made OpenAI model calls.
- Official metrics: tool selection 1.0, calculations 1.0, workflow 1.0, guardrails 1.0,
  cross-domain 1.0 and key-fact coverage 0.9583.
- Official evidence:
  `backend/evaluation/runs/agentic-v2-official-20260824-223517.json` and its Markdown report.
- Token/cost metadata and detailed LangSmith delivery metrics are not currently exported
  by the evaluator.

## Temporal behavior

Relative periods use the runtime system date. Explicit months and years are respected.
Historical questions without an explicit date range use the available data rather than
an invented period. A relative period with no records is reported as no data and is not
silently replaced with the latest historical period.

## Product boundaries

The system is production-oriented within its local synthetic-data scope, not production-
ready. Authentication, deployment hardening, external ERP providers, MCP, write
operations, full receivables and individual PeopleOps analysis are not part of the current
release.
