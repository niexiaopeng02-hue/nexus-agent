# Testing

## Backend

```bash
cd backend
pip install -r requirements.txt
pytest
ruff check .
PYTHONPATH=. python evals/run_eval.py
```

Coverage focuses on health checks, intent routing, order tool, inventory tool, product search, ticket creation, handoff creation, RAG citations, no-context refusal behavior, upload validation, chat API, documents API, tickets API, and analytics.

Latest local result: `25 passed, 2 skipped`. The skipped tests require `PGVECTOR_TEST_DATABASE_URL`.

## PostgreSQL + pgvector Integration

```bash
cd backend
set PGVECTOR_TEST_DATABASE_URL=postgresql+psycopg://nexus:nexus@localhost:5432/nexusagent_test
pytest -m integration
```

CI starts a `pgvector/pgvector:pg16` service and sets `PGVECTOR_TEST_DATABASE_URL`.

## Frontend

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

## Docker

```bash
docker compose up --build
```

Docker uses `pgvector/pgvector:pg16` for the database and runs the backend in mock-provider mode by default.

Local Docker runtime verification was not completed because the Docker CLI is not installed or not available in this environment. The frontend image includes `nginx.conf` that proxies `/api/` to `http://backend:8000/api/` and serves SPA fallback with `try_files`.
