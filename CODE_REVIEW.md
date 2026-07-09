# Senior Engineer Review

## Critical

- None identified in the implemented portfolio scope.

## High

- Local pgvector integration was not executed because no `PGVECTOR_TEST_DATABASE_URL` is configured in this environment. CI is configured with `pgvector/pgvector:pg16` to run these tests.
- Docker runtime was not verified locally because the Docker CLI is unavailable.
- PostgreSQL Alembic runtime verification was not completed locally because no PostgreSQL/pgvector database is available.
- Authentication remains a documented demo limitation. Production deployment needs real identity, authorization, and audit trails.

## Medium

- SQLite unit tests validate repository behavior but cannot prove pgvector operator behavior. Keep pgvector integration required in CI.
- Mock embeddings are deterministic and test-friendly, not semantically equivalent to production embeddings.
- Local development can create schema for demo friendliness. Docker startup now runs Alembic before Uvicorn and disables automatic `create_all`.
- Migration `0002` intentionally drops pre-production 64-dimensional document/chunk data before moving to `Vector(256)`.
- Prompt injection and document trust controls are basic.

## Low

- Add frontend component tests when a frontend test runner is introduced.
- Add Alembic downgrade and rollback tests.
- Add OpenTelemetry or structured tracing for request metrics.

## Audit Checklist

- README avoids claims of hosted deployment: checked.
- Global mutable `DemoStore` is not on the API request path: checked.
- pgvector retrieval is the PostgreSQL chat runtime path: checked.
- PDF/DOCX parsing uses dedicated parsers: checked.
- Citations are generated from retrieved chunks only: checked.
- Async SQLAlchemy session lifecycle uses FastAPI dependency injection: checked.
- Tool input validation uses Pydantic schemas: checked.
- Tool failures are logged without surfacing raw exceptions as chat API 500s: checked.
- Tool failure persistence stores sanitized error messages; technical details go to server logs: checked.
- Request metric `success` is modeled as Boolean: checked.
- Ticket and handoff public IDs use 12 hex characters plus prefix and unique constraints: checked.
- Docker frontend `/api/` proxy exists: statically checked, runtime not verified.
- Secrets were not committed: checked by inspection.
- CI includes PostgreSQL pgvector service: checked.
