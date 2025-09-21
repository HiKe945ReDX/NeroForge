from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    PREMIUM = "premium"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    agreed_to_terms: bool = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserProfile(BaseModel):
    # Career Information
    current_role: Optional[str] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None  # beginner, intermediate, advanced, expert
    years_of_experience: Optional[int] = None
    skills: List[str] = []
    interests: List[str] = []
    
    # Education
    education: List[Dict[str, Any]] = []
    certifications: List[Dict[str, Any]] = []
    
    # Social Links
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    
    # Career Goals
    career_goals: List[str] = []
    learning_preferences: Dict[str, Any] = {}
    
    # Privacy Settings
    profile_visibility: str = "public"  # public, private, friends
    show_email: bool = False
    show_phone: bool = False

class UserPublic(BaseModel):
    """Public user information (safe to expose)"""
    id: str
    email: EmailStr
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    role: str = "user"
    status: str = "active"
    is_verified: bool = False
    created_at: datetime
    last_login: Optional[datetime]
    
    # Public profile info
    current_role: Optional[str] = None
    skills: List[str] = []
    github_username: Optional[str] = None
    portfolio_url: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    user: UserPublic

class OAuthUserData(BaseModel):
    provider: str  # google, github
    provider_id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider_data: Dict[str, Any] = Field(default_factory=dict)
