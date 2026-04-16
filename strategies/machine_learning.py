"""
Machine Learning Strategy
Predictive model-based trading signals
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class MachineLearningStrategy:
    """
    Machine Learning Strategy
    
    Uses technical indicators as features to predict price direction.
    Simplified version - can be extended with actual ML models.
    """
    
    def __init__(self):
        self.lookback = 30
        self.features = ['rsi', 'macd', 'bb_position', 'volume_change', 'price_momentum']
        
    def evaluate(self, market: str, symbol: str, data: Dict,
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """Evaluate using ML features"""
        try:
            candles = data.get('ohlcv') or data.get('candles') or []
            
            if len(candles) < self.lookback + 10:
                return None
            
            closes = [c[4] if isinstance(c, list) else c.get('close', 0) for c in candles]
            volumes = [c[5] if isinstance(c, list) else c.get('volume', 0) for c in candles]
            
            # Calculate features
            features = self._calculate_features(closes, volumes)
            
            if not features:
                return None
            
            # Simple scoring model (replace with actual ML model)
            score = self._calculate_score(features)
            
            if abs(score) < 0.3:
                return None
            
            action = 'buy' if score > 0 else 'sell'
            confidence = min(abs(score), 0.95)
            
            reasoning = f"ML Model Score: {score:.2f}. Features: RSI={features.get('rsi', 0):.1f}, "
            reasoning += f"Momentum={features.get('price_momentum', 0):.2f}"
            
            return {
                'strategy_name': 'machine_learning',
                'action': action,
                'confidence': confidence,
                'reasoning': reasoning,
                'indicators': features
            }
            
        except Exception as e:
            logger.error(f"Error in ML strategy: {e}")
            return None
    
    def _calculate_features(self, closes: list, volumes: list) -> Dict[str, float]:
        """Calculate technical features"""
        if len(closes) < 20:
            return {}
        
        # RSI
        rsi = self._calculate_rsi(closes)
        
        # MACD
        macd = self._calculate_macd(closes)
        
        # Bollinger Band position
        bb_pos = self._calculate_bb_position(closes)
        
        # Volume change
        vol_change = (volumes[-1] - np.mean(volumes[-10:-1])) / np.mean(volumes[-10:-1]) if len(volumes) > 10 else 0
        
        # Price momentum
        momentum = (closes[-1] - closes[-10]) / closes[-10] if len(closes) > 10 else 0
        
        return {
            'rsi': rsi,
            'macd': macd,
            'bb_position': bb_pos,
            'volume_change': vol_change,
            'price_momentum': momentum
        }
    
    def _calculate_rsi(self, closes: list, period: int = 14) -> float:
        """Calculate RSI"""
        if len(closes) < period + 1:
            return 50
        
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, closes: list) -> float:
        """Calculate MACD histogram"""
        if len(closes) < 26:
            return 0
        
        ema_12 = np.mean(closes[-12:])
        ema_26 = np.mean(closes[-26:])
        
        macd_line = ema_12 - ema_26
        signal_line = macd_line  # Simplified
        
        return macd_line - signal_line
    
    def _calculate_bb_position(self, closes: list, period: int = 20) -> float:
        """Calculate position within Bollinger Bands (-1 to 1)"""
        if len(closes) < period:
            return 0
        
        sma = np.mean(closes[-period:])
        std = np.std(closes[-period:])
        
        if std == 0:
            return 0
        
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        
        position = (closes[-1] - lower) / (upper - lower)
        return (position - 0.5) * 2  # Normalize to -1 to 1
    
    def _calculate_score(self, features: Dict) -> float:
        """Calculate prediction score from features"""
        # Simple weighted model (replace with actual trained model)
        weights = {
            'rsi': -0.01,  # Inverse - high RSI is overbought
            'macd': 0.5,
            'bb_position': -0.3,  # Inverse - high position is overbought
            'volume_change': 0.2,
            'price_momentum': 0.3
        }
        
        score = 0
        for feature, value in features.items():
            if feature in weights:
                score += value * weights[feature]
        
        # Normalize to -1 to 1
        return np.tanh(score)
