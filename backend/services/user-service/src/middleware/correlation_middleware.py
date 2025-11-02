"""Middleware to track requests with correlation IDs"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
from ..utils.structured_logger import set_correlation_id, get_correlation_id, logger
import time

class CorrelationMiddleware(BaseHTTPMiddleware):
    """Add correlation ID to all requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Extract or generate correlation ID
        correlation_id = request.headers.get('X-Correlation-ID') or str(uuid.uuid4())
        set_correlation_id(correlation_id)
        
        # Log request
        start_time = time.time()
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2)
                }
            )
            
            # Add correlation ID to response headers
            response.headers['X-Correlation-ID'] = correlation_id
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2)
                },
                exc_info=True
            )
            raise

correlation_middleware = CorrelationMiddleware
