from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # ❌ NO LOCALHOST - MONGO FROM SECRET MANAGER
    mongodb_url: str = os.getenv("MONGO_URI")  # From sm://guidora-mongodb-uri
    database_name: str = "guidora_users"
    
    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8080
    
    # ❌ NO LOCALHOST - JWT FROM SECRET MANAGER
    jwt_secret_key: str = os.getenv("JWT_SECRET")  # From sm://guidora-jwt-secret
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))
    
    # ❌ NO LOCALHOST - REDIS FROM SECRET MANAGER
    redis_url: str = os.getenv("REDIS_URL")  # From sm://guidora-redis-url
    
    # Email
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    email_username: str = os.getenv("EMAIL_USERNAME", "")
    email_password: str = os.getenv("EMAIL_PASSWORD", "")
    
    # ❌ NO LOCALHOST - GEMINI FROM SECRET MANAGER
    gemini_api_key: str = os.getenv("API_KEY")  # From sm://GEMINI_API_KEY
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    class Config:
        case_sensitive = False

settings = Settings()
