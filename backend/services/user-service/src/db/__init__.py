import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

# ✅ PRODUCTION: Only use environment variables
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is required")

client = AsyncIOMotorClient(MONGO_URI)
db = client["guidoradb"]

async def get_database():
    """Get database connection"""
    try:
        await client.admin.command('ping')
        return db
    except ConnectionFailure as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")

async def close_database():
    """Close database connection"""
    client.close()
