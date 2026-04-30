#!/usr/bin/env sh
set -e

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Running database migrations..."
  alembic upgrade head
fi

APP_PORT="${PORT:-8000}"
echo "Starting RiskShield AI API on port ${APP_PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT}"
