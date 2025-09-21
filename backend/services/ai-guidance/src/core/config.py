
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Secure configuration for AI Guidance Service
    Uses environment variables instead of hardcoded values
    """
    
    # Service Configuration
    service_name: str = Field(default="ai-guidance-service", env="SERVICE_NAME")
    service_host: str = Field(default="0.0.0.0", env="SERVICE_HOST")
    service_port: int = Field(default=5001, env="AI_GUIDANCE_PORT")
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
    session_secret: str = Field(..., env="SESSION_SECRET")
    
    # 🔗 OAUTH - SECURE
    github_client_id: str = Field(..., env="GITHUB_CLIENT_ID")
    github_client_secret: str = Field(..., env="GITHUB_CLIENT_SECRET")
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    
    # 🔴 REDIS - SECURE
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    redis_ttl_seconds: int = Field(default=3600, env="REDIS_TTL_SECONDS")
    
    # 🌐 FRONTEND & CORS
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    allowed_origins: str = Field(default="http://localhost:3000", env="ALLOWED_ORIGINS")
    
    # ⚡ PERFORMANCE
    max_resume_size_mb: int = Field(default=10, env="MAX_RESUME_SIZE_MB")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    cache_llm_responses: bool = Field(default=True, env="CACHE_LLM_RESPONSES")
    
    # 🎮 FEATURE FLAGS
    demo_mode: bool = Field(default=True, env="DEMO_MODE")
    linkedin_scraper_enabled: bool = Field(default=True, env="LINKEDIN_SCRAPER_ENABLED")
    
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
            'MONGODB_URL', 'GEMINI_API_KEY', 'JWT_SECRET',
            'GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET',
            'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'
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
    print("✅ AI Guidance Service: All environment variables validated successfully")
except ValueError as e:
    print(f"❌ AI Guidance Service: {e}")
