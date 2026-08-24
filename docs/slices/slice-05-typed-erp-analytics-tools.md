# Slice 5 — Typed ERP Analytics Tools

## 1. Objective
Expose the validated deterministic analytics of all six MVP domains as a safe, typed, bounded tool layer suitable for LangGraph/OpenAI orchestration.

## 2. Dependencies
Slices 0–4 accepted; all deterministic domain capabilities are stable and tested.

## 3. Scope
- Define typed Pydantic request/response schemas for every MVP tool.
- Create tool registry/registration mechanism.
- Wrap domain services without moving calculations into tool wrappers.
- Validate arguments before execution.
- Enforce read-only behavior, result-size bounds, timeouts/error normalization where applicable.
- Standardize tool-result evidence/provenance primitives.
- Create contract tests for all tools.
- Document tool catalog, semantics and domain ownership.

## 4. Out of scope
- Natural-language planning.
- LangGraph state/routing.
- OpenAI calls.
- Final answer synthesis.
- LangSmith tracing except generic hooks/interfaces if required without live integration.

## 5. Files and components affected
- `backend/app/tools/`
- `backend/app/schemas/`
- `backend/app/evidence/` primitives
- contract tests under `tests/contract/`
- tool catalog documentation if maintained separately

## 6. Data / contracts
Tool catalog must represent all MVP domains:
- Sales
- Customers
- Inventory
- Purchases
- Payroll Analytics
- Accounting Lite

Each tool result should carry enough structured metadata to later support:
- numeric claim traceability;
- analysis-performed history;
- warnings/limitations;
- contributing business keys/periods/metrics.

## 7. Implementation rules
- Strict flow: `LLM → Typed Tool → Domain Service → Controlled Query` in later slices.
- Never expose arbitrary SQL or generic unrestricted query tools.
- Tools orchestrate/validate; services calculate.
- Tool names/descriptions must be precise enough for model selection but must not embed hidden business logic.
- Failures should be structured and safe for agent handling.

## 8. Synthetic scenarios
Use existing S1–S7 scenarios for contract-level executions across every domain. Include S8 attempts that must not map to prohibited write/sensitive tools because such tools do not exist.

## 9. Required tests
- Input validation.
- Output schema validation.
- Invalid enum/period/entity cases.
- Result limit behavior.
- Safe error normalization.
- Tool-to-service delegation.
- Evidence/provenance shape.
- Registry completeness across all six domains.
- Negative assertion that no write/free-SQL tools are registered.

## 10. Acceptance criteria
1. Every MVP analytical capability needed by acceptance questions is available through a typed tool.
2. Tool contracts are validated and documented.
3. No business calculation is duplicated in tool wrappers.
4. No free-form SQL or write tool exists.
5. Contract tests pass against the synthetic ERP.

## 11. Validation commands
Run all contract tests, selected integration tests and the full quality suite.

## 12. Deliverables
A complete, safe ERP Analytics Tool Layer that can be orchestrated independently of any specific LLM implementation.

## 13. Definition of Done
All six domain tool contracts are stable, tested, bounded and evidence-capable, with no agentic orchestration implemented yet.

## 14. Prohibitions
Do not let the model-facing layer bypass services/repositories. Do not create a generic SQL tool or module-per-agent architecture.
