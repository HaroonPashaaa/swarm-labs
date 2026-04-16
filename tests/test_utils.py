"""
Tests for Core Utilities
"""

import pytest
from datetime import datetime
from core.utils import (
    format_currency,
    format_percentage,
    calculate_drawdown,
    calculate_win_rate,
    get_market_session,
    validate_symbol
)

def test_format_currency():
    """Test currency formatting"""
    assert format_currency(1234.56) == "USD $1,234.56"
    assert format_currency(1000000) == "USD $1,000,000.00"

def test_format_percentage():
    """Test percentage formatting"""
    assert format_percentage(0.1234) == "12.34%"
    assert format_percentage(0.5) == "50.00%"

def test_calculate_drawdown():
    """Test drawdown calculation"""
    equity = [100, 110, 105, 120, 100, 90, 95]
    dd = calculate_drawdown(equity)
    
    # Max drawdown should be from 120 to 90
    expected_dd = (120 - 90) / 120
    assert abs(dd - expected_dd) < 0.01

def test_calculate_win_rate():
    """Test win rate calculation"""
    trades = [
        {'pnl': 100},
        {'pnl': -50},
        {'pnl': 200},
        {'pnl': -100}
    ]
    
    win_rate = calculate_win_rate(trades)
    assert win_rate == 0.5  # 2 wins out of 4

def test_get_market_session():
    """Test market session detection"""
    # Test Asia session (UTC 02:00)
    asia_time = datetime(2026, 4, 16, 2, 0)
    assert get_market_session(asia_time) == 'asia'
    
    # Test London session (UTC 10:00)
    london_time = datetime(2026, 4, 16, 10, 0)
    assert get_market_session(london_time) == 'london'

def test_validate_symbol():
    """Test symbol validation"""
    assert validate_symbol('BTC/USDT', 'crypto') == True
    assert validate_symbol('EUR_USD', 'forex') == True
    assert validate_symbol('ES', 'futures') == True
    assert validate_symbol('INVALID', 'crypto') == False
