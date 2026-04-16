"""
Tests for Database Operations
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from core.database import DatabaseManager, Trade, AgentDecision, MarketData

@pytest.fixture
def db():
    """Create mock database manager"""
    db = DatabaseManager('postgresql://test:test@localhost/test')
    db.pool = MagicMock()
    return db

@pytest.mark.asyncio
async def test_log_trade(db):
    """Test trade logging"""
    trade = Trade(
        id=None,
        timestamp=datetime.utcnow(),
        agent='crypto_agent',
        strategy='momentum',
        symbol='BTC/USDT',
        market='crypto',
        side='buy',
        entry_price=50000,
        exit_price=None,
        quantity=0.1,
        pnl=None,
        pnl_pct=None,
        status='open',
        metadata={'test': True}
    )
    
    # Mock database response
    mock_conn = AsyncMock()
    mock_conn.fetchrow = AsyncMock(return_value={'id': 1})
    
    db.pool.acquire = MagicMock()
    db.pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    db.pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    
    trade_id = await db.log_trade(trade)
    assert trade_id == 1

@pytest.mark.asyncio
async def test_log_agent_decision(db):
    """Test agent decision logging"""
    decision = AgentDecision(
        timestamp=datetime.utcnow(),
        agent='crypto_agent',
        market='crypto',
        decision='buy',
        confidence=0.85,
        strategy='momentum',
        reasoning='Strong uptrend',
        signals={'rsi': 65}
    )
    
    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock()
    
    db.pool.acquire = MagicMock()
    db.pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    db.pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    
    await db.log_agent_decision(decision)
    mock_conn.execute.assert_called_once()
