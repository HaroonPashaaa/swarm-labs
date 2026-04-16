# Monitoring Guide

## Prometheus Metrics

### Available Metrics

- `swarm_trades_total` - Total trades executed
- `swarm_pnl_daily` - Daily P&L
- `swarm_positions_open` - Open positions count
- `swarm_signals_generated` - Signals generated
- `swarm_agent_status` - Agent health status

### Grafana Dashboard

Import dashboard from `dashboard/dashboard.json`

## Log Monitoring

### Centralized Logging

Configure with ELK stack or similar:

```yaml
# docker-compose.logging.yml
services:
  elasticsearch:
    image: elasticsearch:8.x
  
  logstash:
    image: logstash:8.x
  
  kibana:
    image: kibana:8.x
```

### Alert Rules

```yaml
alerts:
  - name: High Drawdown
    condition: drawdown > 0.10
    action: notify_discord
  
  - name: Agent Down
    condition: agent_status == 0
    action: restart_agent
```
