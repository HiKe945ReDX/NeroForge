"""
📧 NOTIFICATION MODELS - Multi-Channel Notification System
Advanced notification delivery with personalization and scheduling
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    """Types of notifications"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"

class Notification(BaseModel):
    """Individual notification instance"""
    notification_id: str = Field(..., description="Unique notification identifier")
    user_id: str = Field(..., description="Target user identifier")
    
    # Notification content
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    html_content: Optional[str] = Field(None, description="HTML content for rich notifications")
    
    # Delivery settings
    notification_type: NotificationType = Field(..., description="Delivery channel")
    priority: str = Field(default="medium")
    
    # Delivery tracking
    status: NotificationStatus = Field(default=NotificationStatus.PENDING)
    sent_at: Optional[datetime] = Field(None)
    delivered_at: Optional[datetime] = Field(None)
    read_at: Optional[datetime] = Field(None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: str = Field(..., description="User identifier")
    
    # Channel preferences
    email_enabled: bool = Field(default=True)
    sms_enabled: bool = Field(default=False)
    push_enabled: bool = Field(default=True)
    in_app_enabled: bool = Field(default=True)
    
    # Category preferences
    welcome_notifications: bool = Field(default=True)
    reminder_notifications: bool = Field(default=True)
    achievement_notifications: bool = Field(default=True)
    marketing_notifications: bool = Field(default=False)
