# ERP AI Analyst — Evaluation Design

## 1. Evaluation record

Each JSONL case should contain:

```json
{
  "id": "core-001",
  "question": "Why did sales decline this month?",
  "expected_intent": "sales_variance_analysis",
  "expected_tools": [],
  "expected_key_facts": [],
  "expected_calculations": {},
  "expected_answer_characteristics": [],
  "difficulty": "multi_step",
  "category": "cross_domain"
}
```

Exact tool names/arguments should be added after tool schemas are frozen.

## 2. Required categories

- simple Sales;
- simple Customers;
- simple Inventory;
- multi-step Sales → Product/Customer;
- cross-domain Sales → Inventory;
- insufficient data/out-of-scope;
- tool failure;
- ambiguous period/entity;
- unnecessary-tool trap.

## 3. Metrics

From PRD baseline:
- tool selection accuracy;
- calculation correctness;
- key fact coverage;
- unsupported quantitative claim rate;
- unnecessary tool-call rate;
- successful workflow rate;
- latency;
- token/cost metrics when available.

## 4. Evaluation principles

- Deterministic calculations are checked programmatically.
- Tool selection can allow acceptable alternative plans when they reach the same evidence efficiently; document equivalence rules.
- Quantitative claims must map to evidence/tool results.
- A correct refusal/limitation is success for unanswerable/out-of-scope cases.
- Model-assisted grading, if used, is supplementary and must have a documented rubric.

## 5. Release evidence

Portfolio release should publish a concise evaluation report containing dataset size/categories, configuration, metric definitions, results, known failure modes, and architectural changes made because of evaluation findings.

## Mandatory MVP scope clarification

The MVP is complete only when **Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite** are implemented, tested and represented in evaluation. Their implementation is incremental by slice, not optional. Payroll remains aggregated operational-financial analytics; Accounting Lite remains bounded analytical accounting. **Real ERP adapters, the BIZAG Reference Adapter and MCP are post-MVP improvements.**
