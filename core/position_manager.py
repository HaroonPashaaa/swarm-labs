"""
Position Manager
Track and manage trading positions
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Position:
    """Trading position"""
    symbol: str
    side: str  # long or short
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    open_time: datetime
    metadata: Dict

class PositionManager:
    """Manage all trading positions"""
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        
    def open_position(self, symbol: str, side: str, quantity: float,
                     entry_price: float, metadata: Dict = None) -> Position:
        """Open new position"""
        position = Position(
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            open_time=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.positions[symbol] = position
        logger.info(f"Opened {side} position in {symbol}: {quantity} @ {entry_price}")
        
        return position
    
    def close_position(self, symbol: str, exit_price: float) -> Optional[Position]:
        """Close position"""
        if symbol not in self.positions:
            logger.warning(f"No position to close for {symbol}")
            return None
        
        position = self.positions[symbol]
        
        # Calculate realized PnL
        if position.side == 'long':
            pnl = (exit_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - exit_price) * position.quantity
        
        position.realized_pnl = pnl
        position.current_price = exit_price
        
        # Move to closed
        self.closed_positions.append(position)
        del self.positions[symbol]
        
        logger.info(f"Closed position in {symbol}: PnL ${pnl:.2f}")
        
        return position
    
    def update_price(self, symbol: str, current_price: float):
        """Update position mark price"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        position.current_price = current_price
        
        # Update unrealized PnL
        if position.side == 'long':
            position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
        else:
            position.unrealized_pnl = (position.entry_price - current_price) * position.quantity
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position by symbol"""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> List[Position]:
        """Get all open positions"""
        return list(self.positions.values())
    
    def get_total_exposure(self) -> float:
        """Get total portfolio exposure"""
        return sum(
            pos.quantity * pos.current_price 
            for pos in self.positions.values()
        )
    
    def get_total_unrealized_pnl(self) -> float:
        """Get total unrealized PnL"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())
