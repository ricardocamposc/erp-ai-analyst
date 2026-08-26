# ERP AI Analyst — Portfolio Release Report

The six-domain MVP is functionally complete and has a documented Agentic
Evaluation v2 result. The project is production-oriented within its local,
synthetic-data scope; it is not presented as production-ready.

## Validation evidence

- Backend quality gates: 65 tests passed; Ruff and mypy passed.
- Offline Baseline v1.2: 36 cases; tool selection, calculations, key-fact coverage,
  workflow, guardrails and cross-domain success at 1.0; unsupported quantitative
  claims at 0.0; unnecessary tool-call rate at 0.1111.
- Agentic Evaluation v2 official: 108 executions (36 cases × 3 repetitions),
  84/84 analytical executions with OpenAI model calls.
- Agentic v2 metrics: tool selection 1.0; calculations 1.0; key-fact coverage
  0.9583; workflow 1.0; guardrails 1.0; cross-domain 1.0.
- Agentic v2 operations: 294 model calls, 240 tool calls, 6922.616 ms average
  latency.
- Official evidence: `backend/evaluation/runs/agentic-v2-official-20260824-223517.json`
  and its Markdown report.
- PostgreSQL: healthy in Docker on host port 5435.
- FastAPI: `/health` and `POST /api/v1/analysis` are covered by the backend API tests.
- Frontend: the demo UI is implemented and served by FastAPI from
  `frontend/index.html`; it consumes the dynamic-analysis API and presents result
  sets as tables with an optional technical-evidence accordion.
- OpenAI and LangSmith: configured through environment settings; the Agentic v2
  run confirmed OpenAI calls through `OpenAIGateway` and the LangGraph workflow.

## Known limitations and boundaries

The release remains a local, synthetic-data MVP. Authentication, production deployment,
real ERP adapters, BIZAG, MCP provider, write operations, and individual-level
PeopleOps analysis remain intentionally out of scope. Slice 10 is implemented locally
and is the current dynamic-query path; external providers and full receivables remain
future work.

Token usage and estimated cost are not exposed by the current gateway. LangSmith is
configured, but the evaluator does not currently export trace-level delivery or query
metrics. Agentic v2 recorded a 0.2481 unsupported-quantitative-claim rate and a 0.1111
unnecessary-tool-call rate; these are documented limitations for future hardening.

The remaining Agentic v2 key-fact coverage gap (0.9583) is limited to the two guardrail
cases `EVAL-GUARD-004` and `EVAL-GUARD-006`; workflow, calculations, guardrails and
cross-domain success remained 1.0.

The two test warnings are upstream deprecation warnings from LangGraph cache defaults
and Starlette's TestClient/httpx integration; they do not fail the gates.
