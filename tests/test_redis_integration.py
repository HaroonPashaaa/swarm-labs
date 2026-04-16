"""
Integration tests for Redis queue
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from core.redis_queue import MessageBus, SwarmChannels

@pytest.fixture
def message_bus():
    with patch('redis.Redis'):
        bus = MessageBus()
        bus.redis_client = Mock()
        bus.pubsub = Mock()
        return bus

def test_publish_message(message_bus):
    """Test message publishing"""
    message_bus.redis_client.publish = Mock(return_value=1)
    
    result = message_bus.publish('test_channel', {'test': 'data'})
    
    assert result == True
    message_bus.redis_client.publish.assert_called_once()

def test_subscribe_to_channel(message_bus):
    """Test channel subscription"""
    handler = Mock()
    
    message_bus.subscribe('test_channel', handler)
    
    assert 'test_channel' in message_bus.handlers
    assert message_bus.handlers['test_channel'] == handler

def test_direct_message(message_bus):
    """Test direct message to agent"""
    message_bus.publish = Mock(return_value=True)
    
    message_bus.send_direct('agent_1', {'command': 'test'})
    
    message_bus.publish.assert_called_with('agent:agent_1', {'command': 'test'})

def test_broadcast(message_bus):
    """Test broadcast to all agents"""
    message_bus.publish = Mock(return_value=True)
    
    message_bus.broadcast({'alert': 'test'})
    
    message_bus.publish.assert_called_with('swarm:broadcast', {'alert': 'test'})
