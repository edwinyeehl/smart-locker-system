#!/bin/sh
set -e

echo "Waiting for PostgreSQL database to be ready..."
until uv run python -c "
import socket, os
host = os.getenv('POSTGRES_HOST', 'db')
port = int(os.getenv('POSTGRES_PORT', '5432'))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
try:
    s.connect((host, port))
    s.close()
    exit(0)
except Exception:
    exit(1)
"; do
  echo "PostgreSQL is unavailable - sleeping 2 seconds"
  sleep 2
done

echo "PostgreSQL is ready! Executing Alembic database migrations via uv..."
uv run alembic upgrade head

echo "Starting FastAPI dev server with uv..."
exec uv run fastapi dev --host 0.0.0.0 --port 8000
