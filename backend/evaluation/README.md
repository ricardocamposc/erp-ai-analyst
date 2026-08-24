# Evaluation Baseline v1.0

`cases.jsonl` contains the reproducible 36-case baseline. The runner uses the
deterministic `RuleBasedGateway` and the PostgreSQL data configured in
`backend/.env`; it never calls OpenAI and never mutates the database.

Run from `backend/`:

```bash
python scripts/run_evaluation.py
```

Machine-readable and Markdown reports are written to `evaluation/runs/`.
`evaluation/expected/ground-truth-v1.json` records the inspected database
coverage and exact facts used by the cases.
