"""
Mean Reversion Strategy
Fade overextended moves when price deviates from average
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class MeanReversionStrategy:
    """
    Mean Reversion Strategy
    
    Identifies when price has deviated significantly from its average
    and anticipates a return to the mean.
    
    Uses:
    - Bollinger Bands for deviation measurement
    - RSI for overbought/oversold
    - Z-score for statistical significance
    """
    
    def __init__(self):
        self.bb_period = 20
        self.bb_std = 2.0
        self.rsi_period = 14
        self.zscore_threshold = 2.0
        
    def evaluate(self, market: str, symbol: str, data: Dict,
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """Evaluate mean reversion opportunity"""
        try:
            # Get price data
            candles = data.get('ohlcv') or data.get('candles') or data.get('historical', [])
            
            if len(candles) < self.bb_period + 5:
                return None
            
            # Extract closes
            closes = [c[4] if isinstance(c, list) else c.get('close', 0) for c in candles]
            highs = [c[2] if isinstance(c, list) else c.get('high', 0) for c in candles]
            lows = [c[3] if isinstance(c, list) else c.get('low', 0) for c in candles]
            
            current_price = closes[-1]
            
            # Calculate Bollinger Bands
            sma = sum(closes[-self.bb_period:]) / self.bb_period
            std = np.std(closes[-self.bb_period:]) if len(closes) >= self.bb_period else 0
            
            upper_band = sma + (std * self.bb_std)
            lower_band = sma - (std * self.bb_std)
            
            # Calculate Z-score
            zscore = (current_price - sma) / std if std > 0 else 0
            
            # Calculate RSI
            rsi = self._calculate_rsi(closes)
            
            # Determine if price is overextended
            deviation_from_mean = abs(current_price - sma) / sma
            
            # Signal conditions
            is_overbought = current_price > upper_band and zscore > self.zscore_threshold
            is_oversold = current_price < lower_band and zscore < -self.zscore_threshold
            
            if not (is_overbought or is_oversold):
                return None
            
            # Check RSI confirmation
            rsi_confirm = rsi > 70 if is_overbought else rsi < 30
            
            if not rsi_confirm:
                return None
            
            # Calculate signal strength
            deviation_strength = min(abs(zscore) / 3.0, 1.0)  # Normalize to 0-1
            rsi_strength = (rsi - 70) / 30 if is_overbought else (30 - rsi) / 30
            
            confidence = (deviation_strength + rsi_strength) / 2
            
            # Determine action
            if is_overbought:
                action = 'sell'
                target = sma
                stop = current_price + (std * 1.5)
                reasoning = f"Overbought: Price {deviation_from_mean:.2%} above mean, Z-score {zscore:.2f}, RSI {rsi:.1f}"
            else:
                action = 'buy'
                target = sma
                stop = current_price - (std * 1.5)
                reasoning = f"Oversold: Price {deviation_from_mean:.2%} below mean, Z-score {zscore:.2f}, RSI {rsi:.1f}"
            
            return {
                'strategy_name': 'mean_reversion',
                'action': action,
                'confidence': confidence,
                'reasoning': reasoning,
                'indicators': {
                    'sma': sma,
                    'upper_band': upper_band,
                    'lower_band': lower_band,
                    'zscore': zscore,
                    'rsi': rsi,
                    'deviation': deviation_from_mean,
                    'target': target,
                    'stop': stop
                }
            }
            
        except Exception as e:
            logger.error(f"Error in mean reversion strategy: {e}")
            return None
    
    def _calculate_rsi(self, closes: list) -> float:
        """Calculate Relative Strength Index"""
        if len(closes) < self.rsi_period + 1:
            return 50
        
        # Calculate price changes
        changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        
        # Get recent changes
        recent_changes = changes[-self.rsi_period:]
        
        # Separate gains and losses
        gains = [max(c, 0) for c in recent_changes]
        losses = [abs(min(c, 0)) for c in recent_changes]
        
        # Calculate averages
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        # Calculate RS and RSI
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
