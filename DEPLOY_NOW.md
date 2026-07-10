# Deploy NexusAgent Now

This guide is written for a first public portfolio deployment. It keeps the first demo deterministic by using `LLM_PROVIDER=mock`, so no OpenAI key is exposed and there is no API cost.

Recommended stack:

- Frontend: Vercel static site
- Backend: Render web service using the backend Dockerfile or Python service
- Database: Neon PostgreSQL with pgvector enabled

Alternative stack:

- Single VPS with Docker Compose, PostgreSQL pgvector, backend, frontend, and a reverse proxy with HTTPS.

## Step 1: Create The PostgreSQL Database

Where: Neon, Supabase, or another PostgreSQL provider that supports pgvector.

Set up:

- Create a new PostgreSQL project.
- Choose the region closest to the backend host.
- Copy the pooled or direct connection string.

Expected result:

- You have a `DATABASE_URL` that starts with `postgresql://` or `postgresql+psycopg://`.

Common errors:

- Free plans may sleep or limit connections.
- Some providers require enabling pgvector before migrations can create vector columns.

## Step 2: Verify pgvector

Where: Database SQL editor.

Run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
SELECT extname FROM pg_extension WHERE extname = 'vector';
```

Expected result:

```text
vector
```

Common errors:

- Permission denied: choose a provider/plan that allows extensions, or enable pgvector through the provider UI.
- Empty result: the extension was not enabled.

## Step 3: Prepare Backend Environment Variables

Where: Backend hosting platform environment settings.

Set:

```text
ENVIRONMENT=production
LLM_PROVIDER=mock
DATABASE_URL=<cloud-postgres-url>
CORS_ORIGINS=<frontend-url-after-deploy>
EMBEDDING_DIMENSIONS=256
RAG_SIMILARITY_THRESHOLD=0.18
AUTO_CREATE_SCHEMA=false
SECRET_KEY=<generated-secret>
```

Expected result:

- The backend has all required runtime settings.

Common errors:

- Using `localhost` in `DATABASE_URL` on a cloud host.
- Forgetting to update `CORS_ORIGINS` after the frontend URL is known.

## Step 4: Deploy The Backend

Where: Render, Railway, Fly.io, or another Python/Docker web service platform.

Recommended command path:

- Build from the repository.
- Use `backend/Dockerfile` if the platform supports Docker.
- Ensure the service exposes port `8000`.

Production startup:

```text
database ready -> alembic upgrade head -> uvicorn start
```

The repository already implements this in `backend/scripts/start.sh`.

Expected result:

- The backend service starts without migration errors.

Common errors:

- Build context does not include `sample_data`.
- `DATABASE_URL` is missing.
- pgvector extension is not enabled before migration.

## Step 5: Run Alembic Migration

Where: Backend platform release command, shell, or container startup logs.

Command:

```bash
cd backend
alembic upgrade head
```

Expected result:

- Migration completes.
- `alembic_version` contains the latest revision.

Verify:

```sql
SELECT version_num FROM alembic_version;
```

Common errors:

- Wrong working directory.
- Database URL not available to the migration process.

## Step 6: Check Backend Health

Where: Browser or terminal.

Open:

```text
<backend-url>/api/health
```

Expected result:

```json
{"status":"ok"}
```

Also open:

```text
<backend-url>/docs
```

Expected result:

- FastAPI Swagger UI loads.

Common errors:

- Platform health route points at `/` instead of `/api/health`.
- CORS is not relevant for direct browser health checks, but matters from the frontend.

## Step 7: Deploy The Frontend

Where: Vercel or another static frontend platform.

Set build settings:

```text
Root directory: frontend
Build command: npm run build
Output directory: dist
```

Set environment variable:

```text
VITE_API_BASE_URL=<public-backend-url>
```

Expected result:

- Frontend build succeeds.
- Public frontend URL is created.

Common errors:

- `VITE_API_BASE_URL` missing or pointing to localhost.
- Backend CORS does not include the frontend origin.

## Step 8: Update Backend CORS

Where: Backend hosting platform environment settings.

Set:

```text
CORS_ORIGINS=<frontend-url>
```

Expected result:

- Browser calls from the frontend to backend API succeed.

Common errors:

- Including a trailing slash if the backend expects exact origins.
- Forgetting to restart/redeploy backend after changing env vars.

## Step 9: Verify Frontend Routes

Where: Browser.

Open:

```text
<frontend-url>/
<frontend-url>/chat
<frontend-url>/documents
<frontend-url>/tickets
```

Expected result:

- Routes load without 404.
- Chat, documents, tickets, conversations, and analytics views are reachable.

Common errors:

- Static host is not configured for SPA fallback.
- Frontend was built with an old backend URL.

## Step 10: Run Public Smoke Test

Where: Local terminal after backend is public.

Run:

```bash
NEXUS_API_BASE_URL=<public-backend-url> python scripts/smoke_test.py
```

On Windows PowerShell:

```powershell
$env:NEXUS_API_BASE_URL="<public-backend-url>"
python scripts/smoke_test.py
```

Expected result:

- Health: PASS
- Order query: PASS
- Inventory query: PASS
- Knowledge query: PASS
- No-context query: PASS
- Ticket creation: PASS
- Document upload: PASS
- Analytics: PASS

Common errors:

- Backend URL uses the frontend URL by mistake.
- Database migration did not run.
- Seed data was not loaded.
- CORS affects browser calls but not this direct script.

## Step 11: Record Deployment Verification

Where: `docs/DEPLOYMENT_VERIFICATION.md`.

Only after real public checks pass, fill in:

- Deployment date
- Frontend URL
- Backend URL
- API Docs URL
- Health Check URL
- Database provider
- Smoke test result
- Verified scenarios

Do not add fake URLs or unverified pass results.

## Step 12: Capture Portfolio Assets

Where: Deployed site and `docs/screenshots/`.

Capture real screenshots:

- `01-landing.png`
- `02-chat-rag-citation.png`
- `03-order-tool-call.png`
- `04-ticket-created.png`
- `05-knowledge-base.png`
- `06-analytics-dashboard.png`
- `07-api-docs.png`

Suggested demo prompts:

- `What is NovaTech's return policy?`
- `Where is order ORD-10001?`
- `My keyboard stopped working. Please create a support ticket.`
- `Do you offer drone insurance?`

Expected result:

- Screenshots show the real deployed application.

Common errors:

- Capturing localhost instead of the public URL.
- Committing mockup screenshots that were not generated by the running app.
