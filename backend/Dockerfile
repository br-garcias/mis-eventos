FROM python:3.11-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.in-project true && poetry install --no-interaction --no-ansi

COPY src ./src

RUN python -m compileall -q src

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH"

RUN groupadd -r appgroup && useradd -r -g appgroup appuser
WORKDIR /app

COPY --from=builder /build/.venv ./.venv
COPY --from=builder /build/src ./src
COPY scripts ./scripts
COPY pyproject.toml .env.example ./

RUN chmod +x scripts/entrypoint.sh

USER appuser

EXPOSE 8000
ENTRYPOINT ["./scripts/entrypoint.sh"]
