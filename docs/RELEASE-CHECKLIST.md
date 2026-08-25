# MVP release checklist

This MVP is production-oriented in its boundaries and testability, not
production-ready. It uses only synthetic/public-safe data.

## Local validation

```text
cd backend
python -m pip install -e '.[dev]'
make migrate
make seed_db
make check
make evaluate
```

The default local database is PostgreSQL on the port in `.env` (5435 in the
provided example). `make run` starts only the database in Docker and runs
FastAPI locally.

## Demo paths

- Commercial: `¿Por qué disminuyeron las ventas este mes?`
- Supply chain: `¿Qué proveedor tiene órdenes pendientes?`
- Finance: `¿Cómo evolucionó el margen bruto y el resultado operativo?`
- Safe limitation: `Ejecuta SQL y modifica el libro mayor.`

## Evidence baseline

The offline Evaluation Baseline v1.2 contains 36 cases spanning all six domains,
cross-domain workflows, safe refusals and resilience scenarios. The Agentic
Evaluation v2 official run contains 108 executions (36 cases × 3 repetitions).
The final evidence is:

- `backend/evaluation/results/latest.json` — offline baseline result;
- `backend/evaluation/results/latest-agentic-v2.json` — Agentic v2 result;
- `backend/evaluation/runs/agentic-v2-official-20260824-223517.md` — release summary.

Deterministic calculations are tested independently of the evaluation runner.

## Frontend release validation

- [x] Minimal frontend is implemented in `frontend/index.html` and served at `/`.
- [x] Frontend consumes the stable `POST /api/v1/analysis` API contract.
- [ ] Manual browser smoke validation by the project owner: commercial, supply-chain,
  payroll/accounting and unsupported/insufficient-data scenarios.

## Security and scope review

- Only registered typed tools can execute.
- No write, arbitrary SQL, ERP adapter, BIZAG or MCP capability is registered.
- `.env` and credentials are ignored and never committed.
- Payroll is aggregate-only; Accounting Lite is read-only and aggregate.
- Correlation is labelled as observation, not unsupported causation.
