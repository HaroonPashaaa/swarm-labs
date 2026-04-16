"""
Crypto Agent - Binance & Bybit Integration
Monitors crypto futures markets
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import ccxt

from agents.base_agent import BaseAgent, Signal
from core.config import EXCHANGE_CONFIG, TRADING_CONFIG
from exchanges.binance_client import BinanceClient
from exchanges.bybit_client import BybitClient
from strategies.strategy_evaluator import StrategyEvaluator

logger = logging.getLogger(__name__)

class CryptoAgent(BaseAgent):
    """
    Crypto market specialist agent
    Monitors BTC, ETH perpetuals on Binance and Bybit
    """
    
    def __init__(self):
        super().__init__(agent_id="crypto_agent", market="crypto")
        
        # Initialize exchanges
        self.binance = BinanceClient(
            api_key=EXCHANGE_CONFIG.BINANCE_API_KEY,
            secret=EXCHANGE_CONFIG.BINANCE_SECRET,
            testnet=EXCHANGE_CONFIG.BINANCE_TESTNET
        )
        
        self.bybit = BybitClient(
            api_key=EXCHANGE_CONFIG.BYBIT_API_KEY,
            secret=EXCHANGE_CONFIG.BYBIT_SECRET,
            testnet=EXCHANGE_CONFIG.BYBIT_TESTNET
        )
        
        # Strategy evaluator
        self.evaluator = StrategyEvaluator()
        
        # Tracked symbols
        self.symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']
        
        # Market state
        self.positions = {}
        self.market_data = {}
        
    async def gather_data(self) -> Dict[str, Any]:
        """Gather market data from crypto exchanges"""
        data = {
            'timestamp': datetime.utcnow(),
            'symbols': {}
        }
        
        for symbol in self.symbols:
            try:
                # Get OHLCV data from Binance
                ohlcv_binance = await self.binance.fetch_ohlcv(symbol, '1h', limit=100)
                
                # Get OHLCV data from Bybit
                ohlcv_bybit = await self.bybit.fetch_ohlcv(symbol, '1h', limit=100)
                
                # Get orderbook
                orderbook_binance = await self.binance.fetch_order_book(symbol)
                orderbook_bybit = await self.bybit.fetch_order_book(symbol)
                
                # Check for arbitrage opportunity
                arb_opportunity = self._detect_arbitrage(orderbook_binance, orderbook_bybit)
                
                data['symbols'][symbol] = {
                    'binance': {
                        'ohlcv': ohlcv_binance,
                        'orderbook': orderbook_binance,
                        'funding_rate': await self.binance.fetch_funding_rate(symbol)
                    },
                    'bybit': {
                        'ohlcv': ohlcv_bybit,
                        'orderbook': orderbook_bybit,
                        'funding_rate': await self.bybit.fetch_funding_rate(symbol)
                    },
                    'arbitrage': arb_opportunity,
                    'volatility': self._calculate_volatility(ohlcv_binance),
                    'trend': self._determine_trend(ohlcv_binance)
                }
                
            except Exception as e:
                logger.error(f"Error gathering data for {symbol}: {e}")
                continue
        
        # Get positions
        data['positions'] = await self._get_positions()
        
        return data
    
    async def analyze(self, data: Dict[str, Any]) -> Optional[Signal]:
        """Analyze crypto market data and generate signals"""
        best_signal = None
        best_score = 0
        
        for symbol, symbol_data in data['symbols'].items():
            try:
                # Run all strategies through evaluator
                result = self.evaluator.evaluate_all(
                    market='crypto',
                    symbol=symbol,
                    data=symbol_data,
                    positions=data.get('positions', {})
                )
                
                if result['consensus'] >= TRADING_CONFIG.CONSENSUS_THRESHOLD:
                    if result['confidence'] > best_score:
                        best_score = result['confidence']
                        best_signal = Signal(
                            agent=self.agent_id,
                            market='crypto',
                            symbol=symbol,
                            action=result['action'],
                            confidence=result['confidence'],
                            strategy=result['primary_strategy'],
                            reasoning=result['reasoning'],
                            metadata={
                                'strategies': result['strategy_scores'],
                                'arbitrage': symbol_data.get('arbitrage'),
                                'volatility': symbol_data.get('volatility'),
                                'funding_rate': symbol_data['binance'].get('funding_rate')
                            }
                        )
                        
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        return best_signal
    
    def _detect_arbitrage(self, ob1: Dict, ob2: Dict) -> Optional[Dict]:
        """Detect arbitrage between exchanges"""
        bid1 = ob1['bids'][0][0] if ob1['bids'] else 0
        ask1 = ob1['asks'][0][0] if ob1['asks'] else float('inf')
        
        bid2 = ob2['bids'][0][0] if ob2['bids'] else 0
        ask2 = ob2['asks'][0][0] if ob2['asks'] else float('inf')
        
        # Buy on exchange 1, sell on exchange 2
        spread1 = bid2 - ask1
        # Buy on exchange 2, sell on exchange 1
        spread2 = bid1 - ask2
        
        best_spread = max(spread1, spread2)
        
        if best_spread > 0:
            profit_pct = best_spread / min(ask1, ask2)
            if profit_pct > 0.001:  # 0.1% minimum
                return {
                    'spread': best_spread,
                    'profit_pct': profit_pct,
                    'direction': 'binance_to_bybit' if spread1 > spread2 else 'bybit_to_binance'
                }
        
        return None
    
    def _calculate_volatility(self, ohlcv: List) -> float:
        """Calculate recent volatility from OHLCV"""
        if len(ohlcv) < 20:
            return 0
        
        closes = [c[4] for c in ohlcv[-20:]]
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        
        # Standard deviation of returns
        import statistics
        return statistics.stdev(returns) if returns else 0
    
    def _determine_trend(self, ohlcv: List) -> str:
        """Determine current trend"""
        if len(ohlcv) < 50:
            return 'unknown'
        
        closes = [c[4] for c in ohlcv]
        sma_20 = sum(closes[-20:]) / 20
        sma_50 = sum(closes[-50:]) / 50
        
        if closes[-1] > sma_20 > sma_50:
            return 'uptrend'
        elif closes[-1] < sma_20 < sma_50:
            return 'downtrend'
        else:
            return 'ranging'
    
    async def _get_positions(self) -> Dict:
        """Get current positions"""
        positions = {}
        try:
            binance_positions = await self.binance.fetch_positions()
            bybit_positions = await self.bybit.fetch_positions()
            
            positions['binance'] = binance_positions
            positions['bybit'] = bybit_positions
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
        
        return positions
    
    async def execute_command(self, command: str, params: Dict[str, Any]):
        """Execute command from OpenClaw"""
        if command == 'place_order':
            await self._place_order(params)
        elif command == 'close_position':
            await self._close_position(params)
        elif command == 'update_symbols':
            self.symbols = params.get('symbols', self.symbols)
        elif command == 'emergency_stop':
            await self._emergency_stop()
    
    async def _place_order(self, params: Dict):
        """Place order on exchange"""
        symbol = params['symbol']
        side = params['side']
        amount = params['amount']
        exchange = params.get('exchange', 'binance')
        
        try:
            if exchange == 'binance':
                order = await self.binance.create_order(symbol, 'market', side, amount)
            else:
                order = await self.bybit.create_order(symbol, 'market', side, amount)
            
            logger.info(f"Order placed: {side} {amount} {symbol} on {exchange}")
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
    
    async def _close_position(self, params: Dict):
        """Close position"""
        symbol = params['symbol']
        exchange = params.get('exchange', 'binance')
        
        try:
            if exchange == 'binance':
                await self.binance.close_position(symbol)
            else:
                await self.bybit.close_position(symbol)
            
            logger.info(f"Position closed: {symbol} on {exchange}")
            
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
    
    async def _emergency_stop(self):
        """Emergency stop - close all positions"""
        logger.critical("EMERGENCY STOP activated for crypto agent")
        
        for symbol in self.symbols:
            try:
                await self._close_position({'symbol': symbol, 'exchange': 'binance'})
                await self._close_position({'symbol': symbol, 'exchange': 'bybit'})
            except:
                pass
