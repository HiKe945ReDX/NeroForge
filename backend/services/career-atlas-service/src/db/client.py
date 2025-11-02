from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from typing import Optional
import asyncio
import logging
from ..core.config import get_settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages connections to MongoDB Atlas and Redis
    Production-ready with connection pooling and error handling
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.mongodb_client: Optional[AsyncIOMotorClient] = None
        self.redis_client: Optional[redis.Redis] = None
        self.database = None
        self._mongodb_connected = False
        self._redis_connected = False
    
    async def connect(self):
        """Connect to MongoDB Atlas and Redis with error handling"""
        await asyncio.gather(
            self._connect_mongodb(),
            self._connect_redis(),
            return_exceptions=True
        )
        
        # Test connections
        await self.ping()
        
        logger.info("✅ Database connections established successfully")
    
    async def _connect_mongodb(self):
        """Connect to MongoDB Atlas"""
        try:
            self.mongodb_client = AsyncIOMotorClient(
                self.settings.mongodb_url,
                maxPoolSize=self.settings.mongodb_max_connections,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            self.database = self.mongodb_client[self.settings.mongodb_db_name]
            
            # Test connection
            await self.mongodb_client.admin.command('ping')
            self._mongodb_connected = True
            
            logger.info("✅ MongoDB Atlas connected successfully")
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {str(e)}")
            self._mongodb_connected = False
            raise
    
    async def _connect_redis(self):
        """Connect to Redis with password authentication"""
        try:
            redis_url = self.settings.redis_url
            if self.settings.redis_password:
                redis_url = f"redis://:{self.settings.redis_password}@redis:6379"
            
            self.redis_client = redis.from_url(
                redis_url,
                max_connections=self.settings.redis_max_connections,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis_client.ping()
            self._redis_connected = True
            
            logger.info("✅ Redis connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {str(e)}")
            self._redis_connected = False
            # Redis is optional - don't raise error
    
    async def disconnect(self):
        """Gracefully disconnect from databases"""
        try:
            if self.mongodb_client:
                self.mongodb_client.close()
                self._mongodb_connected = False
                logger.info("📴 MongoDB disconnected")
            
            if self.redis_client:
                await self.redis_client.close()
                self._redis_connected = False
                logger.info("📴 Redis disconnected")
                
        except Exception as e:
            logger.error(f"⚠️ Error during disconnect: {str(e)}")
    
    async def ping(self):
        """Test database connections and return status"""
        status = {
            "mongodb": False,
            "redis": False
        }
        
        # Test MongoDB
        if self.mongodb_client:
            try:
                await self.mongodb_client.admin.command('ping')
                status["mongodb"] = True
                self._mongodb_connected = True
            except Exception as e:
                logger.error(f"MongoDB ping failed: {str(e)}")
                status["mongodb"] = False
                self._mongodb_connected = False
        
        # Test Redis
        if self.redis_client:
            try:
                await self.redis_client.ping()
                status["redis"] = True
                self._redis_connected = True
            except Exception as e:
                logger.error(f"Redis ping failed: {str(e)}")
                status["redis"] = False
                self._redis_connected = False
        
        return status
    
    def get_collection(self, name: str):
        """Get MongoDB collection with error handling"""
        if not self.database:
            raise RuntimeError("❌ MongoDB not connected - cannot get collection")
        return self.database[name]
    
    async def cache_get(self, key: str):
        """Get from Redis cache with error handling"""
        if not self.redis_client or not self._redis_connected:
            logger.warning("⚠️ Redis not available - cache miss")
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return value.decode('utf-8')
            return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    async def cache_set(self, key: str, value: str, ttl: int = None):
        """Set to Redis cache with error handling"""
        if not self.redis_client or not self._redis_connected:
            logger.warning("⚠️ Redis not available - skipping cache")
            return False
        
        try:
            ttl = ttl or self.settings.redis_ttl_seconds
            await self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    @property
    def health_status(self) -> dict:
        return {
            "mongodb_connected": self._mongodb_connected,
            "redis_connected": self._redis_connected,
            "overall_health": self._mongodb_connected  # MongoDB is required
        }
