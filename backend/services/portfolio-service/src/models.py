from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class PortfolioStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class PortfolioType(str, Enum):
    WEB_DEVELOPER = "web_developer"
    DATA_SCIENTIST = "data_scientist"
    AI_ENGINEER = "ai_engineer"
    FULLSTACK = "fullstack"
    GENERAL = "general"

class ProjectHighlight(BaseModel):
    title: str
    description: str
    tech_stack: List[str] = Field(default=[])
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    image_url: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    name: str
    title: str
    bio: str
    email: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: List[str] = Field(default=[])

class Portfolio(BaseModel):
    id: Optional[str] = None
    user_id: str
    name: str
    portfolio_type: PortfolioType
    status: PortfolioStatus = PortfolioStatus.DRAFT
    profile: UserProfile
    projects: List[ProjectHighlight] = Field(default=[])
    template_id: str = Field(default="modern")
    theme_colors: Dict[str, str] = Field(default={
        "primary": "#3b82f6",
        "secondary": "#1f2937",
        "accent": "#06b6d4"
    })
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_urls: Dict[str, str] = Field(default={})

class PortfolioRequest(BaseModel):
    user_id: str
    name: str
    portfolio_type: PortfolioType = PortfolioType.GENERAL
    profile: UserProfile
    template_id: str = Field(default="modern")
    max_projects: int = Field(default=6)

class PortfolioResponse(BaseModel):
    portfolio_id: str
    status: PortfolioStatus
    message: str
    preview_url: Optional[str] = None
    download_urls: Dict[str, str] = Field(default={})

class ServiceIntegrationData(BaseModel):
    github_data: Optional[Dict[str, Any]] = None
    career_insights: Optional[Dict[str, Any]] = None
    achievements: Optional[Dict[str, Any]] = None
    simulations: Optional[Dict[str, Any]] = None
