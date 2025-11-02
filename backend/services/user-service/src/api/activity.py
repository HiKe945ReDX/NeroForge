from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

router = APIRouter()

class ActivityLog(BaseModel):
    user_id: str
    activity_type: str
    activity_data: Dict

@router.post("/activity/log")
async def log_activity(activity: ActivityLog):
    """Log user activity"""
    return {
        "success": True,
        "user_id": activity.user_id,
        "activity_type": activity.activity_type,
        "logged_at": datetime.utcnow().isoformat(),
        "message": f"Activity '{activity.activity_type}' logged successfully"
    }

@router.get("/activity/user/{user_id}")
async def get_user_activities(user_id: str):
    """Get user activities"""
    return {
        "user_id": user_id,
        "activities": [
            {
                "activity_type": "resume_upload",
                "timestamp": "2024-09-21T10:30:00Z",
                "data": {"feature_name": "resume_analysis", "duration_seconds": 120}
            },
            {
                "activity_type": "skill_assessment", 
                "timestamp": "2024-09-20T14:15:00Z",
                "data": {"feature_name": "psychometric", "score": 85}
            }
        ],
        "total_activities": 2
    }

@router.get("/activity/stats/{user_id}")
async def get_activity_stats(user_id: str):
    """Get user activity statistics"""
    return {
        "user_id": user_id,
        "stats": {
            "total_sessions": 15,
            "total_time_spent": "4h 32m",
            "most_used_feature": "resume_analysis",
            "features_used": ["resume_analysis", "psychometric", "roadmap_generation"],
            "last_active": datetime.utcnow().isoformat()
        }
    }

@router.get("/health")
async def activity_health():
    """Activity service health check"""
    return {
        "status": "healthy",
        "service": "activity-tracker",
        "features": ["activity-logging", "user-analytics", "statistics"]
    }
