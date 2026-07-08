# Senior Engineer Review

## Critical

- None currently identified in the implemented demo scope.

## High

- Production persistence path is modeled and migrated, but the running demo currently uses an in-memory repository. Before production, connect services to SQLAlchemy repositories and add transaction tests.
- Authentication is documented as simplified. A real deployment needs scoped authorization, password hashing or SSO, and admin/user separation.

## Medium

- File parsing currently treats uploads as UTF-8 text for the demo path. Production support for PDF and DOCX should use dedicated parsers with page metadata extraction.
- Mock embeddings are deterministic but not semantically rich. OpenAI embeddings should be used for production retrieval quality.
- Prompt injection controls are basic. Add source filtering, instruction hierarchy checks, and retrieval content sanitization before external document ingestion.

## Low

- Add frontend component tests once a test runner is introduced.
- Add database integration tests using a temporary PostgreSQL + pgvector service in CI.

## Fixes Applied

- Core workflows use explicit routing instead of unconstrained agent behavior.
- Tool inputs use Pydantic validation.
- Uploads validate type, size, and sanitized filenames.
- No-context answers refuse instead of fabricating citations.
- Dependency compatibility was fixed for the local Python runtime by moving `psycopg[binary]` to `3.3.4`.
- Frontend dependency versions were pinned for repeatable installs.
