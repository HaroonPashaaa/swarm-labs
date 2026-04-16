"""
Tests for OpenClaw decision logic
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from openclaw.core import OpenClaw, SwarmConsensus

@pytest.fixture
def openclaw():
    oc = OpenClaw()
    oc.db = AsyncMock()
    oc.bus = Mock()
    return oc

def test_consensus_calculation_unanimous(openclaw):
    """Test when all agents agree"""
    from agents.base_agent import Signal
    
    signals = [
        Signal('a1', 'crypto', 'BTC', 'buy', 0.9, 'momentum', '', {}, datetime.utcnow()),
        Signal('a2', 'crypto', 'BTC', 'buy', 0.85, 'mean_reversion', '', {}, datetime.utcnow()),
        Signal('a3', 'crypto', 'BTC', 'buy', 0.88, 'scalping', '', {}, datetime.utcnow())
    ]
    
    consensus = openclaw._calculate_consensus(signals)
    
    assert consensus.action == 'buy'
    assert consensus.consensus_pct > 0.9
    assert consensus.confidence > 0.85

def test_consensus_calculation_split(openclaw):
    """Test when agents disagree"""
    from agents.base_agent import Signal
    
    signals = [
        Signal('a1', 'crypto', 'BTC', 'buy', 0.8, 'momentum', '', {}, datetime.utcnow()),
        Signal('a2', 'crypto', 'BTC', 'sell', 0.7, 'mean_reversion', '', {}, datetime.utcnow())
    ]
    
    consensus = openclaw._calculate_consensus(signals)
    
    # Should pick the higher confidence side
    assert consensus.action in ['buy', 'sell']

@pytest.mark.asyncio
async def test_make_decision_buy(openclaw):
    """Test buy decision"""
    consensus = SwarmConsensus('buy', 0.85, 0.75, ['a1', 'a2'], {}, {})
    
    # Mock the pending signals
    openclaw.pending_signals = {'crypto:BTC': []}
    
    await openclaw._make_decision('crypto:BTC', consensus, [])
    
    # Should update tracking
    assert 'crypto:BTC' in openclaw.last_decisions

@pytest.mark.asyncio
async def test_emergency_stop(openclaw):
    """Test emergency stop triggers"""
    openclaw._emergency_stop = AsyncMock()
    
    # Set daily loss beyond limit
    openclaw.daily_pnl = -2000
    openclaw.daily_loss_limit = -1000
    
    await openclaw._check_risk_limits()
    
    openclaw._emergency_stop.assert_called_once()

def test_status_report(openclaw):
    """Test status report generation"""
    openclaw.running = True
    openclaw.daily_pnl = 500
    openclaw.open_positions = 3
    
    status = openclaw.get_status()
    
    assert status['status'] == 'running'
    assert status['daily_pnl'] == 500
    assert status['open_positions'] == 3
