import os
from motor.motor_asyncio import AsyncIOMotorClient

# ✅ PRODUCTION: Only use environment variables
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is required")

JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret")
API_KEY = os.getenv("API_KEY", "")

client = AsyncIOMotorClient(MONGO_URI)
database = client.guidora

async def get_database():
    return database
