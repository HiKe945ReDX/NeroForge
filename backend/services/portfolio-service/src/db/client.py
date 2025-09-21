from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings
from src.utils.logging import logger

class DatabaseClient:
    client: AsyncIOMotorClient = None
    database = None

async def connect_to_database():
    """Create database connection"""
    try:
        DatabaseClient.client = AsyncIOMotorClient(settings.mongodb_url)
        DatabaseClient.database = DatabaseClient.client[settings.mongodb_db_name]
        
        # Test connection
        await DatabaseClient.client.admin.command('ismaster')
        logger.info("✅ Connected to MongoDB successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise

async def close_database_connection():
    """Close database connection"""
    if DatabaseClient.client:
        DatabaseClient.client.close()
        logger.info("📦 Database connection closed")

async def get_database():
    """Get database instance"""
    return DatabaseClient.database
