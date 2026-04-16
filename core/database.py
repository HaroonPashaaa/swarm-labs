"""
Database Layer - TimescaleDB Integration
Optimized for financial time-series data
"""

import asyncpg
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Trade record"""
    id: Optional[int]
    timestamp: datetime
    agent: str
    strategy: str
    symbol: str
    market: str  # crypto, forex, futures
    side: str    # buy, sell
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    pnl: Optional[float]
    pnl_pct: Optional[float]
    status: str  # open, closed, cancelled
    metadata: Dict[str, Any]

@dataclass
class MarketData:
    """OHLCV market data"""
    timestamp: datetime
    symbol: str
    timeframe: str  # 1m, 5m, 15m, 1h, 4h, 1d
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class AgentDecision:
    """Agent decision log"""
    timestamp: datetime
    agent: str
    market: str
    decision: str  # buy, sell, hold
    confidence: float
    strategy: str
    reasoning: str
    signals: Dict[str, Any]

class DatabaseManager:
    """TimescaleDB manager for swarm data"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def connect(self):
        """Create connection pool"""
        self.pool = await asyncpg.create_pool(self.database_url)
        logger.info("Connected to TimescaleDB")
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Disconnected from TimescaleDB")
    
    async def init_tables(self):
        """Initialize database tables"""
        async with self.pool.acquire() as conn:
            # Enable TimescaleDB extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            
            # Trades table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    agent VARCHAR(50) NOT NULL,
                    strategy VARCHAR(50) NOT NULL,
                    symbol VARCHAR(20) NOT NULL,
                    market VARCHAR(20) NOT NULL,
                    side VARCHAR(10) NOT NULL,
                    entry_price DECIMAL(20, 8) NOT NULL,
                    exit_price DECIMAL(20, 8),
                    quantity DECIMAL(20, 8) NOT NULL,
                    pnl DECIMAL(20, 8),
                    pnl_pct DECIMAL(10, 4),
                    status VARCHAR(20) NOT NULL,
                    metadata JSONB
                );
            """)
            
            # Convert to hypertable
            await conn.execute("""
                SELECT create_hypertable('trades', 'timestamp', 
                    if_not_exists => TRUE, migrate_data => TRUE);
            """)
            
            # Market data table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    timestamp TIMESTAMPTZ NOT NULL,
                    symbol VARCHAR(20) NOT NULL,
                    timeframe VARCHAR(10) NOT NULL,
                    open DECIMAL(20, 8) NOT NULL,
                    high DECIMAL(20, 8) NOT NULL,
                    low DECIMAL(20, 8) NOT NULL,
                    close DECIMAL(20, 8) NOT NULL,
                    volume DECIMAL(30, 8) NOT NULL
                );
            """)
            
            await conn.execute("""
                SELECT create_hypertable('market_data', 'timestamp',
                    if_not_exists => TRUE, migrate_data => TRUE);
            """)
            
            # Agent decisions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_decisions (
                    timestamp TIMESTAMPTZ NOT NULL,
                    agent VARCHAR(50) NOT NULL,
                    market VARCHAR(20) NOT NULL,
                    decision VARCHAR(10) NOT NULL,
                    confidence DECIMAL(5, 4) NOT NULL,
                    strategy VARCHAR(50) NOT NULL,
                    reasoning TEXT,
                    signals JSONB
                );
            """)
            
            await conn.execute("""
                SELECT create_hypertable('agent_decisions', 'timestamp',
                    if_not_exists => TRUE, migrate_data => TRUE);
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_trades_agent ON trades (agent, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades (symbol, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data (symbol, timeframe, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_decisions_agent ON agent_decisions (agent, timestamp DESC);
            """)
            
            logger.info("Database tables initialized")
    
    async def log_trade(self, trade: Trade) -> int:
        """Log a trade to database"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO trades (timestamp, agent, strategy, symbol, market, side,
                    entry_price, exit_price, quantity, pnl, pnl_pct, status, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING id
            """, trade.timestamp, trade.agent, trade.strategy, trade.symbol,
                trade.market, trade.side, trade.entry_price, trade.exit_price,
                trade.quantity, trade.pnl, trade.pnl_pct, trade.status, 
                json.dumps(trade.metadata))
            return row['id']
    
    async def log_market_data(self, data: MarketData):
        """Log market data"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO market_data (timestamp, symbol, timeframe, open, high, low, close, volume)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (timestamp, symbol, timeframe) DO NOTHING
            """, data.timestamp, data.symbol, data.timeframe,
                data.open, data.high, data.low, data.close, data.volume)
    
    async def log_agent_decision(self, decision: AgentDecision):
        """Log agent decision"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO agent_decisions (timestamp, agent, market, decision,
                    confidence, strategy, reasoning, signals)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, decision.timestamp, decision.agent, decision.market,
                decision.decision, decision.confidence, decision.strategy,
                decision.reasoning, json.dumps(decision.signals))
    
    async def get_recent_trades(self, agent: str = None, limit: int = 100) -> List[Trade]:
        """Get recent trades"""
        async with self.pool.acquire() as conn:
            if agent:
                rows = await conn.fetch("""
                    SELECT * FROM trades WHERE agent = $1
                    ORDER BY timestamp DESC LIMIT $2
                """, agent, limit)
            else:
                rows = await conn.fetch("""
                    SELECT * FROM trades
                    ORDER BY timestamp DESC LIMIT $1
                """, limit)
            return [Trade(**row) for row in rows]
    
    async def get_performance_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get trading performance statistics"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(pnl) as total_pnl,
                    AVG(pnl_pct) as avg_pnl_pct,
                    MAX(pnl) as best_trade,
                    MIN(pnl) as worst_trade
                FROM trades
                WHERE timestamp > NOW() - INTERVAL '%s days'
            """ % days)
            return dict(row)
