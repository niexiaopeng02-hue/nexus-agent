# Testing

## Backend Commands

```bash
cd backend
ruff check .
pytest -m "not integration"
pytest -m integration
PYTHONPATH=. python evals/run_eval.py
```

Latest local results:

- `ruff check .`: passed.
- `pytest -m "not integration"`: `34 passed, 5 deselected`.
- `pytest -m integration`: `5 skipped, 34 deselected` because `PGVECTOR_TEST_DATABASE_URL` was not configured locally.
- `PYTHONPATH=. python evals/run_eval.py`: 16 cases with intent, tool selection, citation, expected document, and no-context metrics at `1.0`.

## Integration Tests

Set a real pgvector test database:

```bash
set PGVECTOR_TEST_DATABASE_URL=postgresql+psycopg://nexus:nexus@localhost:5432/nexusagent_test
pytest -m integration
```

The integration suite covers migration apply, 0001 to head upgrade behavior, pgvector extension, vector dimension checks, wrong-dimension rejection, pgvector search, threshold filtering, document/chunk insert, citation retrieval, conversation persistence, message persistence, ticket persistence, handoff persistence, customer email persistence, conversation id persistence, success/failed tool logs, request metrics, and document delete cascade.

## Smoke Test

```bash
python scripts/smoke_test.py
```

Latest local result: passed against a local SQLite-backed FastAPI runtime. Set `NEXUS_API_BASE_URL` for Docker or deployed environments.

## Frontend Commands

```bash
cd frontend
npm ci
npm run typecheck
npm run build
```

Latest local results: all passed.

## Docker

```bash
docker compose config
docker compose up --build
```

Both commands were attempted locally but could not run because `docker` is not installed or not available on PATH. Docker configuration was updated statically with a pgvector service healthcheck, backend dependency condition, and Nginx `/api/` proxy.
