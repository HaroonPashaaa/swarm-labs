# Webhook Integration

## Discord Webhooks

### Setup

1. Create Discord webhook in your server
2. Copy webhook URL
3. Add to `.env`:

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Alert Types

- **Trade Alerts**: Executed trades
- **Signal Alerts**: New trading signals
- **Risk Alerts**: Risk limit warnings
- **System Alerts**: Errors and notifications

## Custom Webhooks

### Configuration

```python
WEBHOOK_CONFIG = {
    'trade': 'https://your-webhook.com/trades',
    'alert': 'https://your-webhook.com/alerts'
}
```

### Payload Format

```json
{
  "timestamp": "2026-04-16T10:30:00Z",
  "type": "trade",
  "data": {
    "symbol": "BTC/USDT",
    "action": "buy",
    "price": 50000
  }
}
```
