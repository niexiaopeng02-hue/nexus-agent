# Technical Decisions

## PostgreSQL + pgvector

PostgreSQL keeps business records, conversations, tickets, and vector search in one operational database. pgvector is a practical choice for a portfolio-grade RAG system because it avoids a separate vector service while preserving production migration discipline.

## Explicit Router + Tool Calling

NexusAgent does not let an unrestricted agent decide arbitrary actions. The router maps a validated intent to known workflows and tools. This is easier to test, audit, secure, and explain in enterprise support settings.

## Mock Provider by Default

The default provider is deterministic and requires no secret. This keeps CI, demos, and local development reliable. The OpenAI provider is available when `LLM_PROVIDER=openai` and `OPENAI_API_KEY` are configured.

## Simplified Authentication

Authentication is intentionally simplified for portfolio demonstration purposes. A production deployment should add real user identity, authorization policies, password hashing or SSO, and audit controls.

