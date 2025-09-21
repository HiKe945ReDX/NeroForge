"""
🔒 SECURE CONFIGURATION - GAMIFICATION SERVICE
All sensitive values loaded from environment variables
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Secure configuration for Gamification Service
    Uses environment variables instead of hardcoded values
    """
    
    # Service Configuration
    service_name: str = Field(default="gamification-service", env="SERVICE_NAME")
    service_host: str = Field(default="0.0.0.0", env="SERVICE_HOST")
    service_port: int = Field(default=5003, env="GAMIFICATION_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # 🔐 DATABASE - SECURE (NO HARDCODED VALUES)
    mongodb_url: str = Field(..., env="MONGODB_URL")
    mongodb_db_name: str = Field(default="guidora_db", env="MONGODB_DB_NAME")
    mongodb_max_connections: int = Field(default=100, env="MONGODB_MAX_CONNECTIONS")
    
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
    
    # 🎮 FEATURE FLAGS
    demo_mode: bool = Field(default=True, env="DEMO_MODE")
    
    # 🏆 GAMIFICATION SPECIFIC
    points_system_enabled: bool = Field(default=True, env="POINTS_SYSTEM_ENABLED")
    achievements_enabled: bool = Field(default=True, env="ACHIEVEMENTS_ENABLED")
    leaderboard_enabled: bool = Field(default=True, env="LEADERBOARD_ENABLED")
    daily_challenges_enabled: bool = Field(default=True, env="DAILY_CHALLENGES_ENABLED")
    
    # Points Configuration
    points_resume_upload: int = Field(default=10, env="POINTS_RESUME_UPLOAD")
    points_skill_assessment: int = Field(default=25, env="POINTS_SKILL_ASSESSMENT")
    points_career_exploration: int = Field(default=15, env="POINTS_CAREER_EXPLORATION")
    points_daily_login: int = Field(default=5, env="POINTS_DAILY_LOGIN")
    
    # Leaderboard Settings
    leaderboard_cache_ttl: int = Field(default=3600, env="LEADERBOARD_CACHE_TTL")  # 1 hour
    leaderboard_max_entries: int = Field(default=100, env="LEADERBOARD_MAX_ENTRIES")
    
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
            'MONGODB_URL', 'JWT_SECRET'
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
    print("✅ Gamification Service: All environment variables validated successfully")
except ValueError as e:
    print(f"❌ Gamification Service: {e}")
