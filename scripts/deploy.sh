#!/bin/bash
# Deploy script for production

set -e

echo "🚀 Deploying Swarm Labs to production..."

# Pull latest code
git pull origin main

# Build Docker images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Run migrations
docker-compose run --rm swarm python scripts/init_db.py

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Health check
sleep 10
python scripts/health_check.py

echo "✅ Deployment complete!"
