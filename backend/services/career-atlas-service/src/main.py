import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Career Atlas Service starting...")
    yield
    logger.info("🛑 Career Atlas Service shutting down...")

app = FastAPI(title="Career Atlas", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "career-atlas"}

@app.get("/")
async def root():
    return {"message": "Career Atlas Service", "status": "running"}

# Simple test endpoint
@app.get("/api/v1/careers")
async def get_careers():
    return {"careers": ["Software Engineer", "Data Scientist", "Product Manager"]}
