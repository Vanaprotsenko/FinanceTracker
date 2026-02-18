#!/usr/bin/env sh
set -e

echo "⏳ Waiting for PostgreSQL..."

until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${POSTGRES_USER}" > /dev/null 2>&1; do
  sleep 1
done

echo "✅ PostgreSQL is ready"


if [ "$RUN_MIGRATIONS" = "1" ]; then
  echo "🚀 Running Alembic migrations..."
  alembic upgrade head
fi

echo "✅ Migrations applied successfully"
echo "🚀 Starting app..."
exec "$@"
