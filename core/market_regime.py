"""
Market Regime Detector
Detect current market conditions
"""

import logging
from typing import Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)

class MarketRegimeDetector:
    """Detect market regime (trending, ranging, volatile)"""
    
    def __init__(self):
        self.lookback = 50
        
    def detect_regime(self, data: Dict) -> str:
        """Detect current market regime"""
        candles = data.get('ohlcv') or data.get('candles') or []
        
        if len(candles) < self.lookback:
            return 'unknown'
        
        closes = [c[4] if isinstance(c, list) else c.get('close', 0) for c in candles[-self.lookback:]]
        
        # Calculate metrics
        volatility = self._calculate_volatility(closes)
        adx = self._calculate_adx(closes)
        
        # Classify regime
        if adx > 25 and volatility > 0.02:
            return 'trending'
        elif adx < 20 and volatility < 0.015:
            return 'ranging'
        elif volatility > 0.03:
            return 'volatile'
        else:
            return 'mixed'
    
    def _calculate_volatility(self, closes: list) -> float:
        """Calculate price volatility"""
        if len(closes) < 2:
            return 0
        
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        return np.std(returns)
    
    def _calculate_adx(self, closes: list, period: int = 14) -> float:
        """Simplified ADX calculation"""
        if len(closes) < period + 1:
            return 0
        
        # Simplified - use price momentum as proxy
        momentum = abs(closes[-1] - closes[-period]) / closes[-period]
        return momentum * 100
    
    def get_optimal_strategy(self, regime: str) -> str:
        """Get optimal strategy for regime"""
        strategy_map = {
            'trending': 'momentum',
            'ranging': 'grid_trading',
            'volatile': 'scalping',
            'mixed': 'mean_reversion'
        }
        
        return strategy_map.get(regime, 'momentum')
