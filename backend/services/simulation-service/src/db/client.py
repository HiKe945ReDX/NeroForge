from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import get_settings

class DatabaseClient:
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.db = None
    
    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(
                self.settings.mongodb_url,
                serverSelectionTimeoutMS=5000
            )
            self.db = self.client[self.settings.mongodb_db_name]
            await self.client.admin.command('ismaster')
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    async def disconnect(self):
        if self.client:
            self.client.close()

db_client = DatabaseClient()
