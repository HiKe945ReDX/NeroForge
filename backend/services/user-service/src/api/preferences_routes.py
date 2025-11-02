from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/users", tags=["preferences"])

class PreferenceRequest(BaseModel):
    userId: str
    careers: List[str]
    industries: List[str] = []
    workStyle: str = "hybrid"
    location: str = "worldwide"

@router.post("/preferences/save")
async def save_preferences(request: PreferenceRequest):
    """Save user career preferences to MongoDB"""
    try:
        # MongoDB save (replace with actual DB call)
        # db.user_preferences.update_one(
        #     {"userId": request.userId},
        #     {"$set": request.dict()},
        #     upsert=True
        # )
        
        return {
            "success": True,
            "message": "Preferences saved",
            "careersSelected": len(request.careers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preferences/{userId}")
async def get_preferences(userId: str):
    """Get user preferences"""
    try:
        # Mock response
        prefs = {
            "careers": ["software-engineer"],
            "industries": ["Tech"],
            "workStyle": "hybrid"
        }
        return {"success": True, "preferences": prefs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
