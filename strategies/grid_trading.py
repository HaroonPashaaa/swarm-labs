"""
Grid Trading Strategy
Deploy grid in ranging, low-volatility markets
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class GridTradingStrategy:
    """
    Grid Trading Strategy
    
    Deploys buy and sell orders at regular intervals within
    a defined price range. Profits from price oscillations.
    
    Best for: Low volatility, ranging markets
    """
    
    def __init__(self):
        self.grid_levels = 10
        self.grid_spacing_pct = 0.005  # 0.5% between grids
        self.volatility_threshold = 0.02  # Max 2% volatility for entry
        
    def evaluate(self, market: str, symbol: str, data: Dict,
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """Evaluate grid trading setup"""
        try:
            candles = data.get('ohlcv') or data.get('candles') or data.get('historical', [])
            
            if len(candles) < 20:
                return None
            
            closes = [c[4] if isinstance(c, list) else c.get('close', 0) for c in candles]
            current_price = closes[-1]
            
            # Check volatility
            volatility = self._calculate_volatility(closes)
            if volatility > self.volatility_threshold:
                return None  # Too volatile for grid
            
            # Check if ranging (not trending)
            trend = self._determine_trend(closes)
            if trend != 'ranging':
                return None
            
            # Calculate grid bounds
            recent_high = max(closes[-20:])
            recent_low = min(closes[-20:])
            range_pct = (recent_high - recent_low) / recent_low
            
            if range_pct < 0.01:  # Need at least 1% range
                return None
            
            # Set grid around current price
            grid_upper = current_price * (1 + self.grid_spacing_pct * self.grid_levels / 2)
            grid_lower = current_price * (1 - self.grid_spacing_pct * self.grid_levels / 2)
            
            # Ensure within recent range
            grid_upper = min(grid_upper, recent_high)
            grid_lower = max(grid_lower, recent_low)
            
            # Calculate confidence based on range quality
            confidence = (1 - volatility / self.volatility_threshold) * 0.8
            
            reasoning = f"Grid setup: {self.grid_levels} levels between {grid_lower:.2f} and {grid_upper:.2f}. "
            reasoning += f"Volatility {volatility:.2%} (threshold {self.volatility_threshold:.2%}). "
            reasoning += f"Current price {current_price:.2f} is in ranging mode."
            
            return {
                'strategy_name': 'grid_trading',
                'action': 'grid_setup',  # Special action for grid
                'confidence': confidence,
                'reasoning': reasoning,
                'indicators': {
                    'grid_upper': grid_upper,
                    'grid_lower': grid_lower,
                    'grid_levels': self.grid_levels,
                    'grid_spacing': self.grid_spacing_pct,
                    'volatility': volatility,
                    'range_pct': range_pct,
                    'current_price': current_price
                }
            }
            
        except Exception as e:
            logger.error(f"Error in grid trading strategy: {e}")
            return None
    
    def _calculate_volatility(self, closes: list) -> float:
        """Calculate volatility as standard deviation of returns"""
        if len(closes) < 10:
            return 1.0
        
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        return np.std(returns) if returns else 1.0
    
    def _determine_trend(self, closes: list) -> str:
        """Determine if market is trending or ranging"""
        if len(closes) < 50:
            return 'unknown'
        
        sma_20 = np.mean(closes[-20:])
        sma_50 = np.mean(closes[-50:])
        
        # Check if price oscillates around MAs
        deviation_20 = abs(closes[-1] - sma_20) / sma_20
        deviation_50 = abs(closes[-1] - sma_50) / sma_50
        
        if deviation_20 < 0.005 and deviation_50 < 0.01:
            return 'ranging'
        elif closes[-1] > sma_20 > sma_50:
            return 'uptrend'
        elif closes[-1] < sma_20 < sma_50:
            return 'downtrend'
        else:
            return 'ranging'
