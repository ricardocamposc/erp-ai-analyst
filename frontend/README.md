# ERP AI Analyst frontend

Minimal Spanish-language chat UX for Slice 8. It is intentionally framework-free:
FastAPI serves `index.html` at `/` and the static assets at `/assets/`.

## Local usage

From the repository root, run the backend locally:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Then open <http://127.0.0.1:8000/>. The UI consumes only `POST /api/v1/analysis`.

## Tests

```bash
npm test
```

The UI keeps a client-side transcript for the active session, sends a stable
`conversation_id` for each turn, and supports reset/retry. Each assistant
message exposes the answer, key findings, tool provenance, warnings, structured
data as a table, and a lightweight chart when the API result contains suitable
numeric rows. It includes demo prompts for commercial, supply-chain,
payroll/accounting, and unsupported requests.
