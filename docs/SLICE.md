# ERP AI Analyst — Implementation Slices

## Purpose

This document is the master index for implementation slices. Detailed executable specifications live under `docs/slices/`.

Codex executes **one slice at a time**. Slices 0–9 belong to the mandatory MVP; Slice 10 is the implemented local evolution that changes the primary analytical path from a closed tool catalog to metadata-driven dynamic query execution.

The six-domain MVP is complete with **Sales + Customers + Inventory + Purchases + Payroll Analytics + Accounting Lite**. Slice 10 adds the implemented local dynamic-query foundation; full Accounts Receivable, real ERP adapters, the BIZAG Reference Adapter and the MCP provider remain later improvements.

## Slice sequence

| Slice | Name | Functional deliverable | Detailed specification | Status |
|---|---|---|---|---|
| 0 | Project Bootstrap | Reproducible Git/Python/FastAPI/PostgreSQL/Docker engineering baseline | `docs/slices/slice-00-project-bootstrap.md` | Accepted |
| 1 | Canonical ERP Foundation & Synthetic Business | Six-domain canonical ERP, migrations, deterministic synthetic data, scenarios and ground truth | `docs/slices/slice-01-canonical-foundation-synthetic-business.md` | Accepted |
| 2 | Commercial Analytics | Deterministic Sales + Customers + Inventory analytics and signature commercial chain | `docs/slices/slice-02-commercial-analytics.md` | Accepted |
| 3 | Supply Chain Analytics | Purchases plus Purchases → Inventory → Sales deterministic analysis | `docs/slices/slice-03-supply-chain-analytics.md` | Accepted |
| 4 | Financial & Payroll Analytics | Payroll Analytics + Accounting Lite plus financial cross-domain analysis | `docs/slices/slice-04-financial-payroll-analytics.md` | Accepted |
| 5 | Typed ERP Analytics Tools | Safe typed tool layer across all six MVP domains | `docs/slices/slice-05-typed-erp-analytics-tools.md` | Accepted |
| 6 | Agentic Analysis Workflow | LangGraph + OpenAI multi-step ERP analyst with evidence-aware synthesis | `docs/slices/slice-06-agentic-analysis-workflow.md` | Accepted |
| 7 | Evaluation & Observability | LangSmith, structured logging, evaluation dataset, regression metrics and failure scenarios | `docs/slices/slice-07-evaluation-observability.md` | Accepted |
| 8 | Application Experience | Stable FastAPI analysis API + minimal demo frontend/UX | `docs/slices/slice-08-application-experience.md` | Accepted |
| 9 | MVP Hardening & Portfolio Release | End-to-end hardening, release validation, documentation, evaluation evidence and demo assets | `docs/slices/slice-09-mvp-hardening-portfolio-release.md` | Accepted |
| 10 | Agentic Dynamic Query Execution | Metadata discovery, LLM-generated candidate SQL, validator agent, deterministic guardrails, read-only execution, audit and local ToolProvider | `docs/slices/slice-10-agentic-dynamic-query-execution.md` | Implemented |

## Dependency chain

```text
Slice 0 — Bootstrap
   ↓
Slice 1 — Canonical ERP + Synthetic Business
   ↓
Slice 2 — Commercial Analytics
   ↓
Slice 3 — Supply Chain Analytics
   ↓
Slice 4 — Financial & Payroll Analytics
   ↓
Slice 5 — Typed ERP Analytics Tools
   ↓
Slice 6 — Agentic Analysis Workflow
   ↓
Slice 7 — Evaluation & Observability
   ↓
Slice 8 — Application Experience
   ↓
Slice 9 — MVP Hardening & Portfolio Release
   ↓
Slice 10 — Agentic Dynamic Query Execution
```

## Why the slices are grouped this way

The slices are intentionally functional rather than module-fragmented:

- Slice 1 combines schema, migrations, synthetic data and ground truth so the first data milestone is a usable ERP rather than empty tables.
- Slice 2 combines Sales, Customers and Inventory because they form the signature commercial investigation.
- Slice 3 combines Purchases with existing Inventory/Sales analytics to produce a real supply-chain deliverable.
- Slice 4 combines Payroll Analytics and Accounting Lite because their primary value is financial cross-domain explanation.
- Slice 5 keeps the deterministic/tool boundary explicit before any LLM orchestration.
- Slice 6 groups LangGraph/OpenAI planning, routing, tool execution and synthesis because together they form the agentic product capability.
- Slice 7 combines evaluation and observability because together they provide evidence that the agentic system works and explain why it fails.
- Slice 8 groups API and minimal UX as the application-facing deliverable.
- Slice 9 is hardening/release only; it does not introduce missing mandatory domains.

## Execution rule for Codex

For each implementation request, Codex must read:

1. `AGENTS.md`
2. `docs/CTX.md`
3. `docs/SPEC.md`
4. `docs/REQ.md`
5. `docs/DATA.md`
6. `docs/PLAN.md`
7. this `docs/SLICE.md`
8. the **single active detailed slice file** under `docs/slices/`
9. relevant Accepted ADRs
10. `docs/TEST.md` and `docs/EVAL.md` as applicable

The active detailed slice file is the execution contract. Codex must stop at its boundary and report acceptance results before a later slice is authorized.

## Post-MVP work

After Slice 9 is accepted:

1. implement Slice 10 locally and complete its acceptance gates;
2. harden the canonical integration contract / adapter SDK;
3. implement a BIZAG Reference Adapter without proprietary artifacts;
4. add other ERP adapters where justified;
5. implement an MCP provider using Slice 10 contracts where it adds value;
6. expand Accounts Receivable if justified;
7. add further deployment, auth, scaling, telemetry or UX capabilities based on evidence.
