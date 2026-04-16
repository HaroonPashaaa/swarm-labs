"""
Kelly Criterion Strategy
Position sizing based on edge and odds
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class KellyCriterionStrategy:
    """
    Kelly Criterion Strategy
    
    Calculates optimal position size based on:
    - Win probability (edge)
    - Win/loss ratio (odds)
    
    Formula: f* = (bp - q) / b
    Where:
    - f* = fraction of bankroll to bet
    - b = odds received on win
    - p = probability of win
    - q = probability of loss (1-p)
    """
    
    def __init__(self):
        self.lookback_period = 50
        self.kelly_fraction = 0.5  # Half-Kelly for safety
        
    def evaluate(self, market: str, symbol: str, data: Dict,
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """Evaluate using Kelly Criterion"""
        try:
            candles = data.get('ohlcv') or data.get('candles') or []
            
            if len(candles) < self.lookback_period:
                return None
            
            # Calculate historical win rate and payoff
            closes = [c[4] if isinstance(c, list) else c.get('close', 0) for c in candles[-self.lookback_period:]]
            
            wins = []
            losses = []
            
            for i in range(1, len(closes)):
                ret = (closes[i] - closes[i-1]) / closes[i-1]
                if ret > 0:
                    wins.append(ret)
                else:
                    losses.append(abs(ret))
            
            if not wins or not losses:
                return None
            
            # Calculate probabilities
            total_trades = len(wins) + len(losses)
            win_prob = len(wins) / total_trades
            loss_prob = 1 - win_prob
            
            # Calculate average win/loss
            avg_win = np.mean(wins)
            avg_loss = np.mean(losses)
            
            if avg_loss == 0:
                return None
            
            # Win/loss ratio (b in Kelly formula)
            b = avg_win / avg_loss
            
            # Kelly criterion
            kelly = (b * win_prob - loss_prob) / b
            
            # Apply Kelly fraction (Half-Kelly for safety)
            position_size = kelly * self.kelly_fraction
            
            # Minimum Kelly threshold
            if position_size <= 0:
                return None
            
            # Determine action based on trend
            trend = self._determine_trend(closes)
            
            if trend == 'uptrend':
                action = 'buy'
            elif trend == 'downtrend':
                action = 'sell'
            else:
                return None
            
            confidence = min(position_size * 2, 0.95)  # Scale confidence
            
            reasoning = f"Kelly Criterion: Position size {position_size:.2%}, Win rate {win_prob:.1%}, W/L ratio {b:.2f}"
            
            return {
                'strategy_name': 'kelly_criterion',
                'action': action,
                'confidence': confidence,
                'reasoning': reasoning,
                'indicators': {
                    'kelly_fraction': kelly,
                    'position_size': position_size,
                    'win_probability': win_prob,
                    'win_loss_ratio': b,
                    'avg_win': avg_win,
                    'avg_loss': avg_loss
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Kelly strategy: {e}")
            return None
    
    def _determine_trend(self, closes: list) -> str:
        """Determine trend direction"""
        if len(closes) < 20:
            return 'unknown'
        
        sma_20 = np.mean(closes[-20:])
        
        if closes[-1] > sma_20 * 1.01:
            return 'uptrend'
        elif closes[-1] < sma_20 * 0.99:
            return 'downtrend'
        else:
            return 'ranging'
