# Progress

## Completed

- FastAPI backend and React/Vite frontend.
- Async SQLAlchemy repository layer for runtime persistence.
- PostgreSQL + pgvector model and migration path.
- Documents, chunks, conversations, messages, tickets, handoffs, tool logs, orders, products, inventory, and request metrics persisted through repositories.
- PDF/DOCX/TXT/Markdown parser abstraction.
- Deterministic fast-path classifier plus structured LLM classifier fallback.
- Typed business tool registry with failure logging.
- Sanitized tool error persistence and 12-hex public IDs for tickets and handoffs.
- Nginx frontend reverse proxy for `/api/`.
- GitHub Actions CI with PostgreSQL pgvector service.
- Deterministic evaluation pipeline and generated eval report.
- Smoke test script for deployed/runtime API verification.

## Verified Locally

- Backend lint: `ruff check .` passed.
- Backend non-integration tests: `34 passed, 5 deselected`.
- Evaluation pipeline: 16 cases, all reported key metrics at `1.0`.
- Frontend install: `npm ci` completed.
- Frontend typecheck: passed.
- Frontend production build: passed.
- Smoke test script passed against a local SQLite-backed FastAPI runtime.

## Skipped Or Not Locally Verified

- Local pgvector integration tests: 5 skipped because `PGVECTOR_TEST_DATABASE_URL` was not configured.
- Local `alembic upgrade head`: not verified against PostgreSQL because no PostgreSQL/pgvector database is available locally.
- Docker Compose config/up: not verified because Docker CLI is not installed in this environment.
- Hosted deployment: not configured.

## Remaining Production Work

- Real authentication and authorization.
- Live deployment and smoke checks against the deployed URL.
- Broader migration rollback and transaction-boundary tests.
