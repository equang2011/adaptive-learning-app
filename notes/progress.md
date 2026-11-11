# Progress

## Current state
- FastAPI app runs locally on port 8080.
- GET /health returns {"status": "ok"}.
- Health endpoint has one passing pytest test.
- Ruff passes.
- Smoke client can call the LLM gateway on port 8000.
- First curriculum generation returned valid JSON.
- Curriculum and CurriculumNode Pydantic models are being added.

## Last completed
- Proved downstream app -> gateway -> provider -> normalized response.
- Observed client timeout at 40s while gateway succeeded at ~57s.
- Increased smoke client timeout to 90s.
- Added Pydantic validation with Curriculum.model_validate_json(...).

## Next step
- Confirm the generated curriculum validates successfully.
- Save one raw generation output locally.
- Decide whether to add controlled RequestError and ValidationError handling.

## Open questions
- Where should generation records be stored before a database exists?
- What metadata belongs on Curriculum versus CurriculumGenerationRecord?
- What should the production timeout budget be between client and gateway?


# Persistence slice — progress (2026-11-07)

## Done
- SQLAlchemy 2.0 + Alembic, local Postgres 17 in Docker (`adaptive-learning-db`, port 5433).
- `app/db/`: `base.py` (Base), `session.py` (engine, SessionLocal, `get_session`, `DbSession` Annotated dep), `models.py` (`CurriculumRow`, `LessonRow`).
- Migration 1: `curricula`, `lessons` (FK `curriculum_id` ON DELETE CASCADE, indexed). ORM relationship uses `cascade="all, delete-orphan"`, `passive_deletes=True`.
- Curriculum + lesson routes save to Postgres with model, prompt_version, latency; content stored as JSONB, re-validated with Pydantic on read.
- Lesson form passes `curriculum_id`; file-based storage removed.
- `db.rollback()` after loading the curriculum so no connection is held idle-in-transaction during the LLM call.

## Decisions (and why)
- Commit explicitly in routes, not in `get_session` — transaction boundary visible in code.
- JSONB for curriculum tree / lesson pages: always loaded whole; columns only for things filtered/joined on.
- `node_id` is not a FK (lives inside curriculum JSON) — app validates with `find_node_by_id`.
- Dev on Postgres (dev/prod parity), never against prod.

## Next session starts here: "My curricula" queries
Scaffold done by assistant (uncommitted at time of writing): `GET /internal/curricula`, `GET /internal/curricula/{curriculum_id}`, `curricula_list.html`, `curricula_detail.html`, nav links. All DB queries are `# TODO (me)`.

Plan (Eric writes these):
1. List page, naive first: `select(CurriculumRow).order_by(CurriculumRow.created_at.desc())` + `len(row.lessons)` in template → watch the echo log for N+1 (one SELECT lessons per curriculum).
2. Fix N+1: either `selectinload(CurriculumRow.lessons)` or a `func.count(LessonRow.id)` + outer join + `group_by` query returning `(CurriculumRow, lesson_count)` tuples (what the scaffolded template expects).
3. Detail page: `db.get` + 404, then lessons for that curriculum newest first.
4. Later: show saved lesson instead of regenerating — lookup by (curriculum_id, node_id, detail_level); decide on unique constraint / composite index (migration #2).

Small fix: `app/db/session.py` default URL uses `.as_posix` without `()`.

## Then
1. Fix gateway model: deployed gateway returns 400 `unsupported_model` for `openai-gpt-6-luna` even though repo catalog maps it — check which commit Railway runs and every place that raises `unsupported_model`. Local `.env` uses `deepseek-v4.1-flash-1017`. Check prod app's Railway env var names (`GATEWAY_URL`, `GATEWAY_API_KEY`).
2. Users + auth: `users` table, migration adding nullable `user_id`, password hashing, login, `CurrentUser` dependency, filter by owner.
3. Deploy: Railway Postgres, `DATABASE_URL` in Railway vars, run `alembic upgrade head` on deploy.
4. Tests: a test DB + one route test for save/load; update README (persistence claims now true) and LESSON_APP_PRIORITIES.md.


# Persistence slice — progress (2026-11-07)

## Done
- SQLAlchemy 2.0 + Alembic, local Postgres 17 in Docker (`adaptive-learning-db`, port 5433).
- `app/db/`: `base.py` (Base), `session.py` (engine, SessionLocal, `get_session`, `DbSession` Annotated dep), `models.py` (`CurriculumRow`, `LessonRow`).
- Migration 1: `curricula`, `lessons` (FK `curriculum_id` ON DELETE CASCADE, indexed). ORM relationship uses `cascade="all, delete-orphan"`, `passive_deletes=True`.
- Curriculum + lesson routes save to Postgres with model, prompt_version, latency; content stored as JSONB, re-validated with Pydantic on read.
- Lesson form passes `curriculum_id`; file-based storage removed.
- `db.rollback()` after loading the curriculum so no connection is held idle-in-transaction during the LLM call.

## Decisions (and why)
- Commit explicitly in routes, not in `get_session` — transaction boundary visible in code.
- JSONB for curriculum tree / lesson pages: always loaded whole; columns only for things filtered/joined on.
- `node_id` is not a FK (lives inside curriculum JSON) — app validates with `find_node_by_id`.
- Dev on Postgres (dev/prod parity), never against prod.

## Next
1. Fix gateway model: deployed gateway rejects `openai-gpt-6-luna`; local `.env` uses `deepseek-v4.1-flash-1017`. Check prod app + Railway env var names (`GATEWAY_URL`, `GATEWAY_API_KEY`).
2. "Past curricula" page: list rows, reopen a curriculum and its saved lessons (show saved lesson instead of regenerating).
3. Users + auth: `users` table, migration #2 adding nullable `user_id`, password hashing, login, `CurrentUser` dependency, filter by owner.
4. Deploy: Railway Postgres, `DATABASE_URL` in Railway vars, run `alembic upgrade head` on deploy.
5. Tests: a test DB + one route test for save/load; update README (persistence claims now true) and LESSON_APP_PRIORITIES.md.