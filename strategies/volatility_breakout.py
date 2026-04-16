"""
Volatility Breakout Strategy
Trade breakouts when volatility expands
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class VolatilityBreakoutStrategy:
    """
    Volatility Breakout Strategy
    
    Detects when volatility expands beyond defined thresholds,
    indicating potential strong directional moves.
    
    Uses:
    - Bollinger Band squeeze (low volatility) followed by breakout
    - ATR expansion
    - Volume confirmation
    """
    
    def __init__(self):
        self.bb_period = 20
        self.squeeze_lookback = 10
        self.atr_period = 14
        self.volume_confirm = True
        
    def evaluate(self, market: str, symbol: str, data: Dict,
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """Evaluate volatility breakout opportunity"""
        try:
            candles = data.get('ohlcv') or data.get('candles') or data.get('historical', [])
            
            if len(candles) < self.bb_period + self.squeeze_lookback:
                return None
            
            # Extract data
            closes = [c[4] if isinstance(c, list) else c.get('close', 0) for c in candles]
            highs = [c[2] if isinstance(c, list) else c.get('high', 0) for c in candles]
            lows = [c[3] if isinstance(c, list) else c.get('low', 0) for c in candles]
            volumes = [c[5] if isinstance(c, list) else c.get('volume', 0) for c in candles]
            
            current_price = closes[-1]
            current_high = highs[-1]
            current_low = lows[-1]
            
            # Calculate Bollinger Bands
            sma = np.mean(closes[-self.bb_period:])
            std = np.std(closes[-self.bb_period:])
            
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            bandwidth = (upper_band - lower_band) / sma
            
            # Check for squeeze (low volatility period)
            recent_bandwidths = []
            for i in range(self.squeeze_lookback):
                period_closes = closes[-(self.bb_period+i):-i if i > 0 else None]
                if len(period_closes) >= self.bb_period:
                    p_std = np.std(period_closes)
                    p_sma = np.mean(period_closes)
                    p_bandwidth = (p_sma + p_std * 2 - (p_sma - p_std * 2)) / p_sma
                    recent_bandwidths.append(p_bandwidth)
            
            if not recent_bandwidths:
                return None
            
            avg_bandwidth = np.mean(recent_bandwidths)
            current_bandwidth = bandwidth
            
            # Squeeze condition: current bandwidth significantly lower than average
            is_squeeze = current_bandwidth < avg_bandwidth * 0.6
            
            # Breakout condition: price outside bands after squeeze
            is_breakout_up = current_price > upper_band and current_high > upper_band
            is_breakout_down = current_price < lower_band and current_low < lower_band
            
            if not (is_breakout_up or is_breakout_down):
                return None
            
            # Volume confirmation
            volume_confirmed = True
            if self.volume_confirm and volumes:
                avg_volume = np.mean(volumes[-10:])
                current_volume = volumes[-1]
                volume_confirmed = current_volume > avg_volume * 1.5
            
            if not volume_confirmed:
                return None
            
            # Calculate confidence
            squeeze_strength = 1 - (current_bandwidth / avg_bandwidth) if avg_bandwidth > 0 else 0
            breakout_magnitude = abs(current_price - sma) / std if std > 0 else 0
            
            confidence = (squeeze_strength * 0.4 + min(breakout_magnitude / 3, 1.0) * 0.6)
            
            if is_breakout_up:
                action = 'buy'
                reasoning = f"Volatility breakout UP after squeeze. Bandwidth contracted {squeeze_strength:.1%}, now expanding. Volume {current_volume/avg_volume:.1f}x average."
            else:
                action = 'sell'
                reasoning = f"Volatility breakout DOWN after squeeze. Bandwidth contracted {squeeze_strength:.1%}, now expanding. Volume {current_volume/avg_volume:.1f}x average."
            
            return {
                'strategy_name': 'volatility_breakout',
                'action': action,
                'confidence': min(confidence, 1.0),
                'reasoning': reasoning,
                'indicators': {
                    'squeeze': is_squeeze,
                    'bandwidth': current_bandwidth,
                    'avg_bandwidth': avg_bandwidth,
                    'breakout_magnitude': breakout_magnitude,
                    'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in volatility breakout strategy: {e}")
            return None
