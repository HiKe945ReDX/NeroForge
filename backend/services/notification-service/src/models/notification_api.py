from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

router = APIRouter()

class NotificationRequest(BaseModel):
    user_id: str
    type: str
    title: str
    message: str
    channels: List[str]

@router.post("/send")
async def send_notification(request: NotificationRequest):
    """Send notification to user"""
    return {
        "notification_id": f"notif_{request.user_id}_{int(datetime.utcnow().timestamp())}",
        "user_id": request.user_id,
        "type": request.type,
        "title": request.title,
        "message": request.message,
        "channels": request.channels,
        "status": "sent",
        "delivery_status": {
            channel: "delivered" for channel in request.channels
        },
        "sent_at": datetime.utcnow().isoformat()
    }

@router.get("/preferences/{user_id}")
async def get_notification_preferences(user_id: str):
    """Get user notification preferences"""
    return {
        "user_id": user_id,
        "preferences": {
            "email": True,
            "push": True,
            "sms": False,
            "frequency": "immediate"
        },
        "categories": {
            "achievement": True,
            "reminder": True,
            "update": True,
            "marketing": False
        },
        "updated_at": datetime.utcnow().isoformat()
    }

@router.put("/preferences/{user_id}")
async def update_notification_preferences(user_id: str, preferences: dict):
    """Update user notification preferences"""
    return {
        "user_id": user_id,
        "preferences": preferences,
        "status": "updated",
        "updated_at": datetime.utcnow().isoformat()
    }

@router.get("/history/{user_id}")
async def get_notification_history(user_id: str):
    """Get user notification history"""
    return {
        "user_id": user_id,
        "notifications": [
            {
                "id": "notif_001",
                "type": "achievement",
                "title": "Congratulations!",
                "message": "You've earned a new badge!",
                "channels": ["email", "push"],
                "sent_at": "2024-09-21T10:30:00Z",
                "status": "delivered"
            },
            {
                "id": "notif_002", 
                "type": "reminder",
                "title": "Complete your profile",
                "message": "Add your skills to get better recommendations",
                "channels": ["push"],
                "sent_at": "2024-09-20T15:45:00Z",
                "status": "read"
            }
        ],
        "total_count": 2,
        "unread_count": 0
    }

@router.get("/health")
async def notification_health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "notification-service", 
        "features": ["send", "preferences", "history"],
        "timestamp": datetime.utcnow().isoformat()
    }
