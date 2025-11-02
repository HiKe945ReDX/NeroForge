from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import router as endpoints_router

app = FastAPI(title="Portfolio Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(endpoints_router)

@app.get("/")
async def root():
    return {"service": "portfolio-service", "status": "operational", "features": ["portfolio-generation", "templates", "export"]}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "portfolio-service"}
