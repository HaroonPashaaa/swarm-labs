"""
Momentum Strategy
Trend following using ATR and moving averages
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MomentumSignal:
    trend: str  # bullish, bearish, neutral
    strength: float  # 0.0 to 1.0
    atr: float
    entry_price: float
    stop_loss: float
    take_profit: float

class MomentumStrategy:
    """
    Momentum/Trend Following Strategy
    
    Uses:
    - Moving averages for trend direction
    - ATR for volatility and position sizing
    - Price momentum for entry timing
    """
    
    def __init__(self):
        self.lookback = 20
        self.fast_ma_period = 9
        self.slow_ma_period = 21
        self.atr_period = 14
        
    def evaluate(self, market: str, symbol: str, data: Dict, 
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """
        Evaluate momentum strategy
        
        Returns StrategyResult-compatible dict or None
        """
        try:
            # Get price data
            if 'ohlcv' in data or 'candles' in data or 'historical' in data:
                candles = data.get('ohlcv') or data.get('candles') or data.get('historical', [])
            else:
                return None
            
            if len(candles) < self.slow_ma_period + 5:
                return None
            
            # Extract closes
            closes = [c[4] if isinstance(c, list) else c.get('close', 0) for c in candles]
            highs = [c[2] if isinstance(c, list) else c.get('high', 0) for c in candles]
            lows = [c[3] if isinstance(c, list) else c.get('low', 0) for c in candles]
            
            current_price = closes[-1]
            
            # Calculate moving averages
            fast_ma = sum(closes[-self.fast_ma_period:]) / self.fast_ma_period
            slow_ma = sum(closes[-self.slow_ma_period:]) / self.slow_ma_period
            
            # Calculate ATR
            atr = self._calculate_atr(highs, lows, closes)
            
            # Determine trend
            if fast_ma > slow_ma * 1.001:  # 0.1% buffer
                trend = 'bullish'
            elif fast_ma < slow_ma * 0.999:
                trend = 'bearish'
            else:
                trend = 'neutral'
            
            # Calculate momentum strength
            momentum = self._calculate_momentum(closes)
            
            # Calculate trend strength (ADX-like)
            trend_strength = self._calculate_trend_strength(closes, highs, lows)
            
            # Overall signal strength
            if trend == 'neutral':
                return None
            
            strength = (momentum + trend_strength) / 2
            
            # Require minimum strength
            if strength < 0.5:
                return None
            
            # Calculate entry, stop, and target
            entry = current_price
            
            if trend == 'bullish':
                stop_loss = entry - (atr * 2)
                take_profit = entry + (atr * 3)
                action = 'buy'
            else:
                stop_loss = entry + (atr * 2)
                take_profit = entry - (atr * 3)
                action = 'sell'
            
            # Build reasoning
            reasoning = f"{trend.upper()} trend: Fast MA ({fast_ma:.2f}) vs Slow MA ({slow_ma:.2f}). "
            reasoning += f"Momentum: {momentum:.2f}, Trend Strength: {trend_strength:.2f}. "
            reasoning += f"ATR-based stop at {stop_loss:.2f}, target at {take_profit:.2f}"
            
            return {
                'strategy_name': 'momentum',
                'action': action,
                'confidence': strength,
                'reasoning': reasoning,
                'indicators': {
                    'trend': trend,
                    'fast_ma': fast_ma,
                    'slow_ma': slow_ma,
                    'atr': atr,
                    'momentum': momentum,
                    'trend_strength': trend_strength,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                }
            }
            
        except Exception as e:
            logger.error(f"Error in momentum strategy: {e}")
            return None
    
    def _calculate_atr(self, highs: list, lows: list, closes: list) -> float:
        """Calculate Average True Range"""
        if len(highs) < 2 or len(lows) < 2:
            return 0
        
        tr_values = []
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr_values.append(max(tr1, tr2, tr3))
        
        if not tr_values:
            return 0
        
        # Use most recent ATR period
        recent_tr = tr_values[-self.atr_period:]
        return sum(recent_tr) / len(recent_tr)
    
    def _calculate_momentum(self, closes: list) -> float:
        """Calculate price momentum (0-1 scale)"""
        if len(closes) < 10:
            return 0
        
        # Rate of change over last 10 periods
        roc = (closes[-1] - closes[-10]) / closes[-10]
        
        # Normalize to 0-1 scale (assuming max 10% move)
        normalized = min(abs(roc) / 0.10, 1.0)
        
        return normalized
    
    def _calculate_trend_strength(self, closes: list, highs: list, lows: list) -> float:
        """Calculate trend strength (ADX-like, 0-1 scale)"""
        if len(closes) < 14:
            return 0
        
        # Simple trend strength: consistency of direction
        directions = []
        for i in range(1, min(14, len(closes))):
            if closes[i] > closes[i-1]:
                directions.append(1)
            elif closes[i] < closes[i-1]:
                directions.append(-1)
            else:
                directions.append(0)
        
        if not directions:
            return 0
        
        # Calculate consistency
        positive = sum(1 for d in directions if d > 0)
        negative = sum(1 for d in directions if d < 0)
        
        # Stronger trend = higher percentage in one direction
        consistency = max(positive, negative) / len(directions)
        
        return consistency
