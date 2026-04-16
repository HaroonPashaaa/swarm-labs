#!/bin/bash
# Quick start script

echo "🐝 Swarm Labs Quick Start"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# Setup
echo "Setting up Swarm Labs..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys"
fi

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services
echo "Waiting for services to start..."
sleep 15

# Check health
echo ""
echo "Checking health..."
docker-compose ps

echo ""
echo "✅ Swarm Labs is running!"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop: docker-compose down"
