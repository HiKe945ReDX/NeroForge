"""Redis client for caching and rate limiting"""
import redis.asyncio as redis
from typing import Optional
import json
import logging
from .config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            await self.client.ping()
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.client:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = 300):
        """Set value in cache with TTL (default 5 min)"""
        if not self.client:
            return False
        try:
            await self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.client:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    async def incr(self, key: str, ttl: int = 60) -> int:
        """Increment counter (for rate limiting)"""
        if not self.client:
            return 0
        try:
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, ttl)
            results = await pipe.execute()
            return results[0]
        except Exception as e:
            logger.error(f"Redis INCR error: {e}")
            return 0

redis_client = RedisClient()
