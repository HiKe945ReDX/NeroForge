"""
🎯 ACTIVITY TRACKING MIDDLEWARE - Auto-Track User Behavior
Automatic Instagram-style user activity tracking for all API calls
"""
from fastapi import Request, Response
from fastapi.routing import APIRoute
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import uuid
import time
import json

from ..models.activity import UserActivity, ActivityType
from ..core.database import get_database
from ..services.analytics import process_real_time_analytics

class ActivityTrackingMiddleware:
    """
    🎯 Automatic Activity Tracking Middleware
    Tracks all user interactions automatically like Instagram/Google Analytics
    """
    
    def __init__(self):
        self.excluded_paths = {
            "/docs", "/redoc", "/openapi.json", "/health",
            "/api/v1/activity/track"  # Avoid infinite loops
        }
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process request and automatically track activity"""
        
        # Skip tracking for excluded paths
        if any(excluded in str(request.url) for excluded in self.excluded_paths):
            return await call_next(request)
        
        # Extract user info (if authenticated)
        user_id = await self._extract_user_id(request)
        if not user_id:
            return await call_next(request)  # Skip if no user
        
        # Track activity start
        start_time = time.time()
        session_id = await self._get_or_create_session(request, user_id)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_seconds = int(time.time() - start_time)
        
        # Track the activity asynchronously
        await self._track_request_activity(
            request=request,
            response=response,
            user_id=user_id,
            session_id=session_id,
            duration_seconds=duration_seconds
        )
        
        return response

    async def _track_request_activity(
        self, 
        request: Request, 
        response: Response, 
        user_id: str, 
        session_id: str,
        duration_seconds: int
    ):
        """Track the request as a user activity"""
        
        try:
            # Determine activity type from request
            activity_type = self._determine_activity_type(request, response)
            
            # Extract feature name from URL path
            feature_name = self._extract_feature_name(request.url.path)
            
            # Get device info
            device_info = self._extract_device_info(request)
            
            # Create activity record
            activity = UserActivity(
                user_id=user_id,
                session_id=session_id,
                activity_type=activity_type,
                feature_name=feature_name,
                page_url=str(request.url),
                page_title=self._extract_page_title(request.url.path),
                duration_seconds=duration_seconds,
                referrer=request.headers.get("Referer"),
                user_agent=request.headers.get("User-Agent"),
                device_info=device_info,
                screen_resolution=request.headers.get("X-Screen-Resolution"),
                viewport_size=request.headers.get("X-Viewport-Size"),
                metadata={
                    "method": request.method,
                    "status_code": response.status_code,
                    "response_time_ms": duration_seconds * 1000,
                    "endpoint": request.url.path,
                    "query_params": dict(request.query_params)
                },
                timestamp=datetime.utcnow()
            )
            
            # Store activity in database
            db = await get_database()
            await db.user_activities.insert_one(activity.dict())
            
            # Process real-time analytics
            await process_real_time_analytics(user_id, activity.dict())
            
        except Exception as e:
            print(f"Activity tracking failed: {e}")
            # Don't fail the request if tracking fails

# Middleware setup function
def setup_activity_tracking_middleware(app):
    """Setup activity tracking middleware for FastAPI app"""
    
    middleware = ActivityTrackingMiddleware()
    
    @app.middleware("http")
    async def track_activity(request: Request, call_next):
        return await middleware(request, call_next)
    
    return app
