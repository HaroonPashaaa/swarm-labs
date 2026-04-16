"""
Session-Based Strategy
Tailor strategy based on active trading session
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SessionBasedStrategy:
    """
    Session-Based Trading Strategy
    
    Adjusts trading approach based on:
    - Asian session (consolidation, range-bound)
    - London open (breakout potential)
    - London/NY overlap (highest liquidity)
    - NY afternoon (trend continuation or reversal)
    
    Each session has optimal strategies and risk parameters.
    """
    
    def __init__(self):
        self.session_strategies = {
            'asia': {
                'bias': 'range',
                'best_strategies': ['grid_trading', 'mean_reversion', 'scalping'],
                'volatility_expectation': 'low',
                'risk_multiplier': 0.7
            },
            'london': {
                'bias': 'breakout',
                'best_strategies': ['momentum', 'volatility_breakout', 'scalping'],
                'volatility_expectation': 'medium',
                'risk_multiplier': 1.0
            },
            'new_york': {
                'bias': 'momentum',
                'best_strategies': ['momentum', 'trend_following', 'scalping'],
                'volatility_expectation': 'high',
                'risk_multiplier': 1.1
            },
            'overlap': {
                'bias': 'trend',
                'best_strategies': ['momentum', 'arbitrage', 'scalping'],
                'volatility_expectation': 'high',
                'risk_multiplier': 1.2
            },
            'low_liquidity': {
                'bias': 'avoid',
                'best_strategies': [],
                'volatility_expectation': 'low',
                'risk_multiplier': 0.0
            }
        }
        
    def evaluate(self, market: str, symbol: str, data: Dict,
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """Evaluate based on session characteristics"""
        try:
            # Get session info
            if not context:
                return None
            
            session = context.get('session', 'unknown')
            
            # Skip if session not recognized
            if session not in self.session_strategies:
                return None
            
            session_config = self.session_strategies[session]
            
            # Check if we should avoid trading
            if session_config['bias'] == 'avoid':
                return None
            
            # Get current strategy being evaluated from context
            current_strategy = context.get('current_strategy', '')
            
            # Check if current strategy is optimal for this session
            if current_strategy and current_strategy not in session_config['best_strategies']:
                # Reduce confidence for non-optimal strategies
                confidence_penalty = 0.3
            else:
                confidence_penalty = 0.0
            
            # Get market data
            trend = data.get('trend', 'unknown')
            volatility = data.get('volatility', 0)
            
            # Session-specific analysis
            if session == 'asia':
                return self._evaluate_asia(data, trend, volatility, session_config, confidence_penalty)
            elif session == 'london':
                return self._evaluate_london(data, trend, volatility, session_config, confidence_penalty)
            elif session == 'new_york':
                return self._evaluate_ny(data, trend, volatility, session_config, confidence_penalty)
            elif session == 'overlap':
                return self._evaluate_overlap(data, trend, volatility, session_config, confidence_penalty)
            
            return None
            
        except Exception as e:
            logger.error(f"Error in session-based strategy: {e}")
            return None
    
    def _evaluate_asia(self, data: Dict, trend: str, volatility: float,
                       config: Dict, penalty: float) -> Optional[Dict]:
        """Evaluate Asian session - range trading focus"""
        # Best for mean reversion and grid trading
        # Look for touches of support/resistance
        
        if volatility > 0.02:  # Too volatile for Asia
            return None
        
        # Calculate range
        candles = data.get('ohlcv', [])
        if len(candles) < 20:
            return None
        
        closes = [c[4] if isinstance(c, list) else c.get('close', 0) for c in candles[-20:]]
        range_high = max(closes)
        range_low = min(closes)
        current = closes[-1]
        
        range_pct = (range_high - range_low) / range_low
        position_in_range = (current - range_low) / (range_high - range_low)
        
        if range_pct < 0.005:  # Range too tight
            return None
        
        # Trade range extremes
        if position_in_range > 0.9:  # Near resistance
            action = 'sell'
            confidence = 0.7 - penalty
            reasoning = f"Asian session range: Price {position_in_range:.1%} of range. Sell near resistance."
        elif position_in_range < 0.1:  # Near support
            action = 'buy'
            confidence = 0.7 - penalty
            reasoning = f"Asian session range: Price {position_in_range:.1%} of range. Buy near support."
        else:
            return None
        
        return {
            'strategy_name': 'session_based',
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'indicators': {
                'session': 'asia',
                'range_high': range_high,
                'range_low': range_low,
                'position_in_range': position_in_range,
                'risk_multiplier': config['risk_multiplier']
            }
        }
    
    def _evaluate_london(self, data: Dict, trend: str, volatility: float,
                         config: Dict, penalty: float) -> Optional[Dict]:
        """Evaluate London session - breakout focus"""
        # Look for break of Asian range
        # Momentum after 8:30 AM GMT
        
        if trend == 'uptrend' and volatility > 0.01:
            action = 'buy'
            confidence = 0.75 - penalty
            reasoning = "London open momentum: Uptrend with increasing volatility."
        elif trend == 'downtrend' and volatility > 0.01:
            action = 'sell'
            confidence = 0.75 - penalty
            reasoning = "London open momentum: Downtrend with increasing volatility."
        else:
            return None
        
        return {
            'strategy_name': 'session_based',
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'indicators': {
                'session': 'london',
                'trend': trend,
                'volatility': volatility,
                'risk_multiplier': config['risk_multiplier']
            }
        }
    
    def _evaluate_ny(self, data: Dict, trend: str, volatility: float,
                     config: Dict, penalty: float) -> Optional[Dict]:
        """Evaluate NY session - trend continuation or reversal"""
        # Check for trend continuation or afternoon reversal
        
        hour = datetime.utcnow().hour
        
        if 13 <= hour < 16:  # NY morning - continuation
            if trend == 'uptrend':
                action = 'buy'
                confidence = 0.7 - penalty
                reasoning = "NY morning: Trend continuation expected."
            elif trend == 'downtrend':
                action = 'sell'
                confidence = 0.7 - penalty
                reasoning = "NY morning: Trend continuation expected."
            else:
                return None
                
        elif hour >= 16:  # NY afternoon - watch for reversals
            # More cautious in afternoon
            if trend == 'uptrend' and volatility > 0.015:
                action = 'sell'  # Potential reversal
                confidence = 0.6 - penalty
                reasoning = "NY afternoon: Potential trend exhaustion."
            elif trend == 'downtrend' and volatility > 0.015:
                action = 'buy'  # Potential reversal
                confidence = 0.6 - penalty
                reasoning = "NY afternoon: Potential trend exhaustion."
            else:
                return None
        else:
            return None
        
        return {
            'strategy_name': 'session_based',
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'indicators': {
                'session': 'new_york',
                'hour': hour,
                'trend': trend,
                'volatility': volatility,
                'risk_multiplier': config['risk_multiplier']
            }
        }
    
    def _evaluate_overlap(self, data: Dict, trend: str, volatility: float,
                          config: Dict, penalty: float) -> Optional[Dict]:
        """Evaluate London/NY overlap - highest opportunity"""
        # Best liquidity, clear trends
        
        if trend == 'unknown' or volatility < 0.01:
            return None
        
        if trend == 'uptrend':
            action = 'buy'
            confidence = 0.85 - penalty
            reasoning = "London/NY overlap: Strong uptrend with maximum liquidity."
        else:
            action = 'sell'
            confidence = 0.85 - penalty
            reasoning = "London/NY overlap: Strong downtrend with maximum liquidity."
        
        return {
            'strategy_name': 'session_based',
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'indicators': {
                'session': 'overlap',
                'trend': trend,
                'volatility': volatility,
                'risk_multiplier': config['risk_multiplier']
            }
        }
