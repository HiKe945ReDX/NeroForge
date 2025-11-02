import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB - Read MONGODB_URL from .env, fall back to MONGODB_URI for GCP
    MONGODB_URI: str = os.getenv("MONGODB_URL", os.getenv("MONGODB_URI", "mongodb://localhost:27017/guidora"))
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET: str = "secret"
    JWT_EXPIRATION_MINUTES: str = "15"
    
    # Session
    SESSION_SECRET: str = "secret"
    
    # Email
    EMAIL_BACKEND: str = "console"
    FROM_EMAIL: str = "noreply@guidora.ai"
    FROM_NAME: str = "Guidora"
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
