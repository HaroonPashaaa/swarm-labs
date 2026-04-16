"""
Signal Processor
Process and filter trading signals
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SignalProcessor:
    """Process and filter signals"""
    
    def __init__(self):
        self.recent_signals = []
        self.min_confidence = 0.6
        self.cooldown_period = 300  # 5 minutes
        
    def process_signal(self, signal: Dict) -> Optional[Dict]:
        """Process incoming signal"""
        # Check confidence
        if signal.get('confidence', 0) < self.min_confidence:
            logger.debug(f"Signal rejected: low confidence {signal.get('confidence')}")
            return None
        
        # Check cooldown
        symbol = signal.get('symbol')
        if self._is_in_cooldown(symbol):
            logger.debug(f"Signal rejected: {symbol} in cooldown")
            return None
        
        # Add timestamp
        signal['processed_at'] = datetime.utcnow().isoformat()
        
        # Store signal
        self.recent_signals.append(signal)
        
        # Clean old signals
        self._clean_old_signals()
        
        return signal
    
    def _is_in_cooldown(self, symbol: str) -> bool:
        """Check if symbol is in cooldown"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.cooldown_period)
        
        for signal in self.recent_signals:
            if signal.get('symbol') == symbol:
                signal_time = datetime.fromisoformat(signal.get('timestamp', '2000-01-01'))
                if signal_time > cutoff:
                    return True
        
        return False
    
    def _clean_old_signals(self):
        """Remove old signals"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        self.recent_signals = [
            s for s in self.recent_signals
            if datetime.fromisoformat(s.get('timestamp', '2000-01-01')) > cutoff
        ]
    
    def get_signal_stats(self) -> Dict:
        """Get signal statistics"""
        total = len(self.recent_signals)
        
        actions = {}
        for signal in self.recent_signals:
            action = signal.get('action', 'unknown')
            actions[action] = actions.get(action, 0) + 1
        
        return {
            'total_signals': total,
            'action_breakdown': actions,
            'last_24h': total
        }
