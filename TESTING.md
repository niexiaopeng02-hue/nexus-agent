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
- `pytest -m "not integration"`: `31 passed, 2 deselected`.
- `pytest -m integration`: `3 skipped, 31 deselected` because `PGVECTOR_TEST_DATABASE_URL` was not configured locally.
- `PYTHONPATH=. python evals/run_eval.py`: 16 cases with intent, tool selection, citation, expected document, and no-context metrics at `1.0`.

## Integration Tests

Set a real pgvector test database:

```bash
set PGVECTOR_TEST_DATABASE_URL=postgresql+psycopg://nexus:nexus@localhost:5432/nexusagent_test
pytest -m integration
```

The integration suite covers migration apply, pgvector search, document/chunk insert, citation retrieval, conversation persistence, ticket persistence, tool log persistence, request metrics, and document delete cascade.

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
