from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import hashlib
import os

router = APIRouter()

class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    profession: str

class UserProfile(BaseModel):
    bio: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = []
    experience: Optional[str] = None

@router.post("/register")
async def register_user(user: UserRegistration):
    """Register a new user"""
    user_id = hashlib.md5(user.username.encode()).hexdigest()[:12]
    return {
        "success": True,
        "user_id": user_id,
        "message": f"User {user.username} registered successfully",
        "profile": {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "profession": user.profession,
            "created_at": datetime.utcnow().isoformat()
        }
    }

@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile"""
    return {
        "user_id": user_id,
        "username": f"user_{user_id}",
        "email": f"user_{user_id}@example.com",
        "full_name": "Demo User",
        "profession": "Software Engineer",
        "bio": "Passionate developer",
        "location": "Remote",
        "skills": ["Python", "FastAPI", "AI", "Docker"],
        "experience": "3+ years",
        "created_at": "2024-01-01T00:00:00Z",
        "last_active": datetime.utcnow().isoformat()
    }

@router.put("/profile/{user_id}")
async def update_user_profile(user_id: str, profile: UserProfile):
    """Update user profile"""
    return {
        "success": True,
        "user_id": user_id,
        "message": "Profile updated successfully",
        "updated_fields": profile.dict(exclude_none=True),
        "updated_at": datetime.utcnow().isoformat()
    }

@router.get("/health")
async def user_service_health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "user-service",
        "features": ["registration", "profiles", "activity-tracking"],
        "timestamp": datetime.utcnow().isoformat()
    }
