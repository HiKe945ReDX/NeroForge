from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from ..core.database import get_database
import hashlib

router = APIRouter()

# Request/Response Models
class UserBasicInfo(BaseModel):
    userId: Optional[str] = None
    name: str
    email: EmailStr
    phone: Optional[str] = None
    educationLevel: str
    currentField: Optional[str] = None

class CareerPreferences(BaseModel):
    userId: str
    targetCareer: Optional[str] = None
    industries: List[str] = []
    workStyle: Optional[str] = None
    salaryExpectation: Optional[int] = None
    geographic: Optional[str] = None
    explorationData: Optional[dict] = None

# POST /api/users/profile - Register/Update User
@router.post("/profile")
async def create_or_update_profile(
    user: UserBasicInfo,
    db=Depends(get_database)
):
    """Register new user or update existing profile"""
    try:
        # Generate userId if not provided
        if not user.userId:
            user.userId = hashlib.md5(f"{user.email}{datetime.utcnow().timestamp()}".encode()).hexdigest()[:12]
        
        user_data = user.dict()
        user_data["createdAt"] = datetime.utcnow().isoformat()
        user_data["updatedAt"] = datetime.utcnow().isoformat()
        
        # Upsert to MongoDB
        await db.users.update_one(
            {"userId": user.userId},
            {"$set": user_data},
            upsert=True
        )
        
        return {
            "success": True,
            "userId": user.userId,
            "message": f"Profile for {user.name} saved successfully",
            "profile": user_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /api/users/profile/{user_id} - Get User Profile
@router.get("/profile/{user_id}")
async def get_user_profile(
    user_id: str,
    db=Depends(get_database)
):
    """Retrieve user profile"""
    user = await db.users.find_one({"userId": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.pop("_id", None)
    return user

# POST /api/users/preferences - Save Career Preferences
@router.post("/preferences")
async def save_career_preferences(
    preferences: CareerPreferences,
    db=Depends(get_database)
):
    """Save user career preferences"""
    try:
        pref_data = preferences.dict()
        pref_data["updatedAt"] = datetime.utcnow().isoformat()
        
        await db.career_preferences.update_one(
            {"userId": preferences.userId},
            {"$set": pref_data},
            upsert=True
        )
        
        return {
            "success": True,
            "status": "saved",
            "userId": preferences.userId,
            "message": "Career preferences saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /api/users/preferences/{user_id} - Get Preferences
@router.get("/preferences/{user_id}")
async def get_career_preferences(
    user_id: str,
    db=Depends(get_database)
):
    """Retrieve career preferences"""
    prefs = await db.career_preferences.find_one({"userId": user_id})
    
    if not prefs:
        raise HTTPException(status_code=404, detail="No preferences found")
    
    prefs.pop("_id", None)
    return prefs

# Health Check
@router.get("/health")
async def user_service_health():
    return {
        "status": "healthy",
        "service": "user-service",
        "features": ["registration", "profiles", "preferences", "activity-tracking"],
        "timestamp": datetime.utcnow().isoformat()
    }
