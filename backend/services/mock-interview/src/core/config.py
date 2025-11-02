import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = os.getenv("MONGO_URI")
    mongodb_dbname: str = "guidoradb"
    jwt_secret: str = os.getenv("JWT_SECRET")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
