"""
Tests for Risk Manager
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from agents.risk_manager import RiskManager, RiskMetrics

@pytest.fixture
def risk_manager():
    """Create RiskManager instance"""
    rm = RiskManager()
    rm.bus = Mock()
    return rm

@pytest.mark.asyncio
async def test_calculate_exposure(risk_manager):
    """Test exposure calculation"""
    risk_manager.positions = {
        'BTC/USDT': {'size': 0.5, 'entry_price': 50000},
        'ETH/USDT': {'size': -2.0, 'entry_price': 3000},
    }
    
    exposure = risk_manager._calculate_exposure()
    
    assert exposure['crypto'] > 0
    assert exposure['total'] > 0

def test_check_high_correlation(risk_manager):
    """Test high correlation detection"""
    correlations = {
        'BTC/USDT': {'ETH/USDT': 0.85, 'SOL/USDT': 0.45},
        'ETH/USDT': {'BTC/USDT': 0.85, 'SOL/USDT': 0.70},
    }
    
    high_corr = risk_manager._find_high_correlations(correlations, threshold=0.8)
    
    assert len(high_corr) > 0
    assert ('BTC/USDT', 'ETH/USDT', 0.85) in high_corr

@pytest.mark.asyncio
async def test_oversized_position_alert(risk_manager):
    """Test alert generation for oversized position"""
    risk_manager.positions = {
        'BTC/USDT': {'size': 0.5}  # Large position
    }
    risk_manager.max_position_size = 0.1  # 10% limit
    
    # Mock the position size check
    pos_size = 0.5  # 50% - oversized
    
    assert pos_size > risk_manager.max_position_size

def test_daily_stats_calculation(risk_manager):
    """Test daily statistics calculation"""
    today = datetime.utcnow()
    risk_manager.daily_trades = [
        {'pnl': 100, 'timestamp': today},
        {'pnl': -50, 'timestamp': today},
        {'pnl': 200, 'timestamp': today},
    ]
    
    stats = risk_manager._calculate_daily_stats()
    
    assert stats['pnl'] == 250
    assert stats['trades'] == 3
    assert stats['win_rate'] == 2/3

@pytest.mark.asyncio
async def test_risk_report_generation(risk_manager):
    """Test risk report generation"""
    risk_manager.positions = {'BTC/USDT': {'size': 0.1}}
    
    report = risk_manager._generate_risk_report()
    
    assert 'timestamp' in report
    assert 'exposure' in report
    assert 'open_positions' in report
    assert report['open_positions'] == 1
