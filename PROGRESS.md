# Progress

## Completed

- Monorepo scaffold
- FastAPI API
- React frontend
- Provider abstraction
- Intent classifier and workflow router
- Tool registry with order, product, inventory, ticket, and handoff tools
- RAG ingestion, retrieval, and citation generation
- Demo NovaTech knowledge base
- Tests and deterministic evaluation suite
- Docker Compose and GitHub Actions
- README and architecture documentation
- Senior engineer review

## Verified

- Backend dependencies installed in `backend/.venv`.
- Backend tests passed: 22 passed.
- Backend lint passed: `ruff check .`.
- Evaluation passed with 15 cases and 1.0 for intent accuracy, tool selection accuracy, citation presence, and no-context refusal rate.
- Frontend dependencies installed.
- Frontend typecheck passed.
- Frontend production build passed.
- Backend app import/start object check passed.
- Runtime path migrated from global `DemoStore` to async SQLAlchemy repositories.
- PDF/DOCX/TXT/Markdown parser abstraction implemented.
- Nginx production reverse proxy for `/api/` added.

## Not Completed

- Live hosted deployment.
- Real authentication beyond documented demo posture.
- Runtime Docker startup verification. Docker CLI is not installed or not available in this local environment.
- Local pgvector integration execution. `PGVECTOR_TEST_DATABASE_URL` was not configured locally, so pgvector-specific tests were skipped here and are configured for CI.
