"""Enhanced Pydantic models with strict validation"""
from pydantic import BaseModel, EmailStr, Field, validator
import re
from typing import Optional

class StrictEmailMixin(BaseModel):
    """Email validation mixin"""
    email: EmailStr = Field(..., description="Valid email address")
    
    @validator('email')
    def normalize_email(cls, v):
        return v.lower().strip()

class StrictPasswordMixin(BaseModel):
    """Password validation mixin"""
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="Password (8-128 chars, must include uppercase, lowercase, number, special char)"
    )
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v

class StrictUsernameMixin(BaseModel):
    """Username validation mixin"""
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    
    @validator('username')
    def validate_username(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v

class StrictNameMixin(BaseModel):
    """Name validation mixin"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    
    @validator('full_name')
    def validate_name(cls, v):
        if v:
            v = v.strip()
            if not re.match(r'^[a-zA-Z\s\'-]+$', v):
                raise ValueError('Name can only contain letters, spaces, hyphens, and apostrophes')
        return v

# Updated SignupRequest with strict validation
class SignupRequest(StrictEmailMixin, StrictPasswordMixin, StrictNameMixin):
    """Strict signup request validation"""
    pass

# Updated LoginRequest
class LoginRequest(StrictEmailMixin):
    """Strict login request validation"""
    password: str = Field(..., min_length=1, max_length=128)
