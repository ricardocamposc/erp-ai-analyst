# ERP AI Analyst — Implementation Plan

## MVP Definition

There is one MVP. It includes **Sales + Customers + Inventory + Purchases + Payroll Analytics + Accounting Lite**. The implementation is incremental for risk control, but none of these six domains is optional for MVP Definition of Done.

The detailed implementation contracts are maintained in `docs/slices/`. `docs/SLICE.md` is the master index and status map.

## Phase / Slice 0 — Project Bootstrap
Initialize Git on `main` when needed; create the exact repository structure; configure Python; FastAPI `/health`; settings; `backend/Dockerfile`; `backend/docker-compose.yml` with `api` + PostgreSQL `db`; `backend/Makefile`; separate `backend/` and `frontend/`; DB healthcheck, named volume and internal network; migration scaffold; pytest/lint/format/type-check gates. No ERP business implementation yet.

## Phase / Slice 1 — Canonical ERP Foundation & Synthetic Business
Implement the complete six-domain MVP canonical schema, migrations, repository/data foundations, deterministic synthetic generator, S1–S8 scenarios, ground truth and data-quality checks. End with a reproducible populated ERP, not merely empty tables.

## Phase / Slice 2 — Commercial Analytics
Implement deterministic Sales + Customers + Inventory services and tests, including the signature chain:
`sales decline → product/customer contribution → inventory/stockout inspection`.

## Phase / Slice 3 — Supply Chain Analytics
Implement Purchases/Procurement services and deterministic Purchases → Inventory → Sales analysis, including supplier delivery, PO/receipt status, purchase-cost history and inbound supply.

## Phase / Slice 4 — Financial & Payroll Analytics
Implement aggregated Payroll Analytics and bounded Accounting Lite services plus payroll → operating-expense/accounting variance and purchase-cost → gross-margin cross-domain calculations.

## Phase / Slice 5 — Typed ERP Analytics Tools
Expose all six domains through validated, registered, bounded typed tool contracts. Preserve the architectural boundary `LLM → Typed Tool → Domain Service → Controlled Query`. Establish evidence-capable tool results. No agentic orchestration yet.

## Phase / Slice 6 — Agentic Analysis Workflow
Implement LangGraph state, structured intent/context, planning, conditional routing, bounded tool execution/iteration, OpenAI structured outputs/tool use, evidence-aware synthesis, insufficient-data handling and safe failure behavior.

## Phase / Slice 7 — Evaluation & Observability
Add request IDs, structured logs, LangSmith tracing and the reproducible evaluation/regression suite across all six domains, cross-domain scenarios, negative cases and tool failures. Store/document baseline metrics.

## Phase / Slice 8 — Application Experience
Stabilize the FastAPI analysis API and implement the minimal frontend/demo UX for question, answer, findings, evidence, analysis performed, warnings and useful table/chart presentation.

## Phase / Slice 9 — MVP Hardening & Portfolio Release
Run fresh-clone/Docker validation, complete E2E regression, harden MVP boundaries, finalize README/architecture/ADRs/demo/evaluation results/screenshots/security/limitations/license/roadmap and verify public-safe repository quality.

## Post-MVP improvements

After the six-domain MVP is complete:

1. **Slice 10 — Agentic Dynamic Query Execution:** metadata discovery, LLM-generated candidate SQL, validator agent, deterministic guardrails, read-only executor, audit and local `ToolProvider`.
2. ERP integration contract hardening and adapter SDK.
3. BIZAG Reference Adapter.
4. Other ERP adapters.
5. MCP provider/server using the Slice 10 tool contracts.
6. Accounts Receivable expansion if justified.
7. Further deployment, scale, auth, telemetry or UX enhancements backed by evidence.
