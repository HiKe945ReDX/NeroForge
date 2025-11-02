import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongodb_db_name: str = "guidoradb"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-key")
    
    class Config:
        env_file = ".env"

settings = Settings()
