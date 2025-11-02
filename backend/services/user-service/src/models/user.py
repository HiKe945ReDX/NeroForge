"""
Enhanced User model with email verification and account status
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user fields"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation with password"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """User update fields"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    """User as stored in database"""
    id: str = Field(alias="_id")
    hashed_password: str
    email_verified: bool = False
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class UserResponse(UserBase):
    """User response (public fields only)"""
    id: str
    email_verified: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    expires_in: int = 900  # 15 minutes


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset with token"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class EmailVerification(BaseModel):
    """Email verification"""
    token: str
