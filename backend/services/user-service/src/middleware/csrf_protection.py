"""CSRF protection for state-changing operations"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import secrets
import hmac
import hashlib
from typing import Optional
from ..utils.structured_logger import logger

class CSRFProtection:
    """
    CSRF protection using Double Submit Cookie pattern
    - For APIs with session cookies (not stateless JWT)
    - Validates CSRF token in header matches cookie
    """
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
        self.cookie_name = "csrf_token"
        self.header_name = "X-CSRF-Token"
    
    def generate_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def create_signature(self, token: str) -> str:
        """Create HMAC signature for token"""
        return hmac.new(
            self.secret_key,
            token.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def __call__(self, request: Request, call_next):
        """Validate CSRF for state-changing requests"""
        # Skip CSRF for safe methods
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)
        
        # Skip CSRF for JWT-authenticated requests (stateless)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return await call_next(request)
        
        # Validate CSRF for session-based requests
        csrf_cookie = request.cookies.get(self.cookie_name)
        csrf_header = request.headers.get(self.header_name)
        
        if not csrf_cookie or not csrf_header:
            logger.warning(
                "CSRF validation failed: Missing token",
                extra={"path": request.url.path}
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "CSRF token missing"}
            )
        
        # Validate tokens match
        if not hmac.compare_digest(csrf_cookie, csrf_header):
            logger.warning(
                "CSRF validation failed: Token mismatch",
                extra={"path": request.url.path}
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "CSRF token invalid"}
            )
        
        return await call_next(request)

# Note: We're using JWT (stateless), so CSRF is less critical
# But included for completeness if you add session cookies later
