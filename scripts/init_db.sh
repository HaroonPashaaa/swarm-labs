#!/bin/bash
# Database initialization script

echo "🗄️  Initializing database..."

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until pg_isready -h localhost -p 5432; do
    sleep 1
done

# Run migrations
echo "Running database migrations..."
python scripts/init_db.py

echo "✅ Database initialized!"
