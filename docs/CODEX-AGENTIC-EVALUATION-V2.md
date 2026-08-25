# Codex Execution Prompt — Agentic Evaluation v2

Read `AGENTS.md`, `docs/AGENTIC-EVALUATION-V2.md`, `docs/EVALUATION-BASELINE.md`, `docs/EVAL.md`, and the current evaluation implementation before changing code.

Run the smoke evaluation first:

```text
cd backend
python evaluation/run_agentic_evaluation.py --mode smoke
```

Confirm that analytical cases use OpenAI + LangGraph and that LangSmith tracing is enabled. If any analytical case has zero model calls, stop and diagnose the gateway/evaluator path; do not report the run as Agentic v2.

After smoke succeeds, run the official protocol:

```text
python evaluation/run_agentic_evaluation.py --mode official
```

The official protocol is 36 cases × 3 executions = 108 executions. Preserve the frozen ground truth and report the generated JSON and Markdown files, metrics, failures, model/tool call counts, and any provider or tracing limitations. Do not tune prompts or expected facts merely to improve the score.
