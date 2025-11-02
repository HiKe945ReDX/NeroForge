"""Standard error response models"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ErrorDetail(BaseModel):
    """Single error detail"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: str | List[ErrorDetail]
    correlation_id: str
    timestamp: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "Validation Error"
    detail: List[Dict[str, Any]]
    correlation_id: str
