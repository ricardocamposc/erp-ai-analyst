# Slice 7 — Evaluation & Observability

## 1. Objective
Make ERP AI Analyst measurable and diagnosable by adding LangSmith tracing, structured application logging, a reproducible evaluation dataset/runner, regression metrics and failure/negative scenarios across the entire six-domain MVP.

## 2. Dependencies
Slices 0–6 accepted; end-to-end workflow exists.

## 3. Scope
### Observability
- request/execution IDs propagated through API/workflow/tools where applicable;
- structured logs for major execution events and safe errors;
- LangSmith traces for model calls, plan/routing, tool calls/arguments/results, errors, latency and final answer;
- environment-controlled observability configuration.

### Evaluation
- implement versioned evaluation dataset under `evaluation/` using the agreed schema;
- create `scripts/run_evaluation.py` or equivalent;
- cover single-domain, cross-domain, negative, insufficient-data and tool-failure cases;
- compute/report candidate metrics from PRD such as tool-selection accuracy, calculation correctness, key-fact coverage, unsupported quantitative claim rate, unnecessary tool-call rate, successful workflow rate, latency and token/cost metrics where available;
- create reproducible regression output/report artifacts.

## 4. Out of scope
- Phoenix or duplicate tracing stack.
- Production monitoring infrastructure.
- UI polishing unrelated to showing evaluation/trace evidence.
- Real ERP integration evaluation.

## 5. Files and components affected
- `backend/app/observability/`
- LangSmith integration points
- structured logging configuration
- `evaluation/`
- `scripts/run_evaluation.py`
- `tests/evaluation/`
- evaluation result/report artifacts as appropriate

## 6. Data / contracts
Evaluation records should support fields equivalent to:
- question
- expected_intent
- expected_tools
- expected_key_facts
- expected_calculations
- expected_answer_characteristics
- difficulty
- category

Ground truth from `data/ground_truth/` remains authoritative for deterministic facts/calculations.

## 7. Implementation rules
- Evaluation is part of the product evidence, not a demo afterthought.
- Avoid evaluating calculations with the same function that produced them.
- Separate deterministic correctness from model-assisted qualitative evaluation.
- LangSmith data/logging must not include secrets.
- Phoenix remains explicitly excluded unless a future ADR changes that decision.

## 8. Synthetic scenarios
Evaluation coverage must include all mandatory cross-domain scenarios S1–S8 and representative questions from all six MVP domains.

## 9. Required tests
- trace/log configuration behavior with observability on/off;
- request-ID propagation;
- evaluation dataset schema validation;
- evaluator metric correctness for deterministic metrics;
- regression runner success/failure behavior;
- negative/failure injection cases;
- checks for unsupported quantitative claims/unnecessary tool calls where feasible.

## 10. Acceptance criteria
1. A complete evaluation run can be executed reproducibly.
2. All six MVP domains are represented.
3. Cross-domain scenarios and negative/failure cases are represented.
4. LangSmith traces expose the required workflow/tool/model events.
5. Structured logs include request IDs and safe error context.
6. Baseline evaluation results are stored/documented.

## 11. Validation commands
Run evaluation schema checks, targeted observability tests, full evaluation command, full test suite and quality gates. If live model evaluation is credential-dependent, provide a deterministic/offline test path and a documented live path.

## 12. Deliverables
A measurable, observable ERP AI Analyst with regression evidence suitable for technical review and portfolio demonstration.

## 13. Definition of Done
A reviewer can run the evaluation suite, inspect metrics and traces, and diagnose at least the required success/failure workflows without Phoenix or duplicate observability tooling.

## 14. Prohibitions
Do not hide poor results by removing difficult cases. Do not log secrets or sensitive real data. Do not make evaluation depend exclusively on an unavailable external judge.
