# Wojak Capital - Twitter Article
## Professional Thread for X (Twitter)

---

**Tweet 1/20:**
Building in public: For the past 6 months I've been developing Wojak Capital, a production-grade multi-agent AI trading system that monitors crypto futures, forex, and stock futures simultaneously.

124 files. 6,000+ lines of Python. 12 trading strategies. 7 exchange integrations.

Thread on the architecture and philosophy behind building institutional-grade trading infrastructure 👇

---

**Tweet 2/20:**
The Problem:

Most retail traders fail because they:
• Trade emotionally (FOMO, panic selling)
• Can't monitor multiple markets 24/7
• Lack systematic risk management
• Have no strategy for different market regimes

I wanted to build something that removes emotion from trading entirely.

---

**Tweet 3/20:**
Core Philosophy:

Wojak Capital operates on three principles:

1. SYSTEMATIC - Every decision is algorithmic, no emotion
2. MULTI-MARKET - Diversification across uncorrelated assets
3. ADAPTIVE - Strategies adjust to market conditions in real-time

The name? Because when the market dips, we buy.

---

**Tweet 4/20:**
The Architecture - Multi-Agent System:

Instead of a single trading bot, Wojak Capital uses 4 specialized agents:

• CRYPTO AGENT - Binance/Bybit futures
• FOREX AGENT - OANDA major pairs
• FUTURES AGENT - Interactive Brokers (ES, NQ, YM)
• RISK MANAGER - Portfolio-wide monitoring

Each agent is an expert in their domain.

---

**Tweet 5/20:**
OpenClaw - The Central Orchestrator:

All agents report to OpenClaw, which:
• Collects signals from all market agents
• Calculates weighted consensus using confidence scores
• Makes final execution decisions
• Routes commands to appropriate agents
• Logs everything for audit trails

It's the CEO of the trading operation.

---

**Tweet 6/20:**
The 12 Trading Strategies:

1. Momentum/Trend Following
2. Mean Reversion
3. Scalping
4. News/Sentiment Analysis
5. Volatility Breakout
6. Grid Trading
7. Arbitrage
8. Session-Based Trading
9. Kelly Criterion Position Sizing
10. Pairs Trading
11. Machine Learning Signals
12. Options Flow Analysis

Each strategy has different strengths in different market conditions.

---

**Tweet 7/20:**
Strategy Selection:

The Strategy Evaluator automatically weights strategies based on:
• Current market regime (trending/ranging/volatile)
• Historical performance
• Session (Asia/London/NY)
• Volatility levels

Strategies with better recent performance get higher weights. The system adapts.

---

**Tweet 8/20:**
Consensus Mechanism:

Not all agents agree. That's fine.

OpenClaw calculates weighted consensus:
• Confidence scores from each agent
• Strategy performance weights
• Market correlation factors

Only executes when consensus > 60% and confidence > 65%.

---

**Tweet 9/20:**
Risk Management - The Unsexy But Critical Part:

Wojak Capital implements 4 layers of risk control:

1. Position Level - Max 2% per trade, hard stops
2. Strategy Level - Confidence thresholds
3. Portfolio Level - Max 20% exposure, correlation limits
4. System Level - Emergency stops, kill switches

Paper trading by default. Safety first.

---

**Tweet 10/20:**
Technical Stack:

• Python 3.11 - Core language
• TimescaleDB - Time-series data (market data, trades)
• PostgreSQL - Relational data (accounts, configs)
• Redis - Message queue for agent communication
• Docker - Deployment containerization
• CCXT - Exchange API abstraction

Built for production from day one.

---

**Tweet 11/20:**
Exchange Integrations:

• Binance Futures - Crypto perpetuals
• Bybit Futures - Crypto derivatives
• OANDA - Forex spot/CFDs
• Interactive Brokers - Stock futures
• Coinbase - Spot crypto
• Kraken - Spot and futures

Each integration handles rate limiting, authentication, and error recovery.

---

**Tweet 12/20:**
Data Infrastructure:

Time-series data is critical for trading. Wojak Capital uses:

• TimescaleDB hypertables for market data
• Automated partitioning by time
• Compression for historical data
• Real-time ingestion via WebSocket

Sub-100ms query times for recent data.

---

**Tweet 13/20:**
Communication Layer:

Agents need to coordinate. We use Redis pub/sub:

• agent:signals - Trading signals broadcast
• openclaw:commands - Execution commands
• swarm:risk - Risk alerts
• swarm:broadcast - System-wide updates

Decoupled architecture. Agents can fail independently.

---

**Tweet 14/20:**
Market Regime Detection:

The system detects current market conditions:

• TRENDING - ADX > 25, high momentum
• RANGING - Low volatility, mean-reverting
• VOLATILE - High volatility, breakout potential
• MIXED - Unclear direction

Different strategies work better in different regimes.

---

**Tweet 15/20:**
Session-Based Optimization:

Forex and futures have distinct sessions:

• ASIA (00:00-09:00 UTC) - Range trading, low volatility
• LONDON (08:00-17:00 UTC) - Breakout potential
• NEW YORK (13:00-22:00 UTC) - High liquidity
• OVERLAP (13:00-17:00 UTC) - Best opportunities

The system adjusts risk and strategy weights by session.

---

**Tweet 16/20:**
Testing Infrastructure:

13 test files covering:
• OpenClaw decision logic
• Strategy performance tracking
• Redis message passing
• Database operations
• Input validation
• Exchange client abstractions

 pytest with async support and coverage reporting.

---

**Tweet 17/20:**
What I Learned Building This:

• Rate limiting is everything (exchanges will ban you)
• Risk management matters more than alpha
• Microservices add complexity but improve resilience
• Testing asynchronous code is painful but necessary
• Docker makes deployment actually manageable

Theory vs practice is a real gap.

---

**Tweet 18/20:**
Current Status:

✅ Core architecture complete
✅ 12 strategies implemented
✅ 7 exchanges integrated
✅ Risk management layer active
✅ Docker deployment ready
✅ CI/CD pipelines configured
⏳ Live testing phase
⏳ Performance optimization

Building in public. Progress documented on GitHub.

---

**Tweet 19/20:**
Why Open Source:

I'm not selling anything. No paid courses. No Discord premium.

The code is MIT licensed because:
• I learned from open source
• Retail deserves better tools
• Community contributions improve quality
• Transparency builds trust

https://github.com/HaroonPashaaa/wojak-capital

---

**Tweet 20/20:**
About Me:

• CS @ Binghamton University
• Building @ SolaDex (DeFi on Solana)
• Previously worked on Pasha Tracker (blockchain forensics)
• Self-taught quant trading

Always learning. This project taught me more about system design, risk management, and production engineering than any class.

Questions welcome. DMs open.

/END 🧵

---

**Standalone Tweet (Pinned Alternative):**

Wojak Capital - Multi-Agent AI Trading System

🤖 4 specialized trading agents
📊 12 algorithmic strategies  
🏦 7 exchange integrations
🛡️ Multi-layer risk management
🐳 Docker deployment ready

When the market dips, we buy.

🔗 github.com/HaroonPashaaa/wojak-capital

#Trading #Crypto #AlgoTrading #OpenSource

---

**Posting Tips:**
- Post as thread (reply to yourself)
- Add screenshots of architecture diagram, code, or dashboard
- Pin the standalone tweet to your profile
- Tag relevant accounts: @BinghamtonU, @SolaDex, quant trading communities
- Use hashtags: #AlgoTrading #Crypto #Python #OpenSource #FinTech
