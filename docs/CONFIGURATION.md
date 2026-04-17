# Wojak Capital Configuration

## Environment Variables

### Trading Configuration
```bash
# Trading Mode
PAPER_TRADING=true                    # Start with paper trading

# Risk Limits
MAX_POSITION_SIZE_PCT=0.02           # 2% max per trade
MAX_DAILY_LOSS_PCT=0.05              # 5% daily stop
MAX_TOTAL_EXPOSURE=0.20              # 20% total exposure

# Strategy Settings
MIN_CONFIDENCE_THRESHOLD=0.65        # 65% min confidence
CONSENSUS_THRESHOLD=0.60             # 60% consensus required
```

### API Keys (Required)
```bash
# Binance
BINANCE_API_KEY=your_key_here
BINANCE_SECRET=your_secret_here
BINANCE_TESTNET=true

# Bybit
BYBIT_API_KEY=your_key_here
BYBIT_SECRET=your_secret_here
BYBIT_TESTNET=true

# OANDA
OANDA_API_KEY=your_key_here
OANDA_ACCOUNT_ID=your_account_id
OANDA_PRACTICE=true

# Interactive Brokers
IBKR_ACCOUNT_ID=your_account_id
```

### Infrastructure
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/swarm_labs

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Discord (Optional)
DISCORD_WEBHOOK_URL=your_webhook_url
```

## Strategy Weights

Default strategy weights in `core/config.py`:

| Strategy | Weight | Description |
|----------|--------|-------------|
| momentum | 1.0 | Trend following |
| mean_reversion | 1.0 | Fade extremes |
| scalping | 0.8 | Quick trades |
| news_sentiment | 0.9 | Event-driven |
| volatility_breakout | 1.1 | Breakout trading |
| grid_trading | 0.7 | Range trading |
| arbitrage | 1.2 | Cross-exchange |
| session_based | 0.9 | Time-based |

## Market Sessions

### Forex Sessions
- **Asia**: 00:00 - 09:00 UTC
- **London**: 08:00 - 17:00 UTC
- **New York**: 13:00 - 22:00 UTC
- **Overlap**: London/NY overlap (13:00-17:00 UTC)

### Futures Hours (CT)
- **Pre-market**: 16:00 - 08:30 (previous day)
- **Regular**: 08:30 - 15:15
- **After hours**: 15:15 - 16:00
