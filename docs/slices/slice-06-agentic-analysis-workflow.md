# Slice 6 — Agentic Analysis Workflow

## 1. Objective
Turn the deterministic tool layer into ERP AI Analyst by implementing bounded LangGraph orchestration with OpenAI structured interpretation/planning/tool selection, iterative investigation, evidence-aware synthesis and explicit failure/insufficient-data behavior.

## 2. Dependencies
Slices 0–5 accepted; tool contracts are stable.

## 3. Scope
- Define explicit LangGraph state.
- Implement structured intent/context extraction.
- Implement bounded planning and conditional routing.
- Execute only registered typed tools.
- Allow iterative analysis based on tool results within explicit iteration/retry limits.
- Implement structured answer synthesis using OpenAI without recalculating figures.
- Carry evidence, analysis-performed steps, warnings/errors and request ID through state.
- Distinguish facts, inferences, correlations and limitations in output.
- Handle insufficient data, unsupported domains/actions and controlled tool failures.
- Support the required single-request multi-step MVP questions; conversational follow-up only if explicitly needed by acceptance cases.

## 4. Out of scope
- LangSmith production tracing/evaluation dashboards (Slice 7).
- Final polished frontend (Slice 8).
- Real ERP adapters/MCP.
- Write operations, arbitrary NL-to-SQL or hidden chain-of-thought exposure.

## 5. Files and components affected
- `backend/app/agent/`
- graph nodes, state, routing and prompts
- OpenAI/model configuration integration
- final structured response schemas
- evidence assembly integration
- agentic/integration tests

## 6. Data / contracts
Agent state must minimally carry:
- request ID;
- user question;
- normalized intent/context;
- plan or remaining analysis steps;
- tool-call history;
- deterministic tool results;
- evidence items;
- warnings/errors;
- iteration count;
- final structured answer.

Final answer must separate at least:
- `answer`
- `key_findings`
- `evidence`
- `analysis_performed`
- `warnings`
- status/request metadata.

## 7. Implementation rules
- OpenAI may interpret, plan, select tools and synthesize; it must not calculate reproducible business metrics.
- LangGraph must be a real multi-step stateful workflow, not a wrapper around one model call.
- Cap tool/graph iterations and retries.
- Quantitative synthesis must preserve deterministic tool values.
- Do not expose private chain-of-thought; `analysis_performed` is a concise operational trace of tools/steps, not hidden reasoning.
- Correlation must not become unsupported causation.

## 8. Synthetic scenarios
Demonstrate end-to-end agentic analysis for:
- S1–S3 commercial signature scenario;
- S4 purchases→inventory→sales;
- S5 purchase-cost→gross-margin;
- S6 payroll→operating-expense/accounting variance;
- S8 unsupported/insufficient-evidence cases.

## 9. Required tests
- Intent/context structured-output tests.
- Routing/tool-selection tests.
- Multi-step workflow tests.
- Iteration/retry termination tests.
- Tool failure handling.
- Quantitative value preservation.
- Unsupported write/free-SQL/sensitive PeopleOps request handling.
- Correlation/causality language guard tests.

## 10. Acceptance criteria
1. Natural-language questions can trigger correct multi-step tool workflows.
2. Signature commercial question works end-to-end.
3. At least one supply-chain and one financial/payroll cross-domain question work end-to-end.
4. Final response is structured and evidence-linked.
5. Unsupported/insufficient cases terminate safely.
6. No model-generated free SQL or calculations are used.

## 11. Validation commands
Run agentic tests with deterministic/fake model boundaries where practical, selected live-model smoke tests only when credentials are intentionally available, plus full quality checks.

## 12. Deliverables
The first complete ERP AI Analyst agentic workflow over all mandatory MVP domains.

## 13. Definition of Done
The workflow can interpret, plan, route, call tools, iterate and synthesize grounded answers across the six-domain MVP within explicit safety/termination bounds.

## 14. Prohibitions
Do not add one agent per ERP module. Do not expose chain-of-thought. Do not move calculations into prompts or graph nodes.
