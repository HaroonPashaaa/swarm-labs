# Deployment Guide

## Docker Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/HaroonPashaaa/swarm-labs.git
cd swarm-labs

# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f swarm
```

### Services

- **swarm**: Main application (port 8080)
- **postgres**: PostgreSQL database (port 5432)
- **timescaledb**: Time-series database (port 5433)
- **redis**: Message queue (port 6379)
- **grafana**: Monitoring dashboard (port 3000)

## Manual Deployment

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- TimescaleDB

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python scripts/init_db.py

# Run the swarm
python -m openclaw.core
```

## Cloud Deployment

### AWS ECS

```bash
# Build and push to ECR
docker build -t swarm-labs .
docker tag swarm-labs:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/swarm-labs:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/swarm-labs:latest

# Deploy to ECS
aws ecs update-service --cluster swarm-labs --service swarm --force-new-deployment
```

### Railway

```bash
railway login
railway init
railway up
```

### Render

1. Connect GitHub repository
2. Add environment variables
3. Deploy

## Environment Variables

Required for production:

```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
BINANCE_API_KEY=...
BINANCE_SECRET=...
# ... etc
```

## Monitoring

Access Grafana at `http://localhost:3000`

Default credentials: admin/admin

## SSL/TLS

Use Nginx or Traefik as reverse proxy for SSL termination.

Example Nginx config:

```nginx
server {
    listen 443 ssl;
    server_name api.swarm-labs.io;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
}
```

## Backup

### Database Backup

```bash
# Backup PostgreSQL
docker exec swarm-postgres pg_dump -U swarm swarm_labs > backup.sql

# Backup TimescaleDB
docker exec swarm-timescale pg_dump -U swarm swarm_market > market_backup.sql
```

### Redis Backup

```bash
docker exec swarm-redis redis-cli SAVE
docker cp swarm-redis:/data/dump.rdb ./redis_backup.rdb
```
