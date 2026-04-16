"""
Cache Manager
In-memory and Redis caching utilities
"""

import json
import pickle
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta

class CacheManager:
    """Manage caching for frequently accessed data"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.local_cache = {}
        self.default_ttl = 300  # 5 minutes
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Try local cache first
        if key in self.local_cache:
            value, expiry = self.local_cache[key]
            if datetime.utcnow() < expiry:
                return value
            else:
                del self.local_cache[key]
        
        # Try Redis
        if self.redis:
            try:
                data = self.redis.get(key)
                if data:
                    return pickle.loads(data)
            except Exception:
                pass
        
        return None
        
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        expiry = datetime.utcnow() + timedelta(seconds=ttl)
        
        # Local cache
        self.local_cache[key] = (value, expiry)
        
        # Redis cache
        if self.redis:
            try:
                serialized = pickle.dumps(value)
                self.redis.setex(key, ttl, serialized)
            except Exception:
                pass
                
    def delete(self, key: str):
        """Delete from cache"""
        if key in self.local_cache:
            del self.local_cache[key]
        
        if self.redis:
            try:
                self.redis.delete(key)
            except Exception:
                pass
                
    def clear(self):
        """Clear all caches"""
        self.local_cache.clear()
        
        if self.redis:
            try:
                self.redis.flushdb()
            except Exception:
                pass
                
    def generate_key(self, prefix: str, *args) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps(args, sort_keys=True, default=str)
        hash_key = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{hash_key}"
