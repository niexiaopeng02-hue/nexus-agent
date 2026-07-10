# Release Checklist

## Local Verification

- [x] lint passed locally
- [x] unit tests passed locally
- [ ] integration tests passed against a real local PostgreSQL + pgvector database
- [x] eval passed locally
- [x] frontend typecheck passed locally
- [x] frontend build passed locally
- [x] smoke test passed locally against SQLite-backed API runtime

## CI Verification

- [x] backend lint passed in CI
- [x] unit tests passed in CI
- [x] PostgreSQL integration tests passed in CI
- [x] pgvector extension verified in CI
- [x] fresh Alembic migration verified in CI
- [x] `0001` to `head` migration verified in CI
- [x] vector retrieval verified in CI
- [x] threshold filtering verified in CI
- [x] persistence tests passed in CI
- [x] evaluation pipeline passed in CI
- [x] frontend typecheck passed in CI
- [x] frontend production build passed in CI

## Local Database Verification

- [ ] migration fresh install tested against real PostgreSQL locally
- [ ] 0001 to head upgrade tested against real PostgreSQL locally
- [ ] pgvector extension verified locally
- [x] vector dimension configured as 256 in code, tests, and docs

## Docker

- [ ] compose config valid locally
- [ ] containers healthy locally
- [ ] frontend reachable locally
- [ ] backend reachable locally
- [ ] API proxy works locally
- [ ] persistence survives restart locally

## Security

- [x] no obvious secret committed by local pattern scan
- [x] `.env` ignored
- [x] upload validation present
- [x] tool errors sanitized
- [x] CORS configured

## Portfolio

- [ ] live URL
- [ ] public smoke test
- [ ] screenshots
- [ ] demo video
- [x] README links
- [x] architecture diagram
- [ ] GitHub pinned repo
- [ ] Upwork portfolio entry
- [x] resume project copy prepared
- [x] Upwork portfolio copy prepared
- [x] LinkedIn/project launch post prepared

## GitHub Portfolio

- [ ] GitHub About description set
- [ ] GitHub topics set
- [x] README present
- [x] MIT license present
- [x] CI status is green on latest `main`
- [ ] Live Demo URLs added after deployment
- [ ] Real screenshots committed after deployment
- [ ] Known limitations remain honest and current
