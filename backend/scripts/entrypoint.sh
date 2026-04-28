#!/bin/bash
set -e

echo "→ Starting application bootstrap..."

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
    echo "→ Running migrations..."
    python scripts/migrate.py
fi

if [ "${RUN_SEED:-false}" = "true" ]; then
    echo "→ Running seed..."
    python scripts/seed.py
fi

echo "→ Starting server..."
exec python -m uvicorn apps.api.app:app --host 0.0.0.0 --port 8000
