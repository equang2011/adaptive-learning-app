# CLAUDE.md — Adaptive Learning App

## This project

**Portfolio role:** LLM application architecture, generation reliability, structured evaluation, and a working client of the LLM gateway. Don't expand it into retrieval, personalization, payments, or social features.

**Stack:** FastAPI (sync `def` routes) · Jinja templates · Pydantic models in `app/models/` · SQLAlchemy 2.0 ORM models in `app/db/models.py` · Alembic migrations in `migrations/` · Postgres · LLM calls go through the gateway (`app/clients/gateway.py`), never directly to a provider.

**Persistence conventions**
- Sessions come from the `DbSession` dependency (`app/db/session.py`). Routes commit explicitly; `get_session` never commits.
- Generated curricula and lessons are stored as JSONB `content` and re-validated with Pydantic on read. Columns are only for things we filter, sort, join on, or show in lists.
- Don't hold a DB transaction open across an LLM call (load what you need, then `db.rollback()` before the slow call).
- Watch for N+1 queries in list views; prefer an aggregate or `selectinload`.
- Schema changes always go through a new Alembic migration. Never edit a migration that has been applied anywhere.

**Local dev**
- DB: Docker container `adaptive-learning-db` on `localhost:5433` (start Docker Desktop first).
- Run: `uv run uvicorn app.main:app --reload --port 8080`
- Migrate: `uv run alembic upgrade head` · new migration: `uv run alembic revision --autogenerate -m "..."` (read the generated file before applying)
- Lint: `uv run ruff check` / `uv run ruff format`
- Required env: `GATEWAY_URL`, `GATEWAY_API_KEY`, `DATABASE_URL`. See `.env.example`.

**Deploy rules**
- Railway auto-deploys from `main`. Work on feature branches; merge to `main` only when production has everything the change needs (env vars, database, migrations).
- When a change adds or renames an env var or needs a migration, say so explicitly in your summary.

**When you finish a task, report:** what changed, why, what you ran to verify it, remaining limitations, and anything that affects production.