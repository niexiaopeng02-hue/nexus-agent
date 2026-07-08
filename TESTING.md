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

Latest local result: `22 passed`.

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

Local Docker runtime verification was not completed because the Docker CLI is not installed or not available in this environment.
