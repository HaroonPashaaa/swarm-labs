"""
Redis Message Queue - Agent Communication Bus
Pub/Sub system for swarm coordination
"""

import redis
import json
import asyncio
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MessageBus:
    """Redis-based message bus for agent communication"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.handlers: Dict[str, Callable] = {}
        
    def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        """Publish message to channel"""
        try:
            message['timestamp'] = datetime.utcnow().isoformat()
            self.redis_client.publish(channel, json.dumps(message))
            logger.debug(f"Published to {channel}: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            return False
    
    def subscribe(self, channel: str, handler: Callable):
        """Subscribe to channel with handler"""
        self.pubsub.subscribe(channel)
        self.handlers[channel] = handler
        logger.info(f"Subscribed to channel: {channel}")
    
    def unsubscribe(self, channel: str):
        """Unsubscribe from channel"""
        self.pubsub.unsubscribe(channel)
        if channel in self.handlers:
            del self.handlers[channel]
        logger.info(f"Unsubscribed from channel: {channel}")
    
    async def listen(self):
        """Listen for messages (run in async loop)"""
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                channel = message['channel']
                data = json.loads(message['data'])
                
                if channel in self.handlers:
                    try:
                        await self.handlers[channel](data)
                    except Exception as e:
                        logger.error(f"Error handling message on {channel}: {e}")
    
    def send_direct(self, agent_id: str, message: Dict[str, Any]):
        """Send direct message to specific agent"""
        channel = f"agent:{agent_id}"
        return self.publish(channel, message)
    
    def broadcast(self, message: Dict[str, Any]):
        """Broadcast to all agents"""
        return self.publish("swarm:broadcast", message)
    
    def signal_openclaw(self, message: Dict[str, Any]):
        """Send signal to OpenClaw for decision"""
        return self.publish("openclaw:signals", message)

class SwarmChannels:
    """Channel names for swarm communication"""
    
    # Market data broadcasts
    CRYPTO_DATA = "market:crypto"
    FOREX_DATA = "market:forex"
    FUTURES_DATA = "market:futures"
    
    # Agent coordination
    AGENT_DECISIONS = "swarm:decisions"
    STRATEGY_VOTES = "swarm:votes"
    RISK_ALERTS = "swarm:risk"
    
    # OpenClaw channels
    OPENCLAW_COMMANDS = "openclaw:commands"
    OPENCLAW_DECISIONS = "openclaw:decisions"
    
    # Trade execution
    TRADE_SIGNALS = "execution:signals"
    TRADE_CONFIRMATIONS = "execution:confirmations"
    
    # System
    SYSTEM_STATUS = "system:status"
    SYSTEM_ALERTS = "system:alerts"
