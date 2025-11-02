import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB - Read MONGODB_URL from .env, fall back to MONGODB_URI for GCP
    MONGODB_URI: str = os.getenv("MONGODB_URL", os.getenv("MONGODB_URI", "mongodb://localhost:27017/guidora"))
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET: str = "secret"
    
    # Gemini API (for news summarization)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
