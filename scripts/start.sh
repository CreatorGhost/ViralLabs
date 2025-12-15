#!/bin/bash
set -e

echo "Starting database migration check..."

# Check if alembic_version table exists
ALEMBIC_EXISTS=$(python -c "
from sqlalchemy import create_engine, text
from backend.core.config import settings

engine = create_engine(settings.database_url.replace('+asyncpg', ''))
with engine.connect() as conn:
    result = conn.execute(text(\"\"\"
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'alembic_version'
        )
    \"\"\"))
    print('true' if result.scalar() else 'false')
")

# Check if users table exists (indicates existing database)
USERS_EXISTS=$(python -c "
from sqlalchemy import create_engine, text
from backend.core.config import settings

engine = create_engine(settings.database_url.replace('+asyncpg', ''))
with engine.connect() as conn:
    result = conn.execute(text(\"\"\"
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'users'
        )
    \"\"\"))
    print('true' if result.scalar() else 'false')
")

echo "Alembic version table exists: $ALEMBIC_EXISTS"
echo "Users table exists: $USERS_EXISTS"

if [ "$ALEMBIC_EXISTS" = "false" ] && [ "$USERS_EXISTS" = "true" ]; then
    echo "Database has tables but no migration history. Stamping current state..."
    alembic -c backend/alembic.ini stamp head
    echo "Database stamped with current migration head."
else
    echo "Running migrations..."
    alembic -c backend/alembic.ini upgrade head
    echo "Migrations completed."
fi

echo "Starting FastAPI server..."
exec python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
