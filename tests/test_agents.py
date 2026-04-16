"""
Tests for Market Agents
"""

import pytest
from unittest.mock import Mock, AsyncMock

from agents.crypto_agent import CryptoAgent
from agents.forex_agent import ForexAgent

@pytest.fixture
def crypto_agent():
    agent = CryptoAgent()
    agent.binance = Mock()
    agent.bybit = Mock()
    return agent

@pytest.fixture
def forex_agent():
    agent = ForexAgent()
    agent.oanda = Mock()
    return agent

@pytest.mark.asyncio
async def test_crypto_agent_gather_data(crypto_agent):
    """Test crypto agent data gathering"""
    # Mock exchange responses
    crypto_agent.binance.fetch_ohlcv = AsyncMock(return_value=[
        [1, 50000, 51000, 49000, 50500, 1000]
    ])
    crypto_agent.bybit.fetch_ohlcv = AsyncMock(return_value=[
        [1, 50000, 51000, 49000, 50500, 1000]
    ])
    
    data = await crypto_agent.gather_data()
    
    assert 'symbols' in data
    assert 'positions' in data

@pytest.mark.asyncio
async def test_forex_agent_session_detection(forex_agent):
    """Test forex agent session detection"""
    session = forex_agent._determine_session()
    
    assert session in ['asia', 'london', 'new_york', 'overlap', 'low_liquidity']

def test_crypto_arbitrage_detection(crypto_agent):
    """Test arbitrage detection"""
    ob1 = {'bids': [[50000, 1]], 'asks': [[50100, 1]]}
    ob2 = {'bids': [[50200, 1]], 'asks': [[50300, 1]]}
    
    arb = crypto_agent._detect_arbitrage(ob1, ob2)
    
    assert arb is not None
    assert 'profit_pct' in arb

def test_forex_session_metrics(forex_agent):
    """Test session metrics calculation"""
    candles = [
        {'time': 1, 'open': 1.1, 'high': 1.11, 'low': 1.09, 'close': 1.10, 'volume': 1000}
        for _ in range(30)
    ]
    
    metrics = forex_agent._calculate_session_metrics(candles, 'london')
    
    assert 'avg_volume' in metrics
    assert 'avg_range' in metrics
