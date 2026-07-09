# Release Checklist

## Code

- [x] lint passed locally
- [x] unit tests passed locally
- [ ] integration tests passed against a real local PostgreSQL + pgvector database
- [x] eval passed locally
- [x] frontend typecheck passed locally
- [x] frontend build passed locally
- [x] smoke test passed locally against SQLite-backed API runtime

## Database

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
- [ ] screenshots
- [ ] demo video
- [x] README links
- [x] architecture diagram
- [ ] GitHub pinned repo
- [ ] Upwork portfolio entry
- [x] resume project copy prepared
- [x] Upwork portfolio copy prepared
- [x] LinkedIn/project launch post prepared
