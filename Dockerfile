FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8001

CMD uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}
