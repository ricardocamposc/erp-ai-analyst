# Codex Prompt — Generate ERP AI Analyst Evaluation Baseline v1.0

Implement and execute the first reproducible evaluation baseline for ERP AI Analyst.

## Read first

Read:

- `AGENTS.md`
- `docs/WORKFLOW.md` if present
- `docs/CTX.md`
- `docs/SPEC.md`
- `docs/PLAN.md`
- `docs/SLICE.md`
- applicable ADRs
- `PDD.md`
- `PRD.md`
- `docs/EVALUATION-BASELINE.md`

Repository documentation is authoritative.

## Goal

Create and execute Evaluation Baseline v1.0 for the current MVP implementation.

The baseline must contain exactly 36 cases covering Sales, Customers, Inventory, Purchases, Payroll Analytics, Accounting Lite, cross-domain workflows, guardrails/negative cases, and resilience/failure cases.

## Ground truth

PostgreSQL is already running on port `5435`. Connection parameters are in `.env`.

Before finalizing expected facts/calculations:

1. inspect the actual synthetic ERP data;
2. determine exact values for the known scenarios;
3. use those exact values as ground truth;
4. do not invent expected numbers.

Known current coverage:

- sales date range: 2025-01-01 to 2025-04-28;
- 397 sales documents/lines;
- 47 inventory movements;
- 16 inventory balances;
- 16 purchase orders;
- 16 purchase lines;
- 16 receipts;
- 12 payroll summaries;
- 36 payroll lines;
- 4 accounting periods;
- 12 accounting balances;
- 4 customers;
- 4 products;
- 2 suppliers.

Use the real database as authoritative if counts differ.

## Files

Prefer the existing evaluation structure. If no equivalent exists, create:

```text
backend/evaluation/
├── dataset/
│   └── baseline-v1.jsonl
├── expected/
│   └── ground-truth-v1.json
├── runs/
│   └── .gitkeep
├── scripts/
│   └── run_baseline.py
└── README.md
```

Do not duplicate existing evaluation directories.

## Case distribution

Create exactly 36 cases:

- 18 single-domain: 3 each for Sales, Customers, Inventory, Purchases, Payroll, Accounting Lite;
- 10 cross-domain;
- 6 guardrail/negative;
- 2 failure/resilience.

Use `docs/EVALUATION-BASELINE.md` for the detailed categories and intended scenarios.

## Metrics

Compute automatically:

- tool selection accuracy;
- calculation correctness;
- key fact coverage;
- unsupported quantitative claim rate;
- unnecessary tool-call rate;
- successful workflow rate;
- guardrail success rate;
- cross-domain success rate.

Also record when available latency, token usage, estimated cost, model-call count, and tool-call count.

Do not use exact prose matching. Evaluate behavior using selected tools, structured deterministic results, expected facts, evidence, supported/unsupported quantitative claims, appropriate status, and scope/guardrail compliance.

## Critical baseline rule

Do not tune prompts, routing, tool descriptions, graph behavior, or synthesis before capturing the first baseline result, unless the evaluator itself cannot run.

The purpose of v1.0 is to measure the current implementation honestly.

If cases fail, record and report them. Do not hide failures or change architecture merely to improve the first score.

After the initial baseline result is saved, identify recommended fixes but do not implement them unless needed for the evaluator itself.

## Local execution

PostgreSQL uses port `5435` and the existing `.env`.

Do not start another PostgreSQL instance unnecessarily.

If a live FastAPI server is required:

1. use `8000` if available;
2. otherwise probe `8001`, `8002`, etc.;
3. do not terminate unrelated processes;
4. stop only the server started for this evaluation.

Prefer local FastAPI execution.

Do not run `docker compose build`, `docker compose up --build`, or `make run_docker` unless explicitly required by the existing evaluator implementation.

## Validation

After implementation:

1. run the evaluation suite;
2. save machine-readable JSON results;
3. save human-readable Markdown results;
4. run `make test`;
5. run `make check`.

Do not mark complete if the evaluator fails to run.

## Completion report

Report:

```text
Evaluation Baseline v1.0

Dataset:
- total cases:
- single-domain:
- cross-domain:
- guardrail:
- resilience:

Metrics:
- tool selection accuracy:
- calculation correctness:
- key fact coverage:
- unsupported quantitative claim rate:
- unnecessary tool-call rate:
- successful workflow rate:
- guardrail success rate:
- cross-domain success rate:

Operational:
- average latency:
- token usage:
- estimated cost:

Failures:
- ...

Files created/modified:
- ...

Validation:
- make test:
- make check:

Recommendations:
- ...
```

## Stop conditions

Stop and ask for confirmation only if documents materially conflict, a new architectural decision is required, evaluation requires a new major framework, database operations risk non-synthetic data, required OpenAI/LangSmith credentials are missing, or the evaluator cannot run after reasonable focused fixes.

Do not modify PDD, PRD, accepted ADRs, MVP scope, or adapter strategy. Do not add RAG, MCP, ERP adapters, or unrelated technologies.
