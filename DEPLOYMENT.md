# Deployment

NexusAgent has a React/Nginx frontend, FastAPI backend, and PostgreSQL + pgvector database. It is not deployed yet.

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

Recommended for job-search portfolio and Upwork demo: Option A, using managed Postgres with pgvector and the simplest web hosting that supports backend release commands.

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
