from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from contextlib import asynccontextmanager

# Configure logging FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database functions with error handling
try:
    from src.core.database import connect_to_mongo, close_mongo_connection
except Exception as e:
    logger.error(f"❌ Failed to import database: {e}")
    async def connect_to_mongo():
        logger.warning("⚠️  MongoDB connection skipped - using fallback")
        pass
    async def close_mongo_connection():
        pass

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("🚀 User Service Starting...")
        await connect_to_mongo()
        logger.info("✓ MongoDB Connected")
    except Exception as e:
        logger.warning(f"⚠️  MongoDB failed (will retry on request): {e}")
    
    yield
    
    # Shutdown
    try:
        await close_mongo_connection()
        logger.info("👋 User Service Shutting Down")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="Guidora User Service",
    description="User management, profiles, skills, and empathy assessments",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Import routers with error handling
try:
    from src.api.users import router as users_router
    app.include_router(users_router, prefix="/api/users", tags=["users"])
    logger.info("✓ Users router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load users router: {e}")

try:
    from src.api.skills import router as skills_router
    app.include_router(skills_router, prefix="/api", tags=["skills"])
    logger.info("✓ Skills router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load skills router: {e}")

try:
    from src.api.empathy import router as empathy_router
    app.include_router(empathy_router, prefix="/api/empathy", tags=["empathy"])
    logger.info("✓ Empathy router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load empathy router: {e}")

# Root
@app.get("/")
async def root():
    return {
        "service": "user-service",
        "status": "operational",
        "version": "2.0.0",
        "endpoints": [
            "/api/users/profile",
            "/api/users/preferences",
            "/api/skills/search",
            "/api/empathy/questions"
        ]
    }

# Health
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "user-service"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
