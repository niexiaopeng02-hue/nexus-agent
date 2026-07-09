# Interview Guide

## What To Emphasize

- The project intentionally uses explicit workflows instead of open-ended autonomous actions.
- Citations are created only from retrieved database chunks.
- Tool inputs are Pydantic-validated and failures are logged.
- SQLite is used only for fast unit-test isolation; PostgreSQL + pgvector is the production target.
- The mock provider keeps CI deterministic and secret-free.

## Trade-Offs

- Mock embeddings are deterministic but less semantic than OpenAI embeddings.
- Authentication is simplified for portfolio scope.
- Startup schema creation is convenient for demos; production should run migrations explicitly.
- Local Docker and pgvector runtime checks depend on local infrastructure availability.

## Useful Talking Points

- Why pgvector was chosen over a separate vector database for this scope.
- How session lifecycle is managed with FastAPI dependency injection.
- How malformed LLM classifier output is validated and safely handled.
- How PDF page metadata becomes citation metadata.
- How no-context behavior is threshold-driven instead of hard-coded topic blocking.
