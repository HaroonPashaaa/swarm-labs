"""
Forex Agent - OANDA Integration
Monitors forex major and minor pairs
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from agents.base_agent import BaseAgent, Signal
from core.config import EXCHANGE_CONFIG, TRADING_CONFIG
from exchanges.oanda_client import OandaClient
from strategies.strategy_evaluator import StrategyEvaluator

logger = logging.getLogger(__name__)

class ForexAgent(BaseAgent):
    """
    Forex market specialist agent
    Monitors major and minor currency pairs via OANDA
    """
    
    def __init__(self):
        super().__init__(agent_id="forex_agent", market="forex")
        
        # Initialize OANDA
        self.oanda = OandaClient(
            api_key=EXCHANGE_CONFIG.OANDA_API_KEY,
            account_id=EXCHANGE_CONFIG.OANDA_ACCOUNT_ID,
            practice=EXCHANGE_CONFIG.OANDA_PRACTICE
        )
        
        # Strategy evaluator
        self.evaluator = StrategyEvaluator()
        
        # Major and minor pairs
        self.symbols = [
            'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF',
            'AUD_USD', 'USD_CAD', 'NZD_USD',
            'EUR_GBP', 'EUR_JPY', 'GBP_JPY'
        ]
        
        # Session tracking
        self.current_session = self._determine_session()
        
    async def gather_data(self) -> Dict[str, Any]:
        """Gather forex market data"""
        data = {
            'timestamp': datetime.utcnow(),
            'session': self._determine_session(),
            'symbols': {}
        }
        
        # Update session if changed
        new_session = data['session']
        if new_session != self.current_session:
            logger.info(f"Forex session changed: {self.current_session} -> {new_session}")
            self.current_session = new_session
        
        for symbol in self.symbols:
            try:
                # Get candlestick data
                candles = await self.oanda.fetch_candles(symbol, 'H1', count=100)
                
                # Get current price
                price = await self.oanda.fetch_price(symbol)
                
                # Get orderbook (if available)
                orderbook = await self.oanda.fetch_orderbook(symbol)
                
                # Calculate session-specific metrics
                session_metrics = self._calculate_session_metrics(candles, new_session)
                
                data['symbols'][symbol] = {
                    'candles': candles,
                    'price': price,
                    'orderbook': orderbook,
                    'volatility': self._calculate_volatility(candles),
                    'trend': self._determine_trend(candles),
                    'session_metrics': session_metrics,
                    'spread': price.get('spread', 0) if price else 0
                }
                
            except Exception as e:
                logger.error(f"Error gathering data for {symbol}: {e}")
                continue
        
        # Get open positions
        data['positions'] = await self._get_positions()
        
        # Get economic calendar events
        data['economic_events'] = await self._get_economic_events()
        
        return data
    
    async def analyze(self, data: Dict[str, Any]) -> Optional[Signal]:
        """Analyze forex data and generate signals"""
        best_signal = None
        best_score = 0
        
        session = data.get('session', 'unknown')
        economic_events = data.get('economic_events', [])
        
        for symbol, symbol_data in data['symbols'].items():
            try:
                # Check for high-impact news
                news_impact = self._check_news_impact(symbol, economic_events)
                
                # Evaluate strategies with session context
                result = self.evaluator.evaluate_all(
                    market='forex',
                    symbol=symbol,
                    data=symbol_data,
                    positions=data.get('positions', {}),
                    context={
                        'session': session,
                        'news_impact': news_impact,
                        'spread': symbol_data.get('spread', 0)
                    }
                )
                
                if result['consensus'] >= TRADING_CONFIG.CONSENSUS_THRESHOLD:
                    # Adjust confidence for forex-specific factors
                    adjusted_confidence = self._adjust_confidence(
                        result['confidence'],
                        symbol_data,
                        session,
                        news_impact
                    )
                    
                    if adjusted_confidence > best_score:
                        best_score = adjusted_confidence
                        best_signal = Signal(
                            agent=self.agent_id,
                            market='forex',
                            symbol=symbol,
                            action=result['action'],
                            confidence=adjusted_confidence,
                            strategy=result['primary_strategy'],
                            reasoning=result['reasoning'],
                            metadata={
                                'strategies': result['strategy_scores'],
                                'session': session,
                                'news_impact': news_impact,
                                'volatility': symbol_data.get('volatility'),
                                'spread': symbol_data.get('spread')
                            }
                        )
                        
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        return best_signal
    
    def _determine_session(self) -> str:
        """Determine current forex trading session"""
        from datetime import datetime
        import pytz
        
        utc = datetime.utcnow()
        hour = utc.hour
        
        # Asian session: 00:00 - 09:00 UTC
        # London session: 08:00 - 17:00 UTC
        # NY session: 13:00 - 22:00 UTC
        
        if 0 <= hour < 9:
            if 8 <= hour < 9:
                return 'asia_london_overlap'
            return 'asia'
        elif 8 <= hour < 13:
            if 13 <= hour < 17:
                return 'london_ny_overlap'
            return 'london'
        elif 13 <= hour < 22:
            return 'new_york'
        else:
            return 'low_liquidity'
    
    def _calculate_session_metrics(self, candles: List, session: str) -> Dict:
        """Calculate session-specific metrics"""
        # Filter candles by session hours
        session_candles = [c for c in candles if self._is_session_hour(c['time'], session)]
        
        if not session_candles:
            return {}
        
        volumes = [c['volume'] for c in session_candles]
        ranges = [c['high'] - c['low'] for c in session_candles]
        
        return {
            'avg_volume': sum(volumes) / len(volumes),
            'avg_range': sum(ranges) / len(ranges),
            'session_candles': len(session_candles)
        }
    
    def _is_session_hour(self, timestamp: datetime, session: str) -> bool:
        """Check if timestamp falls in session"""
        hour = timestamp.hour
        
        session_hours = {
            'asia': range(0, 9),
            'london': range(8, 17),
            'new_york': range(13, 22)
        }
        
        return hour in session_hours.get(session, range(0, 24))
    
    def _check_news_impact(self, symbol: str, events: List) -> str:
        """Check for high-impact economic events"""
        # Parse symbol to get currencies
        currencies = symbol.split('_')
        
        for event in events:
            if event.get('impact') == 'high':
                event_currency = event.get('currency')
                if event_currency in currencies:
                    return 'high'
                
        return 'low'
    
    def _adjust_confidence(self, base_confidence: float, 
                          symbol_data: Dict, session: str, 
                          news_impact: str) -> float:
        """Adjust confidence based on forex-specific factors"""
        adjusted = base_confidence
        
        # Reduce confidence during low liquidity
        if session in ['low_liquidity', 'asia']:
            adjusted *= 0.9
        
        # Boost confidence during overlap sessions
        if 'overlap' in session:
            adjusted *= 1.1
        
        # Reduce confidence before high-impact news
        if news_impact == 'high':
            adjusted *= 0.7
        
        # Adjust for spread
        spread = symbol_data.get('spread', 0)
        if spread > 0.0005:  # High spread
            adjusted *= 0.9
        
        return min(adjusted, 1.0)
    
    def _calculate_volatility(self, candles: List) -> float:
        """Calculate volatility from candles"""
        if len(candles) < 20:
            return 0
        
        closes = [c['close'] for c in candles[-20:]]
        returns = [(closes[i] - closes[i-1]) / closes[i-1] 
                   for i in range(1, len(closes))]
        
        import statistics
        return statistics.stdev(returns) * 100  # As percentage
    
    def _determine_trend(self, candles: List) -> str:
        """Determine trend direction"""
        if len(candles) < 50:
            return 'unknown'
        
        closes = [c['close'] for c in candles]
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
            return await self.oanda.fetch_positions()
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return {}
    
    async def _get_economic_events(self) -> List:
        """Get economic calendar events"""
        try:
            return await self.oanda.fetch_economic_calendar()
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
            return []
    
    async def execute_command(self, command: str, params: Dict[str, Any]):
        """Execute command from OpenClaw"""
        if command == 'place_order':
            await self._place_order(params)
        elif command == 'close_position':
            await self._close_position(params)
        elif command == 'emergency_stop':
            await self._emergency_stop()
    
    async def _place_order(self, params: Dict):
        """Place forex order"""
        symbol = params['symbol']
        side = params['side']
        units = params['units']
        
        try:
            order = await self.oanda.create_order(symbol, side, units)
            logger.info(f"Forex order placed: {side} {units} {symbol}")
        except Exception as e:
            logger.error(f"Failed to place forex order: {e}")
    
    async def _close_position(self, params: Dict):
        """Close forex position"""
        symbol = params['symbol']
        
        try:
            await self.oanda.close_position(symbol)
            logger.info(f"Forex position closed: {symbol}")
        except Exception as e:
            logger.error(f"Failed to close forex position: {e}")
    
    async def _emergency_stop(self):
        """Emergency stop - close all forex positions"""
        logger.critical("EMERGENCY STOP activated for forex agent")
        
        for symbol in self.symbols:
            try:
                await self._close_position({'symbol': symbol})
            except:
                pass
