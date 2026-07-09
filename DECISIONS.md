# Technical Decisions

## PostgreSQL + pgvector

PostgreSQL stores documents, chunks, conversations, messages, tickets, handoffs, tool logs, orders, products, inventory, and request metrics. pgvector keeps retrieval in the same transactional database for this portfolio scope.

## 256-Dimensional Embeddings

The vector column uses `Vector(256)`. The OpenAI provider requests the configured dimensionality from the embeddings API; it does not slice or pad returned vectors. The mock provider emits deterministic vectors with the same configured dimension for tests.

## Explicit Router + Tools

The system avoids arbitrary agent actions. A validated intent maps to a known workflow or tool. Tool inputs are Pydantic models, and failures are captured as safe `ToolExecutionError` variants.

## Mock Provider By Default

`LLM_PROVIDER=mock` keeps local demos and CI deterministic and secret-free. The OpenAI provider is available for production-style runs.

## SQLite Test Isolation

Unit/API tests use SQLite with the same repository layer for speed. PostgreSQL + pgvector behavior is covered by integration tests that run when `PGVECTOR_TEST_DATABASE_URL` is configured, including CI.

## Parser Abstraction

Upload parsing is separated from API routing. PDF, DOCX, and text formats have dedicated parsers so page/paragraph metadata can evolve without bloating `main.py`.

## Simplified Authentication

Authentication is intentionally limited. A real deployment should add SSO or password hashing, role-based authorization, and audit controls.
