from motor.motor_asyncio import AsyncIOMotorClient
import logging
from .config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.mongodb_client = None
        self.database = None

    async def connect(self):
        try:
            # Use uppercase to match config.py
            self.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI, maxPoolSize=100)
            await self.mongodb_client.admin.command('ping')
            # Extract DB name from URI or use default
            db_name = settings.MONGODB_URI.split('/')[-1].split('?')[0] if '/' in settings.MONGODB_URI else 'guidora'
            self.database = self.mongodb_client[db_name]
            logger.info("✅ MongoDB connected")
        except Exception as e:
            logger.error(f"❌ MongoDB failed: {e}")
            raise

    async def disconnect(self):
        if self.mongodb_client:
            self.mongodb_client.close()

db_manager = DatabaseManager()

async def connect_to_mongo():
    await db_manager.connect()

async def close_mongo_connection():
    await db_manager.disconnect()

async def get_database():
    return db_manager.database
