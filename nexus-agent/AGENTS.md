# Engineering Guide

NexusAgent is a monorepo with a FastAPI backend and Vite React frontend. Keep changes scoped, readable, and backed by runnable checks.

## Commands

- Backend install: `cd backend && pip install -r requirements.txt`
- Backend dev: `cd backend && uvicorn app.main:app --reload`
- Backend tests: `cd backend && pytest`
- Backend lint: `cd backend && ruff check .`
- Evaluation: `cd backend && PYTHONPATH=. python evals/run_eval.py`
- Frontend install: `cd frontend && npm install`
- Frontend dev: `cd frontend && npm run dev`
- Frontend typecheck/build: `cd frontend && npm run typecheck && npm run build`
- Docker: `docker compose up --build`

## Rules

- Never commit `.env` or real API keys.
- Use `LLM_PROVIDER=mock` for local tests and CI.
- Keep citations tied to retrieved chunks only.
- Validate tool input with Pydantic schemas.
- Keep upload type and size validation in place.
- Prefer explicit workflows over open-ended autonomous agent behavior.

