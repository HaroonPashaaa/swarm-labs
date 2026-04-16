"""
Tests for Cache Manager
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from core.cache import CacheManager

@pytest.fixture
def cache():
    return CacheManager(redis_client=None)

def test_cache_set_and_get(cache):
    """Test basic cache operations"""
    cache.set('test_key', 'test_value', ttl=300)
    
    value = cache.get('test_key')
    
    assert value == 'test_value'

def test_cache_expiration(cache):
    """Test cache expiration"""
    # Set with very short TTL
    cache.set('expiring_key', 'value', ttl=0)
    
    # Should be expired
    value = cache.get('expiring_key')
    
    assert value is None

def test_cache_delete(cache):
    """Test cache deletion"""
    cache.set('delete_key', 'value')
    cache.delete('delete_key')
    
    value = cache.get('delete_key')
    
    assert value is None

def test_generate_key(cache):
    """Test key generation"""
    key1 = cache.generate_key('prefix', 'arg1', 'arg2')
    key2 = cache.generate_key('prefix', 'arg1', 'arg2')
    
    assert key1 == key2
    assert key1.startswith('prefix:')

def test_cache_clear(cache):
    """Test cache clearing"""
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    cache.clear()
    
    assert cache.get('key1') is None
    assert cache.get('key2') is None
