# Technical Decisions

## PostgreSQL + pgvector

PostgreSQL stores documents, chunks, conversations, messages, tickets, handoffs, tool logs, orders, products, inventory, and request metrics. pgvector keeps retrieval in the same transactional database for this portfolio scope.

## 256-Dimensional Embeddings

The vector column uses `Vector(256)`. The OpenAI provider requests the configured dimensionality from the embeddings API; it does not slice or pad returned vectors. The mock provider emits deterministic vectors with the same configured dimension for tests.

Migration `0002` uses a pre-production strategy for old 64-dimensional data: it deletes existing documents and chunks before changing `document_chunks.embedding` to `vector(256)`. This is explicit data cleanup, not an in-place vector resize. Demo seed data or uploaded documents must be regenerated after upgrading an old local database.

## Explicit Router + Tools

The system avoids arbitrary agent actions. A validated intent maps to a known workflow or tool. Tool inputs are Pydantic models, and failures are captured as safe `ToolExecutionError` variants.

Persistent tool error records store structured error codes and sanitized messages. Full technical exceptions are sent to server logs with `logger.exception` instead of being persisted or returned to users.

## Mock Provider By Default

`LLM_PROVIDER=mock` keeps local demos and CI deterministic and secret-free. The OpenAI provider is available for production-style runs.

## SQLite Test Isolation

Unit/API tests use SQLite with the same repository layer for speed. PostgreSQL + pgvector behavior is covered by integration tests that run when `PGVECTOR_TEST_DATABASE_URL` is configured, including CI.

## Parser Abstraction

Upload parsing is separated from API routing. PDF, DOCX, and text formats have dedicated parsers so page/paragraph metadata can evolve without bloating `main.py`.

## Simplified Authentication

Authentication is intentionally limited. A real deployment should add SSO or password hashing, role-based authorization, and audit controls.
