# API Documentation

## REST API Endpoints

### Health Check
```
GET /health
```
Returns system health status.

### Agent Status
```
GET /api/v1/agents/status
```
Returns status of all swarm agents.

Response:
```json
{
  "agents": [
    {
      "agent_id": "crypto_agent",
      "market": "crypto",
      "running": true,
      "last_signal": "2026-04-16T10:30:00Z"
    }
  ]
}
```

### OpenClaw Status
```
GET /api/v1/openclaw/status
```
Returns OpenClaw orchestrator status.

Response:
```json
{
  "status": "running",
  "daily_pnl": 1250.50,
  "open_positions": 5,
  "pending_signals": 3,
  "timestamp": "2026-04-16T10:30:00Z"
}
```

### Performance Report
```
GET /api/v1/performance?period=daily
```
Returns trading performance metrics.

Query Parameters:
- `period`: daily, weekly, monthly

### Manual Override
```
POST /api/v1/trade/manual
```
Manual trade override (requires authentication).

Body:
```json
{
  "symbol": "BTC/USDT",
  "action": "buy",
  "reason": "Manual intervention"
}
```

### Emergency Stop
```
POST /api/v1/emergency-stop
```
Trigger emergency stop for all agents.

## WebSocket API

Connect to: `ws://localhost:8080/ws`

### Subscribe to Signals
```json
{
  "action": "subscribe",
  "channel": "agent:signals"
}
```

### Subscribe to Trades
```json
{
  "action": "subscribe",
  "channel": "execution:trades"
}
```

### Authentication
```json
{
  "action": "auth",
  "token": "your-jwt-token"
}
```

## Authentication

All endpoints (except /health) require JWT authentication.

Header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

## Rate Limiting

- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated
