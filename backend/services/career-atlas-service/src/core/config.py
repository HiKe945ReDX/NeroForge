"""
🔒 SECURE CONFIGURATION - CAREER ATLAS SERVICE
All sensitive values loaded from environment variables
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Secure configuration for Career Atlas Service
    Uses environment variables instead of hardcoded values
    """
    
    # Service Configuration
    service_name: str = Field(default="career-atlas-service", env="SERVICE_NAME")
    service_host: str = Field(default="0.0.0.0", env="SERVICE_HOST")
    service_port: int = Field(default=5002, env="CAREER_ATLAS_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # 🔐 DATABASE - SECURE (NO HARDCODED VALUES)
    mongodb_url: str = Field(..., env="MONGODB_URL")
    mongodb_db_name: str = Field(default="guidora_db", env="MONGODB_DB_NAME")
    mongodb_max_connections: int = Field(default=100, env="MONGODB_MAX_CONNECTIONS")
    
    # 🤖 AI CONFIGURATION - SECURE
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    google_project_id: str = Field(default="guidora-main", env="GOOGLE_PROJECT_ID")
    google_location: str = Field(default="us-central1", env="GOOGLE_LOCATION")
    google_application_credentials: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")
    genai_timeout_seconds: int = Field(default=60, env="GENAI_TIMEOUT_SECONDS")
    
    # 🔑 AUTHENTICATION - SECURE
    jwt_secret: str = Field(..., env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_minutes: int = Field(default=1440, env="JWT_EXPIRATION_MINUTES")
    
    # 🔴 REDIS - SECURE
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    redis_ttl_seconds: int = Field(default=3600, env="REDIS_TTL_SECONDS")
    
    # 🌐 FRONTEND & CORS
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    allowed_origins: str = Field(default="http://localhost:3000", env="ALLOWED_ORIGINS")
    
    # ⚡ PERFORMANCE
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    cache_llm_responses: bool = Field(default=True, env="CACHE_LLM_RESPONSES")
    
    # 🎮 FEATURE FLAGS
    demo_mode: bool = Field(default=True, env="DEMO_MODE")
    
    # 🗺️ CAREER ATLAS SPECIFIC
    knowledge_graph_enabled: bool = Field(default=True, env="KNOWLEDGE_GRAPH_ENABLED")
    skill_mapping_enabled: bool = Field(default=True, env="SKILL_MAPPING_ENABLED")
    career_paths_cache_ttl: int = Field(default=86400, env="CAREER_PATHS_CACHE_TTL")  # 24 hours
    
    class Config:
        # Look for .env file at project root
        env_file = [
            "../../../.env",  # From service perspective
            ".env",           # Fallback
        ]
        case_sensitive = False
        
    def validate_required_env_vars(self):
        """Validate that all required environment variables are set"""
        required_vars = [
            'MONGODB_URL', 'GEMINI_API_KEY', 'JWT_SECRET'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")

# Global settings instance
settings = Settings()

# Validate on import
try:
    settings.validate_required_env_vars()
    print("✅ Career Atlas Service: All environment variables validated successfully")
except ValueError as e:
    print(f"❌ Career Atlas Service: {e}")

from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_url: str = "mongodb+srv://guidora_admin:Sris0945@sris0945.yim8u.mongodb.net/guidora_db?retryWrites=true&w=majority&appName=Sris0945"
    mongodb_db_name: str = "guidora_db"
    redis_url: str = "redis://:guidoraredis@redis:6379"
    jwt_secret: str = "guidora_super_secure_jwt_secret_key_2025"
    
    class Config:
        env_file = ".env"

settings = Settings()

def get_settings():
    return settings
