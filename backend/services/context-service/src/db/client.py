"""MongoDB Client - Production Grade"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseClient:
    """Singleton MongoDB client"""
    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        try:
            mongo_uri = os.getenv("MONGO_URI", os.getenv("MONGODB_URL"))
            if not mongo_uri:
                raise ValueError("MONGO_URI or MONGODB_URL environment variable required")
            
            cls.client = AsyncIOMotorClient(mongo_uri)
            cls.database = cls.client.get_database("guidora_db")
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info("✅ MongoDB connected successfully")
            
            # Create indexes (safe way - won't duplicate)
            await cls._ensure_indexes()
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise

    @classmethod
    async def _ensure_indexes(cls):
        """Create indexes safely (idempotent)"""
        try:
            # Personas collection
            await cls.database.personas.create_index(
                "user_id",
                unique=True,
                background=True,
                name="user_id_unique"
            )  # ← FIXED: Added closing parenthesis
            logger.info("✅ Indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning (may already exist): {e}")

    @classmethod
    async def close(cls):
        """Close connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

# Global database accessor
db = DatabaseClient.database
