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

The offline evaluation contains eight cases spanning all six domains, S1–S8,
positive workflows and safe refusals. The generated report is
`backend/evaluation/results/latest.json`. Deterministic calculations are
tested independently of the evaluation runner.

## Security and scope review

- Only registered typed tools can execute.
- No write, arbitrary SQL, ERP adapter, BIZAG or MCP capability is registered.
- `.env` and credentials are ignored and never committed.
- Payroll is aggregate-only; Accounting Lite is read-only and aggregate.
- Correlation is labelled as observation, not unsupported causation.

