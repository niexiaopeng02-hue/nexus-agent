# Senior Engineer Review

## Critical

- None currently identified in the implemented demo scope.

## High

- Authentication is documented as simplified. A real deployment needs scoped authorization, password hashing or SSO, and admin/user separation.
- Local pgvector integration tests were not executed in this environment because no PostgreSQL/pgvector URL was available. CI is configured to run them with a pgvector service.
- On native Windows, psycopg async PostgreSQL connections require a Selector event loop. Docker/Linux deployment avoids this local event-loop limitation.

## Medium

- Mock embeddings are deterministic but not semantically rich. OpenAI embeddings should be used for production retrieval quality with a deliberate vector dimensionality migration.
- Prompt injection controls are basic. Add source filtering, instruction hierarchy checks, and retrieval content sanitization before external document ingestion.

## Low

- Add frontend component tests once a test runner is introduced.
- Add migration rollback tests and stricter transaction-boundary tests.

## Fixes Applied

- Core workflows use explicit routing instead of unconstrained agent behavior.
- Tool inputs use Pydantic validation.
- Uploads validate type, size, and sanitized filenames.
- No-context answers refuse instead of fabricating citations.
- Dependency compatibility was fixed for the local Python runtime by moving `psycopg[binary]` to `3.3.4`.
- Frontend dependency versions were pinned for repeatable installs.
- Runtime APIs now use async SQLAlchemy repositories instead of global mutable `DemoStore`.
- pgvector retrieval is in the chat runtime path for PostgreSQL deployments.
- PDF and DOCX parsing now use PyMuPDF and python-docx.
- Frontend production Docker image now proxies `/api/` through Nginx.
