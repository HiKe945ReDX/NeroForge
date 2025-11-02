"""Rate limiting middleware"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from ..core.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window = 60  # 1 minute window
    
    async def __call__(self, request: Request, call_next):
        # Get client identifier (user_id or IP)
        client_id = request.client.host
        if hasattr(request.state, "user"):
            client_id = f"user:{request.state.user['user_id']}"
        else:
            client_id = f"ip:{client_id}"
        
        # Rate limit key
        now = int(time.time())
        window_key = f"rate_limit:{client_id}:{now // self.window}"
        
        # Check rate limit
        count = await redis_client.incr(window_key, ttl=self.window)
        
        if count > self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_id}: {count} requests")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Try again later.",
                    "retry_after": self.window
                }
            )
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_per_minute - count))
        response.headers["X-RateLimit-Reset"] = str((now // self.window + 1) * self.window)
        
        return response

rate_limiter = RateLimiter(requests_per_minute=60)
