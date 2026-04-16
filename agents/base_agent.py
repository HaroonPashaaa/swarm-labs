"""
Base Agent Class
All swarm agents inherit from this
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

from core.redis_queue import MessageBus, SwarmChannels
from core.config import AGENT_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class Signal:
    """Trading signal from agent"""
    agent: str
    market: str
    symbol: str
    action: str  # buy, sell, hold
    confidence: float  # 0.0 to 1.0
    strategy: str
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class BaseAgent(ABC):
    """Abstract base class for all swarm agents"""
    
    def __init__(self, agent_id: str, market: str):
        self.agent_id = agent_id
        self.market = market
        self.bus = MessageBus(
            host=AGENT_CONFIG.REDIS_HOST,
            port=AGENT_CONFIG.REDIS_PORT,
            db=AGENT_CONFIG.REDIS_DB
        )
        self.running = False
        self.decision_interval = AGENT_CONFIG.DECISION_INTERVAL_SECONDS
        
    async def start(self):
        """Start the agent"""
        logger.info(f"Starting agent: {self.agent_id}")
        self.running = True
        
        # Subscribe to relevant channels
        self.bus.subscribe(f"agent:{self.agent_id}", self._handle_direct_message)
        self.bus.subscribe(SwarmChannels.OPENCLAW_COMMANDS, self._handle_command)
        self.bus.subscribe(SwarmChannels.SYSTEM_STATUS, self._handle_status)
        
        # Start message listener in background
        asyncio.create_task(self.bus.listen())
        
        # Start main loop
        await self._main_loop()
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping agent: {self.agent_id}")
        self.running = False
    
    async def _main_loop(self):
        """Main agent loop - override in subclasses"""
        while self.running:
            try:
                # Gather market data
                data = await self.gather_data()
                
                # Analyze and generate signal
                signal = await self.analyze(data)
                
                # Publish signal
                if signal:
                    await self.publish_signal(signal)
                
                # Wait for next cycle
                await asyncio.sleep(self.decision_interval)
                
            except Exception as e:
                logger.error(f"Error in agent {self.agent_id} main loop: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    @abstractmethod
    async def gather_data(self) -> Dict[str, Any]:
        """Gather market data - implement in subclass"""
        pass
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Optional[Signal]:
        """Analyze data and generate signal - implement in subclass"""
        pass
    
    async def publish_signal(self, signal: Signal):
        """Publish signal to swarm"""
        message = {
            'agent': signal.agent,
            'market': signal.market,
            'symbol': signal.symbol,
            'action': signal.action,
            'confidence': signal.confidence,
            'strategy': signal.strategy,
            'reasoning': signal.reasoning,
            'metadata': signal.metadata,
            'timestamp': signal.timestamp.isoformat()
        }
        
        # Publish to decisions channel
        self.bus.publish(SwarmChannels.AGENT_DECISIONS, message)
        
        # Also send to OpenClaw
        self.bus.signal_openclaw(message)
        
        logger.info(f"{self.agent_id} published signal: {signal.action} {signal.symbol} "
                   f"(confidence: {signal.confidence:.2f})")
    
    async def _handle_direct_message(self, message: Dict[str, Any]):
        """Handle direct message to this agent"""
        logger.debug(f"{self.agent_id} received direct message: {message}")
        # Override in subclass for specific handling
    
    async def _handle_command(self, message: Dict[str, Any]):
        """Handle command from OpenClaw"""
        target = message.get('target')
        if target == self.agent_id or target == 'all':
            command = message.get('command')
            logger.info(f"{self.agent_id} received command: {command}")
            await self.execute_command(command, message.get('params', {}))
    
    async def _handle_status(self, message: Dict[str, Any]):
        """Handle system status updates"""
        # Override in subclass if needed
        pass
    
    @abstractmethod
    async def execute_command(self, command: str, params: Dict[str, Any]):
        """Execute command from OpenClaw - implement in subclass"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'market': self.market,
            'running': self.running,
            'timestamp': datetime.utcnow().isoformat()
        }
