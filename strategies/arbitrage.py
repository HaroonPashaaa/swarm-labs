"""
Arbitrage Strategy
Exploit price discrepancies across markets
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ArbitrageStrategy:
    """
    Arbitrage Strategy
    
    Identifies and exploits price discrepancies across:
    - Different exchanges
    - Correlated instruments
    - Spot vs futures basis
    
    Requires low-latency execution and careful fee accounting.
    """
    
    def __init__(self):
        self.min_spread_pct = 0.001  # 0.1% minimum spread
        self.max_hold_time = 300     # 5 minutes max to close
        self.fee_estimate = 0.001    # 0.1% estimated fees
        
    def evaluate(self, market: str, symbol: str, data: Dict,
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """Evaluate arbitrage opportunity"""
        try:
            # Check for arbitrage data in market data
            arbitrage = data.get('arbitrage')
            
            if not arbitrage:
                # Try to find in nested data structure
                if 'binance' in data and 'bybit' in data:
                    # Calculate cross-exchange arbitrage
                    arbitrage = self._calculate_cross_exchange_arbitrage(data)
            
            if not arbitrage:
                return None
            
            spread = arbitrage.get('spread', 0)
            profit_pct = arbitrage.get('profit_pct', 0)
            direction = arbitrage.get('direction', '')
            
            # Account for fees
            net_profit = profit_pct - (self.fee_estimate * 2)  # Entry + exit fees
            
            if net_profit < self.min_spread_pct:
                return None
            
            # Determine action based on direction
            if direction == 'binance_to_bybit':
                # Buy on Binance, sell on Bybit
                action = 'buy'
                entry_exchange = 'binance'
                exit_exchange = 'bybit'
            elif direction == 'bybit_to_binance':
                # Buy on Bybit, sell on Binance
                action = 'buy'
                entry_exchange = 'bybit'
                exit_exchange = 'binance'
            else:
                return None
            
            # Calculate confidence based on profit margin
            confidence = min(net_profit / 0.005, 1.0)  # Scale to 0.5% = max confidence
            
            reasoning = f"Arbitrage: {profit_pct:.3%} spread between {entry_exchange} and {exit_exchange}. "
            reasoning += f"Net profit after fees: {net_profit:.3%}. Hold time target: <{self.max_hold_time}s."
            
            return {
                'strategy_name': 'arbitrage',
                'action': action,
                'confidence': confidence,
                'reasoning': reasoning,
                'indicators': {
                    'spread': spread,
                    'profit_pct': profit_pct,
                    'net_profit': net_profit,
                    'direction': direction,
                    'entry_exchange': entry_exchange,
                    'exit_exchange': exit_exchange,
                    'max_hold_time': self.max_hold_time
                }
            }
            
        except Exception as e:
            logger.error(f"Error in arbitrage strategy: {e}")
            return None
    
    def _calculate_cross_exchange_arbitrage(self, data: Dict) -> Optional[Dict]:
        """Calculate arbitrage between exchanges"""
        try:
            binance_ob = data['binance'].get('orderbook', {})
            bybit_ob = data['bybit'].get('orderbook', {})
            
            if not binance_ob or not bybit_ob:
                return None
            
            # Get best bid/ask from each
            binance_bid = binance_ob.get('bids', [[0, 0]])[0][0]
            binance_ask = binance_ob.get('asks', [[float('inf'), 0]])[0][0]
            
            bybit_bid = bybit_ob.get('bids', [[0, 0]])[0][0]
            bybit_ask = bybit_ob.get('asks', [[float('inf'), 0]])[0][0]
            
            # Calculate spreads
            # Buy Binance, sell Bybit
            spread_1 = bybit_bid - binance_ask
            profit_1 = spread_1 / binance_ask if binance_ask > 0 else 0
            
            # Buy Bybit, sell Binance
            spread_2 = binance_bid - bybit_ask
            profit_2 = spread_2 / bybit_ask if bybit_ask > 0 else 0
            
            if profit_1 > profit_2 and profit_1 > 0:
                return {
                    'spread': spread_1,
                    'profit_pct': profit_1,
                    'direction': 'binance_to_bybit'
                }
            elif profit_2 > 0:
                return {
                    'spread': spread_2,
                    'profit_pct': profit_2,
                    'direction': 'bybit_to_binance'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating cross-exchange arbitrage: {e}")
            return None
