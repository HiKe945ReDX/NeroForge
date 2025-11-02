"""Request size and complexity limiter"""
from fastapi import Request, HTTPException
from starlette.datastructures import UploadFile
import logging

logger = logging.getLogger(__name__)

class RequestLimiter:
    """Limit request size and complexity"""
    
    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_JSON_DEPTH = 10
    MAX_ARRAY_LENGTH = 1000
    
    async def __call__(self, request: Request, call_next):
        """Check request limits"""
        # Check content-length header
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Request too large. Maximum: {self.MAX_BODY_SIZE / 1024 / 1024}MB"
            )
        
        response = await call_next(request)
        return response
    
    @classmethod
    def validate_json_depth(cls, obj, depth=0):
        """Recursively check JSON depth"""
        if depth > cls.MAX_JSON_DEPTH:
            raise HTTPException(status_code=400, detail="JSON too deeply nested")
        
        if isinstance(obj, dict):
            for value in obj.values():
                cls.validate_json_depth(value, depth + 1)
        elif isinstance(obj, list):
            if len(obj) > cls.MAX_ARRAY_LENGTH:
                raise HTTPException(status_code=400, detail=f"Array too large (max {cls.MAX_ARRAY_LENGTH})")
            for item in obj:
                cls.validate_json_depth(item, depth + 1)

request_limiter = RequestLimiter()
