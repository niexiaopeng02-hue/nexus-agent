# Testing

## Local Results

Latest local verification:

- `ruff check .`: passed.
- `pytest -m "not integration"`: `34 passed, 5 deselected`.
- `pytest -m integration`: `5 skipped, 34 deselected` because `PGVECTOR_TEST_DATABASE_URL` was not configured locally.
- `PYTHONPATH=. python evals/run_eval.py`: passed with 16 deterministic evaluation cases and key metrics at `1.0`.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `python scripts/smoke_test.py`: passed against a local SQLite-backed FastAPI runtime.

Local Docker verification was not completed because Docker is not installed or not available on PATH in the local environment used for this audit.

## GitHub Actions CI Results

Latest verified CI status: passed on `main` after commit `c1b6628`.

Verified in GitHub Actions CI:

- Backend lint passed.
- Backend unit tests passed.
- PostgreSQL + pgvector integration tests passed.
- Fresh Alembic migration test passed.
- `0001` to `head` migration test passed.
- pgvector extension verification passed.
- Vector similarity retrieval test passed.
- Threshold filtering test passed.
- Document and chunk persistence tests passed.
- Conversation persistence tests passed.
- Ticket, handoff, tool log, and request metric persistence tests passed.
- Document delete cascade test passed.
- Evaluation pipeline passed.
- Frontend typecheck passed.
- Frontend production build passed.

## Backend Commands

```bash
cd backend
ruff check .
pytest -m "not integration"
pytest -m integration
PYTHONPATH=. python evals/run_eval.py
```

## Integration Tests

Set a real pgvector test database:

```bash
set PGVECTOR_TEST_DATABASE_URL=postgresql+psycopg://nexus:nexus@localhost:5432/nexusagent_test
pytest -m integration
```

The integration suite covers migration apply, 0001 to head upgrade behavior, pgvector extension, vector dimension checks, wrong-dimension rejection, pgvector search, threshold filtering, document/chunk insert, citation retrieval, conversation persistence, message persistence, ticket persistence, handoff persistence, customer email persistence, conversation id persistence, success/failed tool logs, request metrics, and document delete cascade.

These integration tests are verified in GitHub Actions CI with the `pgvector/pgvector:pg16` service container. They are skipped locally unless `PGVECTOR_TEST_DATABASE_URL` is configured.

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
