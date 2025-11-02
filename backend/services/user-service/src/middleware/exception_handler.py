"""Global exception handler with detailed error responses"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from ..utils.structured_logger import logger, get_correlation_id
from typing import Union
import traceback

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    correlation_id = get_correlation_id()
    
    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "correlation_id": correlation_id
        }
    )

async def http_exception_handler(request: Request, exc: Union[StarletteHTTPException, Exception]):
    """Handle HTTP exceptions"""
    correlation_id = get_correlation_id()
    
    # Default to 500 for unknown errors
    status_code = getattr(exc, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
    detail = getattr(exc, 'detail', str(exc))
    
    # Log based on severity
    if status_code >= 500:
        logger.error(
            f"Server error: {detail}",
            extra={"path": request.url.path},
            exc_info=True
        )
    else:
        logger.warning(
            f"Client error: {detail}",
            extra={"path": request.url.path, "status_code": status_code}
        )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Internal Server Error" if status_code >= 500 else "Request Error",
            "detail": detail if status_code < 500 else "An unexpected error occurred",
            "correlation_id": correlation_id
        }
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions"""
    correlation_id = get_correlation_id()
    
    logger.critical(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please contact support.",
            "correlation_id": correlation_id
        }
    )
