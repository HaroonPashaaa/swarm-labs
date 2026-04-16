"""
Scalping Strategy
High-frequency entries during high liquidity windows
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ScalpingStrategy:
    """
    Scalping Strategy
    
    Rapid high-frequency trades during high liquidity periods.
    Targets small price movements with tight stops.
    
    Uses:
    - Order book imbalance
    - Microstructure patterns
    - Volume spikes
    - Session-based timing
    """
    
    def __init__(self):
        self.profit_target = 0.002  # 0.2%
        self.stop_loss = 0.001      # 0.1%
        self.max_hold_time = 60     # 60 seconds max
        self.min_volume_ratio = 1.5  # 1.5x average volume
        
    def evaluate(self, market: str, symbol: str, data: Dict,
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """Evaluate scalping opportunity"""
        try:
            # Check if we're in a suitable session for scalping
            if context:
                session = context.get('session', '')
                # Best for high liquidity sessions
                if session in ['london_ny_overlap', 'regular_hours', 'opening_range']:
                    session_boost = 1.2
                elif session in ['asia', 'low_liquidity']:
                    return None  # Skip low liquidity
                else:
                    session_boost = 1.0
            else:
                session_boost = 1.0
            
            # Get order book data
            orderbook = data.get('orderbook')
            if not orderbook:
                return None
            
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            if len(bids) < 5 or len(asks) < 5:
                return None
            
            # Calculate order book imbalance
            bid_volume = sum(b[1] for b in bids[:5])
            ask_volume = sum(a[1] for a in asks[:5])
            
            if bid_volume == 0 or ask_volume == 0:
                return None
            
            imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
            
            # Volume check
            volume_data = data.get('volume_profile', {})
            current_volume = volume_data.get('avg_volume', 0)
            avg_volume = volume_data.get('avg_volume', current_volume)
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio < self.min_volume_ratio:
                return None
            
            # Determine signal
            if imbalance > 0.3:  # Strong buying pressure
                action = 'buy'
                strength = abs(imbalance)
            elif imbalance < -0.3:  # Strong selling pressure
                action = 'sell'
                strength = abs(imbalance)
            else:
                return None
            
            # Calculate confidence
            confidence = min(strength * session_boost * (volume_ratio / 2), 1.0)
            
            best_bid = bids[0][0]
            best_ask = asks[0][0]
            spread = (best_ask - best_bid) / best_bid
            
            reasoning = f"Scalping {action.upper()}: Order book imbalance {imbalance:.2f}, "
            reasoning += f"volume {volume_ratio:.1f}x average, spread {spread:.4%}. "
            reasoning += f"Target {self.profit_target:.2%}, stop {self.stop_loss:.2%}"
            
            return {
                'strategy_name': 'scalping',
                'action': action,
                'confidence': confidence,
                'reasoning': reasoning,
                'indicators': {
                    'imbalance': imbalance,
                    'bid_volume': bid_volume,
                    'ask_volume': ask_volume,
                    'volume_ratio': volume_ratio,
                    'spread': spread,
                    'profit_target': self.profit_target,
                    'stop_loss': self.stop_loss,
                    'max_hold_time': self.max_hold_time
                }
            }
            
        except Exception as e:
            logger.error(f"Error in scalping strategy: {e}")
            return None
