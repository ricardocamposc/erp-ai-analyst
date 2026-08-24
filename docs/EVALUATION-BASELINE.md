# ERP AI Analyst — Evaluation Baseline v1.0

## Purpose

Define the first reproducible evaluation baseline for ERP AI Analyst after implementation of the MVP slices.

This baseline measures the quality of agentic analytics over structured ERP data. It is not a RAG evaluation.

The baseline must allow future changes to prompts, routing, tool descriptions, tool selection, graph logic, or synthesis behavior to be compared objectively against a known reference.

## Scope

The baseline covers the six mandatory MVP domains:

- Sales
- Customers
- Inventory
- Purchases
- Payroll Analytics
- Accounting Lite

It must also cover cross-domain workflows, negative/guardrail scenarios, insufficient-data behavior, and controlled failure/resilience scenarios.

## Ground truth source

The source of truth is the synthetic ERP dataset already loaded in PostgreSQL.

Known current data coverage:

- Sales: 397 documents/lines
- Sales date range: 2025-01-01 to 2025-04-28
- Inventory: 47 movements, 16 balances
- Purchases: 16 purchase orders, 16 lines, 16 receipts
- Payroll: 12 summaries, 36 lines
- Accounting Lite: 4 periods, 12 balances
- Customers: 4
- Products: 4
- Suppliers: 2

Codex must inspect the actual database values before finalizing expected facts or expected calculations. It must not invent ground truth from assumptions.

## Baseline dataset location

Create or adapt the existing evaluation structure to contain:

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

If an equivalent structure already exists, preserve it instead of duplicating folders.

## Case schema

Each case should preserve information equivalent to:

```json
{
  "id": "EVAL-SALES-001",
  "question": "¿Cómo evolucionaron las ventas de abril de 2025 respecto a marzo de 2025?",
  "category": "single_domain",
  "domain": ["sales"],
  "difficulty": "easy",
  "expected_intent": ["sales_analysis"],
  "expected_tools": ["compare_sales_periods"],
  "allowed_tools": [],
  "forbidden_tools": [],
  "expected_key_facts": [],
  "expected_calculations": [],
  "expected_status": "completed",
  "expected_answer_characteristics": [],
  "notes": ""
}
```

Field names may adapt to the implementation, but the information content must remain.

## Baseline case groups

The baseline should contain exactly 36 cases.

### A. Single-domain cases — 18

Three per domain:

- Sales: period comparison, product contribution, trend/contribution analysis.
- Customers: customer contribution, reduced purchases, purchase history for a known synthetic customer.
- Inventory: April stockouts, stock history for a known product, low availability/stockout risk.
- Purchases: pending/partial POs, supplier delays, purchase-price evolution.
- Payroll: April vs March payroll, concept variance, cost-center variance.
- Accounting Lite: April vs March accounting, expense-group variance, gross margin/operating result.

### B. Cross-domain cases — 10

Include at least:

1. Sales decline vs inventory stockout.
2. Product sales decline vs pending purchase orders.
3. Supplier delay vs inbound supply vs stock availability.
4. Stockout-risk products with pending purchase orders.
5. Purchase cost increase vs gross-margin deterioration.
6. Payroll increase vs operating-expense increase.
7. Payroll cost-center variance vs accounting cost-center variance.
8. Customer sales decline with inventory context.
9. Supply-chain issue affecting a high-selling product.
10. A multi-step question requiring at least three domains.

At least one case must represent each synthetic chain:

```text
Supplier delay
→ Purchase order / receipt delay
→ Stockout
→ Sales decline
```

and:

```text
Payroll overtime increase
→ Payroll cost increase
→ Operating expenses increase
→ Accounting period variance
```

### C. Guardrail / negative cases — 6

Include:

- request to delete sales;
- arbitrary SQL such as DROP TABLE;
- individual employee salary/sensitive payroll detail;
- request to prove causality from correlation only;
- question outside implemented ERP domains;
- question requiring data outside the available date range.

### D. Failure / resilience cases — 2

Include controlled tool failure and invalid/insufficient tool arguments or simulated timeout, without unsafe database operations.

## Required metrics

Compute at least:

1. Tool selection accuracy
2. Calculation correctness
3. Key fact coverage
4. Unsupported quantitative claim rate
5. Unnecessary tool-call rate
6. Successful workflow rate
7. Guardrail success rate
8. Cross-domain success rate

Also record when available:

- latency;
- token usage;
- estimated cost;
- model-call count;
- tool-call count.

## Metric rules

- Tool selection: required tools must appear; explicitly forbidden tools must not. Optional valid tools must not reduce the score.
- Calculation correctness: compare deterministic numerical outputs against synthetic ERP ground truth.
- Key fact coverage: percentage of expected facts present in the response/structured output.
- Unsupported quantitative claim rate: quantitative claims not supported by tool results/evidence. Lower is better.
- Unnecessary tool-call rate: irrelevant calls that do not contribute to the answer. Lower is better.
- Successful workflow: correct termination, appropriate status, relevant tools/capabilities, no blocker error, scope respected.
- Guardrail success: safe handling of write/SQL/sensitive/out-of-scope cases.
- Cross-domain success: correct domain combination and synthesis of deterministic results.

## Output report

Each run must generate machine-readable JSON and human-readable Markdown under `backend/evaluation/runs/`, for example:

```text
baseline-v1.0-YYYYMMDD-HHMMSS.json
baseline-v1.0-YYYYMMDD-HHMMSS.md
```

Report at least:

```text
ERP AI Analyst — Evaluation Baseline v1.0

Total cases:
Passed:
Failed:

Tool selection accuracy:
Calculation correctness:
Key fact coverage:
Unsupported quantitative claim rate:
Unnecessary tool-call rate:
Successful workflow rate:
Guardrail success rate:
Cross-domain success rate:

Latency:
Token usage:
Estimated cost:

Failures by category:
Top regressions / issues:
```

Do not invent metric values.

## Regression policy

```text
Baseline v1.0
    ↓
change to prompt / routing / tools / graph / synthesis
    ↓
run evaluation
    ↓
compare metrics
    ↓
accept or reject change
```

## Acceptance criteria

Baseline v1.0 is complete when:

- 36 cases exist;
- expected facts/calculations are grounded in the actual synthetic ERP data;
- all six MVP domains are represented;
- cross-domain workflows are represented;
- guardrail and resilience cases are represented;
- the evaluator runs end-to-end;
- metrics are computed automatically;
- results are saved as JSON and Markdown;
- the current implementation is evaluated before tuning;
- failures are reported rather than hidden;
- `make test` passes;
- `make check` passes.

## Non-goals

Do not modify PDD/PRD, change MVP scope, add RAG, add ERP adapters/MCP, add a new framework only for evaluation, weaken tests to improve metrics, or tune prompts before capturing the initial baseline result.
