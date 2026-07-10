# Deployment

NexusAgent has a React/Vite frontend, FastAPI backend, and PostgreSQL + pgvector database. It is not deployed yet.

## Recommended Stack

Recommended first public portfolio deployment:

- Frontend: Vercel static hosting
- Backend: Render web service
- Database: Neon PostgreSQL with pgvector

Why this stack:

- Cost: suitable for a small portfolio demo, with low-cost or free-entry tiers to evaluate.
- Deployment complexity: separates static frontend, Python backend, and managed database without requiring server administration.
- pgvector support: Neon supports the pgvector extension and works well for PostgreSQL-backed demos.
- HTTPS: Vercel and Render provide managed HTTPS for public URLs.
- Maintenance: avoids VPS patching, database backups, and TLS operations for the first release.
- Portfolio fit: easy to share separate frontend, API docs, and health URLs.

Use `LLM_PROVIDER=mock` for the first public demo. It is deterministic, has no API cost, does not require exposing an OpenAI key in a public demo environment, and keeps the portfolio walkthrough stable.

Fallback stack:

- Single VPS with Docker Compose.
- Use Caddy, Traefik, or Nginx for HTTPS.
- Run the provided `docker-compose.yml`.
- Own backups, patching, monitoring, and restart policy yourself.

## Option A: Portfolio-Friendly Managed Deployment

Use a managed Postgres provider with pgvector plus a simple app hosting platform.

Reasonable candidates to verify before deployment:

- Neon Postgres with pgvector: https://neon.com/docs/extensions/pgvector
- Supabase Postgres with Vector extension: https://supabase.com/docs/guides/database/extensions/pgvector
- Render web services and PostgreSQL extensions: https://render.com/docs/postgresql-extensions
- Railway may also work if its current PostgreSQL offering supports the needed extension in the selected plan.

Typical shape:

1. Create managed PostgreSQL with pgvector enabled.
2. Deploy backend as a Python web service.
3. Set `DATABASE_URL`, `LLM_PROVIDER=mock` or `openai`, `OPENAI_API_KEY` if needed, `AUTO_CREATE_SCHEMA=false`.
4. Run `alembic upgrade head` as a release command.
5. Deploy frontend static build with `VITE_API_BASE_URL` pointing to the backend, or keep Nginx reverse proxy in a container platform.
6. Run `python scripts/smoke_test.py` with `NEXUS_API_BASE_URL`.

Pros:

- Lower maintenance than a VPS.
- Faster portfolio launch.
- Managed backups and database operations are easier.

Cons:

- Platform-specific networking and release commands need careful setup.
- Free/low-cost tiers may sleep, limit databases, or restrict extensions.
- Need to confirm current pgvector support and plan limits before relying on it.

Recommended for job-search portfolio and Upwork demo: Option A.

Preferred first deployment path:

- Managed PostgreSQL with pgvector: Neon or Supabase, after confirming current plan limits.
- Backend: a Python web service or Docker-compatible service that supports a release command.
- Frontend: static hosting pointed at the backend with `VITE_API_BASE_URL`, or the existing Nginx container if the platform supports multi-service Docker.

This keeps maintenance lower than a VPS while still allowing a real public demo.

## Production Environment Variables

First public portfolio demo can use MockProvider:

```text
ENVIRONMENT=production
LLM_PROVIDER=mock
DATABASE_URL=<managed-postgres-connection-url>
CORS_ORIGINS=<frontend-origin>
EMBEDDING_DIMENSIONS=256
RAG_SIMILARITY_THRESHOLD=0.18
AUTO_CREATE_SCHEMA=false
SECRET_KEY=<platform-secret>
```

Optional OpenAI mode:

```text
LLM_PROVIDER=openai
OPENAI_API_KEY=<platform-secret>
```

Do not commit real values to Git. Put them only in hosting platform secrets/environment settings.

## Option B: Single VPS With Docker Compose

Use an Ubuntu VPS with Docker Compose.

Typical shape:

1. Provision Ubuntu VPS.
2. Install Docker and Docker Compose.
3. Point a domain to the VPS.
4. Add a reverse proxy such as Caddy, Traefik, or Nginx for HTTPS.
5. Store environment variables outside Git.
6. Run `docker compose up --build -d`.
7. Run database backups for the `postgres_data` volume.
8. Run smoke tests after every deployment.

Pros:

- One server controls frontend, backend, and database.
- Docker Compose matches this repository closely.
- Predictable for demos.

Cons:

- You own patching, backups, monitoring, TLS, and incident response.
- Database lives on the same machine unless split later.
- More operational work than a managed platform.

Recommended only if managed platforms are too limiting or a single low-cost VPS is preferred.
