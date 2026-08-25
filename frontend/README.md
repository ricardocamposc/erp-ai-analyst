# ERP AI Analyst frontend

Minimal Spanish-language chat UX for Slice 10. It is intentionally framework-free:
FastAPI serves `index.html` at `/` and the static assets at `/assets/`.

## Local usage

From the repository root, run the backend locally:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Then open <http://127.0.0.1:8000/>. The UI consumes `POST /api/v1/dynamic-analysis`,
the guarded agentic SQL workflow introduced by Slice 10.

## Tests

```bash
npm test
```

The UI keeps a client-side transcript for the active session, sends a stable
`conversation_id` for each turn, and supports reset/retry. Each assistant
message exposes the answer, key findings, tool provenance, warnings, structured
data as a table, a lightweight chart when the API result contains suitable
numeric rows, and the dynamic query trace (validated SQL, guardrail status,
row count and SQL hash). It includes demo prompts for commercial, supply-chain,
payroll/accounting, and unsupported requests.
