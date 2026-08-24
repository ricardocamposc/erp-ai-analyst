# ERP AI Analyst — Test Strategy

## Test layers

1. **Unit** — pure domain calculations, period logic, contribution calculations, stockout logic, evidence builders.
2. **Contract** — typed tool inputs/outputs, validation, error normalization, result limits.
3. **Integration** — repositories + PostgreSQL + migrations + seeded scenarios.
4. **Agentic** — routing/tool-selection/workflow behavior with controlled model boundaries where possible.
5. **Evaluation regression** — end-to-end known questions against expected tools/facts/calculations/answer characteristics.

## Core rules

- Ground-truth calculations must be independent of production calculation code.
- Prefer deterministic tests for business math.
- LLM-based checks may supplement but not replace deterministic assertions.
- Every bug in business math/tool routing should add a regression test.
- Test failures caused by external model variability should be isolated from deterministic CI where practical.

## Minimum acceptance suite

- sales period totals and variance;
- product/customer contribution to decline;
- customer purchase decline;
- stockout windows and duration;
- cross-domain signature workflow;
- insufficient-data response;
- invalid tool arguments;
- tool timeout/failure behavior;
- graph iteration limit;
- unsupported quantitative claim detection in evaluation;
- request ID propagation.

## Mandatory MVP scope clarification

The MVP is complete only when **Sales, Customers, Inventory, Purchases, Payroll Analytics and Accounting Lite** are implemented, tested and represented in evaluation. Their implementation is incremental by slice, not optional. Payroll remains aggregated operational-financial analytics; Accounting Lite remains bounded analytical accounting. **Real ERP adapters, the BIZAG Reference Adapter and MCP are post-MVP improvements.**
