"""
Futures Agent - Interactive Brokers Integration
Monitors stock futures (ES, NQ, YM)
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, time

from agents.base_agent import BaseAgent, Signal
from core.config import EXCHANGE_CONFIG, TRADING_CONFIG
from exchanges.interactive_brokers import IBKRClient
from strategies.strategy_evaluator import StrategyEvaluator

logger = logging.getLogger(__name__)

class FuturesAgent(BaseAgent):
    """
    Stock futures specialist agent
    Monitors E-mini S&P 500 (ES), Nasdaq-100 (NQ), Dow (YM)
    """
    
    def __init__(self):
        super().__init__(agent_id="futures_agent", market="futures")
        
        # Initialize Interactive Brokers
        self.ibkr = IBKRClient(
            account_id=EXCHANGE_CONFIG.IBKR_ACCOUNT_ID,
            port=EXCHANGE_CONFIG.IBKR_PORT
        )
        
        # Strategy evaluator
        self.evaluator = StrategyEvaluator()
        
        # Futures symbols
        self.symbols = ['ES', 'NQ', 'YM']  # E-mini contracts
        
        # Market hours (CT - Central Time)
        self.pre_market_start = time(16, 0)  # 4:00 PM CT (previous day)
        self.regular_start = time(8, 30)     # 8:30 AM CT
        self.regular_end = time(15, 15)      # 3:15 PM CT
        self.after_hours_end = time(16, 0)   # 4:00 PM CT
        
    async def gather_data(self) -> Dict[str, Any]:
        """Gather futures market data"""
        data = {
            'timestamp': datetime.utcnow(),
            'market_phase': self._determine_market_phase(),
            'symbols': {}
        }
        
        # Check if market is open
        if not self._is_market_open():
            logger.debug("Futures market closed, using last known data")
            data['market_open'] = False
            return data
        
        data['market_open'] = True
        
        for symbol in self.symbols:
            try:
                # Get historical data
                historical = await self.ibkr.fetch_historical_data(symbol, '1 hour', '2 D')
                
                # Get real-time quote
                quote = await self.ibkr.fetch_quote(symbol)
                
                # Get order book
                orderbook = await self.ibkr.fetch_orderbook(symbol)
                
                # Calculate VWAP
                vwap = self._calculate_vwap(historical)
                
                # Check for volume profile
                volume_profile = self._analyze_volume_profile(historical)
                
                data['symbols'][symbol] = {
                    'historical': historical,
                    'quote': quote,
                    'orderbook': orderbook,
                    'vwap': vwap,
                    'volume_profile': volume_profile,
                    'volatility': self._calculate_volatility(historical),
                    'trend': self._determine_trend(historical),
                    'market_phase': data['market_phase']
                }
                
            except Exception as e:
                logger.error(f"Error gathering data for {symbol}: {e}")
                continue
        
        # Get positions
        data['positions'] = await self._get_positions()
        
        # Get market internals
        data['market_internals'] = await self._get_market_internals()
        
        return data
    
    async def analyze(self, data: Dict[str, Any]) -> Optional[Signal]:
        """Analyze futures data and generate signals"""
        if not data.get('market_open'):
            return None
        
        best_signal = None
        best_score = 0
        
        market_phase = data.get('market_phase', 'unknown')
        market_internals = data.get('market_internals', {})
        
        for symbol, symbol_data in data['symbols'].items():
            try:
                # Evaluate with market context
                result = self.evaluator.evaluate_all(
                    market='futures',
                    symbol=symbol,
                    data=symbol_data,
                    positions=data.get('positions', {}),
                    context={
                        'market_phase': market_phase,
                        'market_internals': market_internals,
                        'vwap_distance': self._calculate_vwap_distance(symbol_data)
                    }
                )
                
                if result['consensus'] >= TRADING_CONFIG.CONSENSUS_THRESHOLD:
                    # Adjust for futures-specific factors
                    adjusted_confidence = self._adjust_confidence_for_futures(
                        result['confidence'],
                        symbol_data,
                        market_phase,
                        market_internals
                    )
                    
                    if adjusted_confidence > best_score:
                        best_score = adjusted_confidence
                        best_signal = Signal(
                            agent=self.agent_id,
                            market='futures',
                            symbol=symbol,
                            action=result['action'],
                            confidence=adjusted_confidence,
                            strategy=result['primary_strategy'],
                            reasoning=result['reasoning'],
                            metadata={
                                'strategies': result['strategy_scores'],
                                'market_phase': market_phase,
                                'vwap': symbol_data.get('vwap'),
                                'market_internals': market_internals,
                                'volume_profile': symbol_data.get('volume_profile')
                            }
                        )
                        
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        return best_signal
    
    def _determine_market_phase(self) -> str:
        """Determine current futures market phase"""
        from datetime import datetime
        import pytz
        
        ct = pytz.timezone('US/Central')
        now = datetime.now(ct)
        current_time = now.time()
        
        # Pre-market: 4:00 PM - 8:30 AM CT (next day)
        # Regular: 8:30 AM - 3:15 PM CT
        # After hours: 3:15 PM - 4:00 PM CT
        
        if self.regular_start <= current_time <= self.regular_end:
            # First hour = opening range
            if current_time.hour == 8 and current_time.minute < 45:
                return 'opening_range'
            # Last hour = closing range
            elif current_time.hour == 14 or (current_time.hour == 15 and current_time.minute < 15):
                return 'closing_range'
            return 'regular_hours'
        elif self.pre_market_start <= current_time or current_time <= self.regular_start:
            return 'pre_market'
        elif self.regular_end < current_time <= self.after_hours_end:
            return 'after_hours'
        else:
            return 'closed'
    
    def _is_market_open(self) -> bool:
        """Check if futures market is currently open"""
        return self._determine_market_phase() != 'closed'
    
    def _calculate_vwap(self, historical: List) -> float:
        """Calculate Volume Weighted Average Price"""
        if not historical:
            return 0
        
        total_volume = sum(bar['volume'] for bar in historical)
        if total_volume == 0:
            return 0
        
        vwap = sum(bar['close'] * bar['volume'] for bar in historical) / total_volume
        return vwap
    
    def _calculate_vwap_distance(self, symbol_data: Dict) -> float:
        """Calculate distance from VWAP as percentage"""
        vwap = symbol_data.get('vwap', 0)
        quote = symbol_data.get('quote', {})
        
        if not vwap or not quote:
            return 0
        
        current_price = quote.get('last', quote.get('close', 0))
        if not current_price:
            return 0
        
        return abs(current_price - vwap) / vwap
    
    def _analyze_volume_profile(self, historical: List) -> Dict:
        """Analyze volume distribution"""
        if not historical:
            return {}
        
        volumes = [bar['volume'] for bar in historical]
        prices = [bar['close'] for bar in historical]
        
        import statistics
        
        return {
            'total_volume': sum(volumes),
            'avg_volume': statistics.mean(volumes) if volumes else 0,
            'volume_trend': 'increasing' if volumes[-1] > volumes[0] else 'decreasing',
            'price_range': max(prices) - min(prices) if prices else 0
        }
    
    def _adjust_confidence_for_futures(self, base_confidence: float,
                                       symbol_data: Dict,
                                       market_phase: str,
                                       market_internals: Dict) -> float:
        """Adjust confidence for futures-specific factors"""
        adjusted = base_confidence
        
        # Reduce confidence outside regular hours
        if market_phase in ['pre_market', 'after_hours']:
            adjusted *= 0.85
        elif market_phase == 'opening_range':
            # Higher volatility in opening range
            adjusted *= 0.9
        
        # VWAP mean reversion boost
        vwap_distance = self._calculate_vwap_distance(symbol_data)
        if vwap_distance > 0.005:  # >0.5% from VWAP
            adjusted *= 1.15  # Boost mean reversion
        
        # Market internals check
        adv_decl = market_internals.get('advancers_decliners_ratio', 1)
        if adv_decl > 2 or adv_decl < 0.5:
            # Strong trend confirmed by internals
            adjusted *= 1.1
        
        return min(adjusted, 1.0)
    
    def _calculate_volatility(self, historical: List) -> float:
        """Calculate volatility"""
        if len(historical) < 20:
            return 0
        
        closes = [bar['close'] for bar in historical[-20:]]
        returns = [(closes[i] - closes[i-1]) / closes[i-1] 
                   for i in range(1, len(closes))]
        
        import statistics
        return statistics.stdev(returns) * 100 if returns else 0
    
    def _determine_trend(self, historical: List) -> str:
        """Determine trend"""
        if len(historical) < 50:
            return 'unknown'
        
        closes = [bar['close'] for bar in historical]
        sma_20 = sum(closes[-20:]) / 20
        sma_50 = sum(closes[-50:]) / 50
        
        if closes[-1] > sma_20 > sma_50:
            return 'uptrend'
        elif closes[-1] < sma_20 < sma_50:
            return 'downtrend'
        else:
            return 'ranging'
    
    async def _get_positions(self) -> Dict:
        """Get open positions"""
        try:
            return await self.ibkr.fetch_positions()
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return {}
    
    async def _get_market_internals(self) -> Dict:
        """Get market internals (advance/decline, etc.)"""
        try:
            return await self.ibkr.fetch_market_internals()
        except Exception as e:
            logger.error(f"Error fetching market internals: {e}")
            return {}
    
    async def execute_command(self, command: str, params: Dict[str, Any]):
        """Execute command from OpenClaw"""
        if command == 'place_order':
            await self._place_order(params)
        elif command == 'close_position':
            await self._close_position(params)
        elif command == 'emergency_stop':
            await self._emergency_stop()
    
    async def _place_order(self, params: Dict):
        """Place futures order"""
        symbol = params['symbol']
        side = params['side']
        quantity = params['quantity']
        
        try:
            order = await self.ibkr.create_order(symbol, side, quantity)
            logger.info(f"Futures order placed: {side} {quantity} {symbol}")
        except Exception as e:
            logger.error(f"Failed to place futures order: {e}")
    
    async def _close_position(self, params: Dict):
        """Close futures position"""
        symbol = params['symbol']
        
        try:
            await self.ibkr.close_position(symbol)
            logger.info(f"Futures position closed: {symbol}")
        except Exception as e:
            logger.error(f"Failed to close futures position: {e}")
    
    async def _emergency_stop(self):
        """Emergency stop"""
        logger.critical("EMERGENCY STOP activated for futures agent")
        
        for symbol in self.symbols:
            try:
                await self._close_position({'symbol': symbol})
            except:
                pass
