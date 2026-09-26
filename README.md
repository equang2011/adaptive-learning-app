# Adaptive Learning App

A mobile-first learning app that turns a topic and optional learner context
into a structured curriculum, then generates focused lessons for individual
curriculum nodes. Long-term direction and full product context live in
[`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md).

Core loop: **topic + learner context → curriculum → lesson → (later) quiz**.

## Architecture

This app is one of two services. It talks to a separate **LLM Gateway**
service over HTTP — it never calls a model provider directly and holds no
provider API keys.

```
Browser
  |
  v
Learning App (this repo) :8001
  |
  v
LLM Gateway :8000
  |
  v
Provider (OpenRouter, etc.)
```

This repo owns curriculum/lesson prompts, schemas, and validation. The
gateway owns provider auth, request/response normalization, timeouts, and
retries.

## Stack

- FastAPI + Jinja2 templates (server-rendered, no separate frontend yet)
- Pydantic for validating generated JSON
- httpx for calling the gateway
- pytest + Ruff

## Setup

```bash
uv sync
cp .env.example .env
```

Start the gateway separately (port 8000), then run this app:

```bash
uvicorn app.main:app --reload --port 8001
```

- `GET /health` — liveness check
- `GET /internal` — working UI for generating and reviewing curricula/lessons
  against saved test scenarios and models (`app/config/`)

## Deployment

Currently hosted on Railway: <https://adaptive-learning-app-production.up.railway.app/internal>

`/internal` always generates with `openai/gpt-5.6-luna` (set by `MODEL` in
`app/routes/internal.py`); there is no model picker.

## Project layout

```
app/
  main.py              FastAPI app, /health
  routes/internal.py    /internal routes: generate curriculum, generate lesson
  models/               Pydantic schemas (curriculum.py, lesson.py)
  services/             Prompt construction + gateway invocation per domain
  clients/gateway.py     httpx client for the LLM gateway's /invoke endpoint
  config/                Scenario and model fixtures used by /internal (committed)
  templates/, static/    Jinja2 templates and CSS for the internal UI
  evaluation/            LLM-graded evaluation of generated curricula/lessons
prompts/                 Versioned prompt templates (curriculum_v1..v4, lesson_v1, ...)
scripts/                 Standalone smoke-test clients for curriculum/lesson generation
data/                    Gitignored; not present in deployed containers
  generations/            Saved curriculum generation outputs (JSON)
  lessons/                Saved lesson generation outputs (JSON)
  test_inputs/            Evaluation batch fixtures
  evaluations/            Evaluation run outputs
notes/                    Working notes and design docs (not polished docs)
tests/                    pytest suite
```

## Prompts

Prompts are plain-text templates in `prompts/`, versioned by filename
(`curriculum_v1.md`, `curriculum_v2.md`, ...) rather than edited in place, so
past generations stay reproducible against the prompt version that produced
them. Each generation record stores which prompt version and model produced
it (see `CurriculumGenerationRecord` in `app/models/curriculum.py`).

Templates use Python `str.format()` placeholders (e.g. `{curriculum_json}`,
`{lesson_length_minutes}`). Literal JSON braces inside a template must be
doubled (`{{` / `}}`) to survive formatting.

## Evaluation

Generated curricula and lessons can be evaluated by separate LLM-based
evaluators. Evaluation is intentionally kept separate from generation: a
generated artifact is treated as input to an evaluator prompt and parsed into
a structured Pydantic evaluation object.

The initial evaluation flow is:

```text
saved curriculum or lesson
  → versioned evaluator prompt
  → LLM Gateway
  → validated evaluation object
  → saved evaluation JSON

## Testing

```bash
pytest
ruff check .
```

## Current status

Curriculum generation and lesson generation both work end-to-end through the
gateway, with Pydantic validation on the returned JSON. The `/internal` UI is
the current way to exercise both flows manually against saved scenarios and
models. Quiz generation, a real frontend, and persistence beyond flat JSON
files are not built yet — see `PROJECT_CONTEXT.md` for the full roadmap and
`notes/progress.md` for day-to-day state.

## Configuration

```
LLM_GATEWAY_URL=http://127.0.0.1:8000/invoke
```

The value is the full gateway endpoint, including `/invoke`. In production it
points at the deployed gateway on Railway
(`https://llm-gateway-production-b085.up.railway.app/invoke`).

No provider API keys belong in this repo — those live in the gateway service.
