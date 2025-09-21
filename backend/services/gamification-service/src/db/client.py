import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import redis.asyncio as redis
from typing import Optional
import logging
from datetime import datetime
from ..core.config import settings

logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self):
        self.mongodb_client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.redis_client: Optional[redis.Redis] = None

    async def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongodb_client = AsyncIOMotorClient(
                settings.mongodb_url,
                maxPoolSize=settings.mongodb_max_connections
            )
            
            await self.mongodb_client.admin.command('ping')
            self.database = self.mongodb_client[settings.mongodb_db_name]
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def connect_redis(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=True
            )
            
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Close all connections"""
        if self.mongodb_client:
            self.mongodb_client.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Disconnected from databases")

    async def health_check(self) -> dict:
        """Check health of database connections"""
        health_info = {
            "mongodb": "disconnected",
            "redis": "disconnected",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            if self.mongodb_client:
                await self.mongodb_client.admin.command('ping')
                health_info["mongodb"] = "connected"
        except:
            health_info["mongodb"] = "error"
        
        try:
            if self.redis_client:
                await self.redis_client.ping()
                health_info["redis"] = "connected"
        except:
            health_info["redis"] = "error"
        
        return health_info

# Global database instance
db_client = DatabaseClient()

async def get_database():
    """Dependency to get database instance"""
    return db_client.database

async def get_redis():
    """Dependency to get Redis instance"""
    return db_client.redis_client
