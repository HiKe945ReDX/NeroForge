import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = os.getenv("MONGO_URI")
    mongodb_dbname: str = "guidoradb"
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    jwt_secret: str = os.getenv("JWT_SECRET")
    
    class Config:
        env_file = ".env"

settings = Settings()
