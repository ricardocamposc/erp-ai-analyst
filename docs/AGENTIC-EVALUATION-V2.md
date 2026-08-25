# ERP AI Analyst — Agentic Evaluation v2

Agentic Evaluation v2 measures the same 36-case ground truth used by the offline baseline, but executes analytical cases through `OpenAIGateway` and the bounded LangGraph workflow. Registered ERP tools remain deterministic. LangSmith tracing is enabled through the repository environment.

## Execution protocol

1. Smoke: 36 cases, one execution each, to validate OpenAI credentials, LangGraph execution, tool calls and LangSmith configuration.
2. Official: 36 cases, three executions each (108 executions) to measure repeatability and non-determinism.

The evaluator aborts if any answerable single-domain or cross-domain case reports zero OpenAI model calls. Guardrail refusals may terminate deterministically because they are specifically testing the safe boundary, not model reasoning.

## Ground truth

The dataset remains `backend/evaluation/cases.jsonl` and the expected deterministic facts remain `backend/evaluation/expected/ground-truth-v1.json`. This keeps the comparison with Offline Baseline v1.2 direct and prevents changing expected answers to fit the model.

## Commands

From `backend/`:

```bash
python evaluation/run_agentic_evaluation.py --mode smoke
python evaluation/run_agentic_evaluation.py --mode official
```

Reports are written to `backend/evaluation/runs/` as JSON and Markdown. The latest JSON is also written to `backend/evaluation/results/latest-agentic-v2.json`.

## Metrics

The runner records tool selection, calculation correctness, key-fact coverage, unsupported quantitative claims, unnecessary tool calls, workflow success, guardrail success and cross-domain success. Key-fact coverage checks the answer, structured tool data and evidence, with normalized field names and documented bilingual aliases. Operational data includes latency, model calls and tool calls. Token/cost fields remain `null` unless the gateway exposes provider usage metadata.

## Interpretation

The v2 score is evidence about the complete agentic path, not only the deterministic business logic. A regression may come from interpretation, planning, tool selection, synthesis, grounding or workflow termination. The offline baseline remains the deterministic correctness reference.
