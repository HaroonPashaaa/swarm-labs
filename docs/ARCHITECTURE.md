# Architecture

## System Overview

Swarm Labs is a multi-agent trading system where specialized AI agents monitor multiple financial markets simultaneously, consult each other on optimal strategies, and report to OpenClaw (the central orchestrator) for final trading decisions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      OPENCLAW (CEO)                         │
│              Central Decision Engine                        │
│  - Receives signals from all agents                         │
│  - Calculates weighted consensus                            │
│  - Makes final trading decisions                            │
│  - Issues commands to agents                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌──────▼────────┐
│ CRYPTO AGENT │ │ FOREX    │ │ FUTURES AGENT │
│ (Binance/    │ │ (OANDA)  │ │ (Interactive  │
│  Bybit)      │ │          │ │  Brokers)     │
└───────┬──────┘ └────┬─────┘ └──────┬────────┘
        │             │              │
        └─────────────┼──────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼─────┐ ┌────▼────┐ ┌──────▼──────┐
│ STRATEGY    │ │ RISK    │ │  DATABASE   │
│ EVALUATOR   │ │ MANAGER │ │  (Timescale │
│ (8 Strategies)│ │         │ │   DB)       │
└─────────────┘ └─────────┘ └─────────────┘
```

## Components

### OpenClaw
The central orchestrator that:
- Collects signals from all market agents
- Calculates weighted consensus using confidence scores
- Makes final trade decisions
- Routes commands to appropriate agents
- Logs all decisions

### Market Agents
Each agent specializes in one market:
- **CryptoAgent**: BTC, ETH futures on Binance/Bybit
- **ForexAgent**: Major/minor pairs on OANDA
- **FuturesAgent**: ES, NQ, YM on Interactive Brokers

### Risk Manager
Monitors portfolio-wide risk:
- Position size limits
- Daily loss limits
- Correlation exposure
- Emergency stop functionality

### Strategy Evaluator
Evaluates 8 trading strategies:
1. Momentum/Trend Following
2. Mean Reversion
3. Scalping
4. News/Sentiment
5. Volatility Breakout
6. Grid Trading
7. Arbitrage
8. Session-Based

## Data Flow

1. Agents gather market data from exchanges
2. Each agent runs all 8 strategies
3. Strategy Evaluator calculates weighted consensus
4. Agent sends signal to OpenClaw
5. OpenClaw aggregates signals from all agents
6. OpenClaw makes final decision
7. Command sent to appropriate agent for execution
8. Trade logged to database
9. Risk Manager monitors portfolio

## Communication

- **Redis Pub/Sub**: Real-time agent communication
- **TimescaleDB**: Time-series market data and trade logs
- **Discord**: Real-time alerts and monitoring
