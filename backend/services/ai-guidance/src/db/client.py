from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

class MongoDBClient:
    _client: AsyncIOMotorClient = None

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if cls._client is None:
            try:
                cls._client = AsyncIOMotorClient(settings.mongodb_url)
                logger.info("MongoDB client connected to %s", settings.mongodb_url)
            except Exception as e:
                logger.error(f"Failed to create MongoDB client: {e}")
                raise
        return cls._client

    @classmethod
    def get_database(cls):
        client = cls.get_client()
        db = client[settings.mongodb_db_name]
        return db

    @classmethod
    async def initialize(cls):
        """Initialize MongoDB connection and test connectivity"""
        try:
            client = cls.get_client()
            # Test the connection with a simple ping
            await client.admin.command('ping')
            logger.info("✅ MongoDB connection initialized successfully")
            
            # Optionally test database access
            db = cls.get_database()
            await db.list_collection_names()
            logger.info("✅ Database access verified")
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {e}")
            raise

    @classmethod
    async def close(cls):
        """Close MongoDB connection"""
        if cls._client:
            try:
                cls._client.close()
                cls._client = None
                logger.info("✅ MongoDB connection closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {e}")
                raise

    @classmethod
    def is_connected(cls) -> bool:
        """Check if MongoDB client is connected"""
        return cls._client is not None

    @classmethod
    async def health_check(cls) -> dict:
        """Perform health check on MongoDB connection"""
        try:
            if not cls.is_connected():
                return {"status": "disconnected", "error": "No active connection"}
            
            client = cls.get_client()
            # Ping with timeout
            result = await client.admin.command('ping')
            
            if result.get('ok') == 1:
                return {"status": "healthy", "connection": "active"}
            else:
                return {"status": "unhealthy", "error": "Ping failed"}
                
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
