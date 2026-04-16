# Swarm Labs

> Multi-Agent AI Trading Swarm with Cross-Market Intelligence

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Redis](https://img.shields.io/badge/Redis-7.0-red.svg)](https://redis.io/)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-Latest-orange.svg)](https://www.timescale.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

Swarm Labs is a sophisticated multi-agent trading system where specialized AI agents monitor cryptocurrency futures, forex, and stock futures markets simultaneously. Agents consult each other on optimal strategies, report intelligence to OpenClaw (the central orchestrator), and execute trades through integrated exchange APIs.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         OPENCLAW (CEO)                           │
│              Central Decision Engine & Orchestrator              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
┌─────────▼─────────┐ ┌────▼─────┐ ┌───────▼────────┐
│   CRYPTO AGENT    │ │  FOREX   │ │ FUTURES AGENT  │
│  (Binance/Bybit)  │ │  (OANDA) │ │    (IBKR)      │
└─────────┬─────────┘ └────┬─────┘ └───────┬────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
┌─────────▼─────────┐ ┌────▼─────┐ ┌───────▼────────┐
│ STRATEGY EVALUATOR│ │   RISK   │ │  REDIS QUEUE   │
│  (8 Strategies)   │ │ MANAGER  │ │  (Message Bus) │
└───────────────────┘ └──────────┘ └────────────────┘
```

## Features

### Multi-Market Coverage
- **Crypto Futures**: BTC, ETH perpetuals via Binance & Bybit
- **Forex**: Major and minor pairs via OANDA
- **Stock Futures**: ES, NQ, YM via Interactive Brokers

### Swarm Intelligence
- 8 concurrent trading strategies evaluated in real-time
- Weighted consensus mechanism with confidence scoring
- Cross-market correlation detection
- Real-time strategy adaptation based on market conditions

### Risk Management
- Position sizing based on volatility
- Dynamic stop-loss and take-profit
- Maximum drawdown protection
- Kill switches and circuit breakers
- Portfolio-level risk aggregation

### Execution Layer
- Multi-exchange integration with unified API
- Order routing optimization
- Position tracking across all markets
- Error handling and retry logic

### Communication
- Discord integration for real-time alerts
- GitHub logging for decision audit trail
- Redis pub/sub for agent coordination
- Structured JSON logging

## Trading Strategies

1. **Momentum/Trend Following** - ATR and moving average confirmation
2. **Mean Reversion** - Fade overextended moves
3. **Scalping** - High-frequency during liquidity windows
4. **News/Sentiment** - Real-time news analysis
5. **Volatility Breakout** - Bollinger Band squeeze detection
6. **Grid Trading** - Range-bound market strategies
7. **Arbitrage** - Cross-exchange and cross-market opportunities
8. **Session-Based** - Asia/London/NY session optimizations

## Quick Start

```bash
# Clone repository
git clone https://github.com/HaroonPashaaa/swarm-labs.git
cd swarm-labs

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start infrastructure
docker-compose up -d

# Initialize database
python scripts/init_db.py

# Run swarm
python -m openclaw.core
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [API Reference](docs/API.md) - Exchange integrations and methods
- [Strategies](docs/STRATEGIES.md) - Trading strategy implementations
- [Risk Management](docs/RISK.md) - Risk controls and safety measures
- [Deployment](docs/DEPLOYMENT.md) - Production deployment guide

## Repository Structure

```
swarm-labs/
├── openclaw/          # Central orchestrator
├── agents/            # Market-specific agents
├── strategies/        # Trading strategies
├── exchanges/         # Exchange integrations
├── core/              # Shared infrastructure
├── data/              # Data handling
├── tests/             # Test suite
└── docs/              # Documentation
```

## Safety & Disclaimer

This system is designed for paper trading by default. Real money trading requires:
- Extensive backtesting
- Understanding of all risk parameters
- Acceptance of potential losses
- Compliance with local regulations

**Never trade with money you cannot afford to lose.**

## License

MIT License - See [LICENSE](LICENSE) for details.

---

Built with precision by the Swarm Labs team.
