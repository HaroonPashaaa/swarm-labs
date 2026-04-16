"""
Bybit Exchange Client
Futures trading via Bybit API
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import ccxt.async_support as ccxt

logger = logging.getLogger(__name__)

class BybitClient:
    """
    Bybit Futures API Client
    
    Mirrors BinanceClient interface for consistency
    """
    
    def __init__(self, api_key: str, secret: str, testnet: bool = True):
        self.api_key = api_key
        self.secret = secret
        self.testnet = testnet
        
        # Initialize CCXT exchange
        config = {
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        }
        
        if testnet:
            config['sandbox'] = True
        
        self.exchange = ccxt.bybit(config)
        self.connected = False
        
    async def connect(self):
        """Connect to Bybit"""
        try:
            await self.exchange.load_markets()
            self.connected = True
            logger.info("Connected to Bybit" + (" TESTNET" if self.testnet else ""))
        except Exception as e:
            logger.error(f"Failed to connect to Bybit: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Bybit"""
        await self.exchange.close()
        self.connected = False
        logger.info("Disconnected from Bybit")
    
    async def fetch_balance(self) -> Dict[str, Any]:
        """Fetch account balance"""
        try:
            balance = await self.exchange.fetch_balance()
            return {
                'total': balance.get('total', {}),
                'free': balance.get('free', {}),
                'used': balance.get('used', {}),
                'USDT': {
                    'total': balance.get('total', {}).get('USDT', 0),
                    'free': balance.get('free', {}).get('USDT', 0),
                    'used': balance.get('used', {}).get('USDT', 0)
                }
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}
    
    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1h',
                          limit: int = 100) -> List[List]:
        """Fetch OHLCV data"""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return []
    
    async def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch ticker"""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker.get('last'),
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'volume': ticker.get('quoteVolume'),
                'change': ticker.get('change'),
                'percentage': ticker.get('percentage')
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return {}
    
    async def fetch_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Fetch order book"""
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit)
            return {
                'symbol': symbol,
                'bids': orderbook.get('bids', []),
                'asks': orderbook.get('asks', []),
                'timestamp': orderbook.get('timestamp')
            }
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            return {'bids': [], 'asks': []}
    
    async def fetch_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """Fetch funding rate"""
        try:
            funding = await self.exchange.fetch_funding_rate(symbol)
            return {
                'symbol': symbol,
                'fundingRate': funding.get('fundingRate'),
                'fundingTimestamp': funding.get('fundingTimestamp'),
                'nextFundingTimestamp': funding.get('nextFundingTimestamp')
            }
        except Exception as e:
            logger.error(f"Error fetching funding rate for {symbol}: {e}")
            return {}
    
    async def fetch_positions(self) -> List[Dict[str, Any]]:
        """Fetch positions"""
        try:
            positions = await self.exchange.fetch_positions()
            active_positions = [
                {
                    'symbol': pos['symbol'],
                    'side': 'long' if pos['contracts'] > 0 else 'short',
                    'contracts': abs(pos['contracts']),
                    'entryPrice': pos['entryPrice'],
                    'markPrice': pos['markPrice'],
                    'unrealizedPnl': pos['unrealizedPnl'],
                    'liquidationPrice': pos.get('liquidationPrice'),
                    'leverage': pos.get('leverage', 1)
                }
                for pos in positions
                if pos.get('contracts', 0) != 0
            ]
            return active_positions
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    async def create_order(self, symbol: str, side: str, amount: float,
                          order_type: str = 'market', price: float = None,
                          params: Dict = None) -> Dict[str, Any]:
        """Create order"""
        try:
            order_params = params or {}
            
            order = await self.exchange.create_order(
                symbol, order_type, side, amount, price, order_params
            )
            
            logger.info(f"Bybit order created: {side} {amount} {symbol} @ {order_type}")
            
            return {
                'id': order.get('id'),
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'type': order_type,
                'status': order.get('status'),
                'timestamp': order.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise
    
    async def create_market_order(self, symbol: str, side: str,
                                  amount: float) -> Dict[str, Any]:
        """Create market order"""
        return await self.create_order(symbol, side, amount, 'market')
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order"""
        try:
            await self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    async def close_position(self, symbol: str) -> Dict[str, Any]:
        """Close position"""
        try:
            positions = await self.fetch_positions()
            position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if not position:
                logger.info(f"No position to close for {symbol}")
                return {}
            
            side = 'sell' if position['side'] == 'long' else 'buy'
            amount = position['contracts']
            
            order = await self.create_order(
                symbol, side, amount, 'market',
                params={'reduce_only': True}
            )
            
            logger.info(f"Position closed for {symbol}")
            return order
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            raise
    
    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage"""
        try:
            await self.exchange.set_leverage(leverage, symbol)
            logger.info(f"Leverage set to {leverage}x for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error setting leverage: {e}")
            return False
