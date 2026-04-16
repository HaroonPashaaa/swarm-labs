"""
Tests for OpenClaw orchestrator
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from openclaw.core import OpenClaw, SwarmConsensus
from agents.base_agent import Signal

@pytest.fixture
def openclaw():
    """Create OpenClaw instance for testing"""
    oc = OpenClaw()
    oc.db = AsyncMock()
    oc.bus = Mock()
    return oc

@pytest.mark.asyncio
async def test_calculate_consensus_buy(openclaw):
    """Test consensus calculation with buy signals"""
    signals = [
        Signal('crypto_agent', 'crypto', 'BTC/USDT', 'buy', 0.8, 'momentum', 'test', {}, datetime.utcnow()),
        Signal('forex_agent', 'crypto', 'BTC/USDT', 'buy', 0.7, 'scalping', 'test', {}, datetime.utcnow()),
        Signal('futures_agent', 'crypto', 'BTC/USDT', 'hold', 0.6, 'mean_reversion', 'test', {}, datetime.utcnow())
    ]
    
    consensus = openclaw._calculate_consensus(signals)
    
    assert consensus.action == 'buy'
    assert consensus.consensus_pct > 0.5
    assert 'crypto_agent' in consensus.participating_agents
    assert 'forex_agent' in consensus.participating_agents

@pytest.mark.asyncio
async def test_calculate_consensus_sell(openclaw):
    """Test consensus calculation with sell signals"""
    signals = [
        Signal('crypto_agent', 'crypto', 'BTC/USDT', 'sell', 0.9, 'momentum', 'test', {}, datetime.utcnow()),
        Signal('forex_agent', 'crypto', 'BTC/USDT', 'sell', 0.8, 'scalping', 'test', {}, datetime.utcnow()),
    ]
    
    consensus = openclaw._calculate_consensus(signals)
    
    assert consensus.action == 'sell'
    assert consensus.confidence > 0.8

@pytest.mark.asyncio
async def test_calculate_consensus_hold(openclaw):
    """Test consensus calculation with no clear winner"""
    signals = [
        Signal('crypto_agent', 'crypto', 'BTC/USDT', 'buy', 0.5, 'momentum', 'test', {}, datetime.utcnow()),
        Signal('forex_agent', 'crypto', 'BTC/USDT', 'sell', 0.5, 'scalping', 'test', {}, datetime.utcnow()),
    ]
    
    consensus = openclaw._calculate_consensus(signals)
    
    # Should default to hold with low confidence
    assert consensus.action == 'hold' or consensus.consensus_pct < 0.6

@pytest.mark.asyncio
async def test_check_risk_limits_stop_trading(openclaw):
    """Test that trading stops when daily loss limit hit"""
    openclaw.daily_pnl = -1500  # Beyond limit
    openclaw.daily_loss_limit = -1000
    
    # Should trigger emergency stop
    openclaw._emergency_stop = AsyncMock()
    await openclaw._check_risk_limits()
    
    openclaw._emergency_stop.assert_called_once()

@pytest.mark.asyncio
async def test_signal_to_dict(openclaw):
    """Test signal serialization"""
    signal = Signal(
        agent='crypto_agent',
        market='crypto',
        symbol='BTC/USDT',
        action='buy',
        confidence=0.85,
        strategy='momentum',
        reasoning='Strong uptrend',
        metadata={'rsi': 65},
        timestamp=datetime.utcnow()
    )
    
    result = openclaw._signal_to_dict(signal)
    
    assert result['agent'] == 'crypto_agent'
    assert result['action'] == 'buy'
    assert result['confidence'] == 0.85
    assert 'timestamp' in result
