from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

# Track startup state
app_ready = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown"""
    global app_ready
    
    # STARTUP
    logger.info("🚀 Starting application...")
    try:
        # Connect to MongoDB at startup
        from .database import init_db
        await init_db()
        logger.info("✅ MongoDB connected at startup")
        app_ready = True
    except Exception as e:
        logger.error(f"⚠️ MongoDB connection failed (non-critical): {e}")
        app_ready = False  # Still allow startup, will retry per-request
    
    yield
    
    # SHUTDOWN
    logger.info("👋 Shutting down...")
    from .database import close_db
    await close_db()

app = FastAPI(
    title="Guidora Context Service",
    lifespan=lifespan
)

# Health check endpoint
@app.get("/health")
async def health():
    """Quick health check for Cloud Run"""
    return {"status": "healthy", "ready": app_ready}

@app.get("/ready")
async def readiness():
    """Readiness probe - checks dependencies"""
    if not app_ready:
        return {"status": "warming up", "ready": False}, 503
    return {"status": "ready", "ready": True}
