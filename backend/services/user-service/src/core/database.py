from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import redis.asyncio as redis
from typing import Optional
import logging
from .config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.mongodb_client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to databases"""
        try:
            # MongoDB
            self.mongodb_client = AsyncIOMotorClient(
                settings.mongodb_url,
                maxPoolSize=settings.mongodb_max_connections
            )
            
            # Test connection
            await self.mongodb_client.admin.command('ping')
            self.database = self.mongodb_client[settings.mongodb_db_name]
            
            logger.info("✅ Connected to MongoDB")
            
            # Redis
            self.redis_client = redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                decode_responses=True
            )
            
            # Test Redis connection
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close database connections"""
        if self.mongodb_client:
            self.mongodb_client.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("🔌 Database connections closed")
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get MongoDB database instance"""
        if not self.database:
            await self.connect()
        return self.database
    
    async def get_redis(self) -> redis.Redis:
        """Get Redis client instance"""
        if not self.redis_client:
            await self.connect()
        return self.redis_client

# Global database manager
db_manager = DatabaseManager()

async def get_database() -> AsyncIOMotorDatabase:
    """Dependency for getting database"""
    return await db_manager.get_database()

async def get_redis() -> redis.Redis:
    """Dependency for getting Redis client"""
    return await db_manager.get_redis()

async def close_database_connection():
    """Close database connection - placeholder function"""
    try:
        # Database connection cleanup logic would go here
        print("Database connection closed")
    except Exception as e:
        print(f"Warning: Database cleanup failed: {e}")
