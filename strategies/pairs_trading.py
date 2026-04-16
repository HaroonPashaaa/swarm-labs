"""
Pairs Trading Strategy
Statistical arbitrage between correlated assets
"""

import logging
from typing import Dict, Any, Optional, Tuple
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

class PairsTradingStrategy:
    """
    Pairs Trading Strategy
    
    Trade the spread between two correlated assets.
    When spread deviates from mean, bet on reversion.
    
    Example: Long GLD / Short SLV when gold/silver ratio is extreme
    """
    
    def __init__(self):
        self.lookback = 60
        self.entry_zscore = 2.0
        self.exit_zscore = 0.5
        self.correlation_threshold = 0.8
        
    def evaluate(self, market: str, symbol: str, data: Dict,
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """Evaluate pairs trading opportunity"""
        try:
            # Need pair data in context
            if not context or 'pair_symbol' not in context:
                return None
            
            pair_symbol = context['pair_symbol']
            pair_data = context.get('pair_data', {})
            
            if not pair_data:
                return None
            
            # Get price series
            series1 = self._get_price_series(data)
            series2 = self._get_price_series(pair_data)
            
            if len(series1) < self.lookback or len(series2) < self.lookback:
                return None
            
            # Calculate correlation
            correlation = np.corrcoef(series1[-self.lookback:], series2[-self.lookback:])[0, 1]
            
            if correlation < self.correlation_threshold:
                return None
            
            # Calculate spread
            spread = np.array(series1) - np.array(series2)
            
            # Calculate z-score of spread
            spread_mean = np.mean(spread[-self.lookback:])
            spread_std = np.std(spread[-self.lookback:])
            
            if spread_std == 0:
                return None
            
            current_spread = spread[-1]
            zscore = (current_spread - spread_mean) / spread_std
            
            # Generate signal based on z-score
            if abs(zscore) < self.entry_zscore:
                return None
            
            if zscore > self.entry_zscore:
                # Spread too high - short asset1, long asset2
                action = 'pairs_short_spread'
                confidence = min(abs(zscore) / 3, 0.95)
                reasoning = f"Spread z-score {zscore:.2f}. Short {symbol}, long {pair_symbol}."
            else:
                # Spread too low - long asset1, short asset2
                action = 'pairs_long_spread'
                confidence = min(abs(zscore) / 3, 0.95)
                reasoning = f"Spread z-score {zscore:.2f}. Long {symbol}, short {pair_symbol}."
            
            return {
                'strategy_name': 'pairs_trading',
                'action': action,
                'confidence': confidence,
                'reasoning': reasoning,
                'indicators': {
                    'correlation': correlation,
                    'spread': current_spread,
                    'spread_mean': spread_mean,
                    'spread_std': spread_std,
                    'zscore': zscore,
                    'pair_symbol': pair_symbol
                }
            }
            
        except Exception as e:
            logger.error(f"Error in pairs trading strategy: {e}")
            return None
    
    def _get_price_series(self, data: Dict) -> list:
        """Extract price series from data"""
        candles = data.get('ohlcv') or data.get('candles') or []
        return [c[4] if isinstance(c, list) else c.get('close', 0) for c in candles]
