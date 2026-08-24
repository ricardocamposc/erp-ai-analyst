# Slice 9 — MVP Hardening & Portfolio Release

## 1. Objective
Turn the functionally complete six-domain application into a reproducible, technically defendable portfolio MVP with end-to-end validation, security/operational hardening appropriate to scope, final documentation, evaluation evidence and demo assets.

## 2. Dependencies
Slices 0–8 accepted.

## 3. Scope
- Run fresh-clone/extract setup and Docker validation from documented instructions.
- Complete end-to-end regression across all six domains and mandatory cross-domain scenarios.
- Fix defects required for MVP acceptance without adding unrelated features.
- Review read-only/security boundaries, environment handling, result/iteration/time limits and safe logging.
- Finalize README setup, architecture, use cases, example questions and demo steps.
- Ensure ADRs accurately reflect implemented decisions.
- Publish/document evaluation methodology and baseline results.
- Capture screenshots/demo artifacts.
- Document limitations, known risks, synthetic-data statement and roadmap.
- Add/verify license and repository hygiene.
- Confirm post-MVP roadmap starts with integration/adapters rather than unfinished mandatory domains.

## 4. Out of scope
- Real ERP adapters.
- BIZAG Reference Adapter.
- MCP integration server/client ecosystem.
- Full Accounts Receivable.
- Unplanned feature expansion, cloud-scale architecture or production-readiness claims without evidence.

## 5. Files and components affected
Potentially all existing files for defect fixes and documentation synchronization, especially:
- `README.md`
- architecture/docs/ADRs
- evaluation reports
- screenshots/demo assets
- Docker/env/setup docs
- tests and release checklist
- license/roadmap

## 6. Data / contracts
No new business-domain contracts should be introduced unless required to correct a defect. Freeze MVP public API/tool/evidence contracts and document any known limitations.

## 7. Implementation rules
- Prefer defect correction, simplification and documentation over new features.
- Do not label the project `production-ready`; describe it as production-oriented where supported.
- Public repository must contain only synthetic/public-safe data and no secrets/proprietary ERP material.
- Re-run evaluation after any fix that affects behavior.

## 8. Synthetic scenarios
All S1–S8 and representative domain questions must be part of final demo/regression evidence.

## 9. Required tests
- Full unit/contract/integration/agentic/evaluation suites.
- Fresh database migration/seed.
- Fresh Docker build/start/health/API checks.
- Frontend build/smoke tests.
- End-to-end signature scenarios.
- Negative/security boundary tests.
- Evaluation regression compared with accepted baseline thresholds.

## 10. Acceptance criteria
MVP is accepted only if:
1. Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite are implemented and tested.
2. Cross-domain commercial, supply-chain and financial/payroll scenarios work end-to-end.
3. Typed tools, LangGraph/OpenAI workflow, evidence, LangSmith and evaluation are present.
4. API/minimal UX is usable.
5. Fresh local setup via documentation/Docker succeeds.
6. Evaluation results and limitations are documented.
7. Repository is public-safe and reproducible.
8. Adapters/BIZAG/MCP remain clearly post-MVP.

## 11. Validation commands
Execute the complete documented release checklist: clean environment setup, Docker build/start, migrations/seed, all quality gates, all test classes, evaluation run, API/UI smoke and repository hygiene checks.

## 12. Deliverables
A portfolio-ready ERP AI Analyst MVP with reproducible execution, documented architecture and decisions, visible evaluation evidence, screenshots/demo, limitations and post-MVP integration roadmap.

## 13. Definition of Done
A third party can understand, run and evaluate the project from the repository, and a technical interviewer can inspect both deterministic and agentic evidence across all six mandatory MVP domains.

## 14. Prohibitions
Do not defer any mandatory MVP domain to adapters or future work. Do not add adapters/MCP to make the release appear broader. Do not claim production readiness beyond demonstrated evidence.
