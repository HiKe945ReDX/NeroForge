from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.users import router as users_router
from .api.activity import router as activity_router

app = FastAPI(title="User Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)
app.include_router(activity_router)

@app.get("/")
async def root():
    return {"service": "user-service", "status": "operational", "features": ["users", "activity"]}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "user-service"}
