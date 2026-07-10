# Deployment Verification

Deployment has not been completed yet. Do not mark these checks as passed until they are run against the real public environment.

## Pre-deployment CI Verification

Latest verified CI status: passed on `main` after commit `c1b6628`.

Verified components:

- Backend lint
- Backend unit tests
- PostgreSQL + pgvector integration tests
- Fresh Alembic migration
- `0001` to `head` migration path
- pgvector extension
- Vector search
- Threshold filtering
- Persistence
- Evaluation pipeline
- Frontend typecheck
- Frontend production build

## Deployment Record

- Deployment date: pending
- Frontend URL: pending
- Backend URL: pending
- API Docs URL: pending
- Health Check URL: pending
- Database provider: pending
- LLM provider mode: planned `mock` for first public portfolio demo

## Health Result

Pending.

Expected:

```json
{"status":"ok"}
```

## Smoke Test Result

Pending.

Command:

```bash
NEXUS_API_BASE_URL=<public-backend-url> python scripts/smoke_test.py
```

Required scenarios:

- Health
- Order query
- Inventory query
- Knowledge query
- No-context query
- Ticket creation
- Document upload
- Analytics

## Database Verification

Pending.

Required:

- `SELECT extname FROM pg_extension WHERE extname = 'vector';`
- `alembic upgrade head`
- `alembic_version` equals latest revision
- Seed data does not duplicate after restart

## Known Limitations

- Public deployment URL is not available yet.
- Runtime pgvector verification depends on the selected hosting/database platform.
- Public demo should use MockProvider unless OpenAI secrets are configured in the hosting platform.
