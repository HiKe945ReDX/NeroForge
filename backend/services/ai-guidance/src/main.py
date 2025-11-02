from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.psychometric import router as psychometric_router
from src.api.empathy import router as empathy_router
from src.api.discovery import router as discovery_router
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Guidora AI Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers (they already have /api/X prefixes in their routers)
app.include_router(psychometric_router)
logger.info("✅ Registered psychometric router: /api/psychometric")

app.include_router(empathy_router)
logger.info("✅ Registered empathy router: /api/empathy")

app.include_router(discovery_router)
logger.info("✅ Registered discovery router: /api/careers")

# Log all registered routes on startup
@app.on_event("startup")
async def startup_event():
    routes = [{"path": route.path, "name": route.name} for route in app.routes]
    logger.info(f"📋 Registered routes: {routes}")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai-guidance"}

@app.get("/")
async def root():
    return {
        "service": "guidora-ai",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/api/psychometric/questions",
            "/api/psychometric/complete",
            "/api/empathy/questions",
            "/api/empathy/submit",
            "/api/careers/discover"
        ]
    }
EOF
