#!/bin/bash
set -e

echo "🚀 Starting portal-python server..."

# Wait for database if needed
if [ -n "$DATABASE_URL" ]; then
    echo "⏳ Waiting for database..."
    python -c "
import time
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

url = '$DATABASE_URL'
engine = create_engine(url)
max_retries = 30
retry = 0

while retry < max_retries:
    try:
        engine.connect()
        print('✅ Database is ready')
        sys.exit(0)
    except OperationalError:
        retry += 1
        print(f'⏳ Waiting for database... ({retry}/{max_retries})')
        time.sleep(2)

print('❌ Database connection failed')
sys.exit(1)
"
fi

# Run database migrations if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "🔄 Running database migrations..."
    python -c "
import asyncio
from python.database import init_db
asyncio.run(init_db())
print('✅ Migrations complete')
"
fi

# Start the server
echo "🌟 Starting uvicorn..."
exec uvicorn main:app \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-8000}" \
    --log-level "${LOG_LEVEL:-info}" \
    ${RELOAD:+--reload}
