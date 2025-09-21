from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.notification_api import router as notification_router

app = FastAPI(title="Notification Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include notification router  
app.include_router(notification_router)

@app.get("/")
async def root():
    return {"service": "notification-service", "status": "operational", "features": ["send", "preferences", "history"]}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notification-service"}
