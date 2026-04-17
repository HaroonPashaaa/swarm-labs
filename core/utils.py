"""
Utility functions for Wojak Capital
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

def format_currency(value: float, currency: str = 'USD') -> str:
    """Format currency value"""
    return f"{currency} ${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format percentage"""
    return f"{value * 100:.2f}%"

def calculate_drawdown(equity_curve: List[float]) -> float:
    """Calculate maximum drawdown from equity curve"""
    if not equity_curve:
        return 0.0
    
    peak = equity_curve[0]
    max_drawdown = 0
    
    for value in equity_curve:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        max_drawdown = max(max_drawdown, drawdown)
    
    return max_drawdown

def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate annualized Sharpe ratio"""
    if not returns or len(returns) < 2:
        return 0.0
    
    excess_returns = [r - risk_free_rate / 252 for r in returns]  # Daily
    mean_return = np.mean(excess_returns)
    std_return = np.std(excess_returns)
    
    if std_return == 0:
        return 0.0
    
    sharpe = mean_return / std_return * np.sqrt(252)  # Annualize
    return sharpe

def calculate_win_rate(trades: List[Dict]) -> float:
    """Calculate win rate from trades"""
    if not trades:
        return 0.0
    
    winning_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
    return winning_trades / len(trades)

def calculate_profit_factor(trades: List[Dict]) -> float:
    """Calculate profit factor (gross profit / gross loss)"""
    gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
    gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0
    
    return gross_profit / gross_loss

def get_market_session(timestamp: datetime = None) -> str:
    """Determine market session from timestamp"""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    hour = timestamp.hour
    
    # Forex sessions (UTC)
    if 0 <= hour < 8:
        return 'asia'
    elif 8 <= hour < 13:
        return 'london'
    elif 13 <= hour < 22:
        return 'new_york'
    else:
        return 'low_liquidity'

def validate_symbol(symbol: str, market: str) -> bool:
    """Validate symbol format for market"""
    if market == 'crypto':
        return '/' in symbol and symbol.endswith('USDT')
    elif market == 'forex':
        return '_' in symbol and len(symbol) == 7
    elif market == 'futures':
        return symbol in ['ES', 'NQ', 'YM', 'CL', 'GC']
    return False

def calculate_position_size(account_balance: float, risk_pct: float,
                           entry_price: float, stop_price: float) -> float:
    """Calculate position size based on risk"""
    risk_amount = account_balance * risk_pct
    price_risk = abs(entry_price - stop_price)
    
    if price_risk == 0:
        return 0
    
    position_size = risk_amount / price_risk
    return position_size

def round_to_tick(value: float, tick_size: float) -> float:
    """Round value to nearest tick size"""
    return round(value / tick_size) * tick_size
