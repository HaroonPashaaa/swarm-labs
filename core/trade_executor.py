"""
Trade Executor
Execute trades on exchanges
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class TradeResult:
    """Trade execution result"""
    success: bool
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float
    timestamp: datetime
    error: str = None

class TradeExecutor:
    """Execute trades across multiple exchanges"""
    
    def __init__(self, exchanges: Dict):
        self.exchanges = exchanges
        
    async def execute_trade(self, symbol: str, side: str, quantity: float,
                           order_type: str = 'market', price: float = None,
                           exchange: str = None) -> TradeResult:
        """Execute a trade"""
        try:
            # Select exchange
            if not exchange:
                exchange = self._select_exchange(symbol)
            
            if exchange not in self.exchanges:
                return TradeResult(
                    success=False,
                    order_id='',
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=0,
                    fee=0,
                    timestamp=datetime.utcnow(),
                    error=f"Exchange {exchange} not available"
                )
            
            # Execute on exchange
            ex = self.exchanges[exchange]
            
            if order_type == 'market':
                result = await ex.create_market_order(symbol, side, quantity)
            else:
                result = await ex.create_limit_order(symbol, side, quantity, price)
            
            logger.info(f"Trade executed: {side} {quantity} {symbol} on {exchange}")
            
            return TradeResult(
                success=True,
                order_id=result.get('id', ''),
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=result.get('price', 0),
                fee=result.get('fee', 0),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            
            return TradeResult(
                success=False,
                order_id='',
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=0,
                fee=0,
                timestamp=datetime.utcnow(),
                error=str(e)
            )
    
    def _select_exchange(self, symbol: str) -> str:
        """Select best exchange for symbol"""
        # Simple selection logic
        if 'USDT' in symbol:
            return 'binance'
        elif 'USD' in symbol:
            return 'oanda'
        else:
            return list(self.exchanges.keys())[0]
