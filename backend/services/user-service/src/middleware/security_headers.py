"""Security headers middleware using secure library"""
from secure import Secure
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

secure_headers = Secure(
    server=Secure.Server(value=""),  # Hide server info
    csp=Secure.ContentSecurityPolicy(
        default=("'self'",),
        script=("'self'",),
        style=("'self'", "'unsafe-inline'"),
        img=("'self'", "data:", "https:"),
        connect=("'self'", "https://guidora-users-*.run.app"),
    ),
    hsts=Secure.StrictTransportSecurity(
        max_age=31536000,  # 1 year
        include_subdomains=True,
        preload=True
    ),
    referrer=Secure.ReferrerPolicy(policy="strict-origin-when-cross-origin"),
    permissions=Secure.PermissionsPolicy(
        geolocation=(),
        microphone=(),
        camera=()
    ),
    cache=Secure.CacheControl(no_store=True),
    xfo=Secure.XFrameOptions(option="DENY"),
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Apply security headers
        secure_headers.framework.fastapi(response)
        
        # Additional custom headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        
        return response

security_headers_middleware = SecurityHeadersMiddleware
