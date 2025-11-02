from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Identity(BaseModel):
    name: str
    age: Optional[int] = None
    education: Optional[str] = None
    roleType: Optional[str] = None
    goals: Optional[List[str]] = None

class SkillsSelection(BaseModel):
    skills: List[str] = Field(default_factory=list)
    maxAllowed: int = 10

class Psychometric(BaseModel):
    traits: Dict[str, float] = {}
    summary: Optional[str] = None

class ContextView(BaseModel):
    userId: str
    identity: Optional[Identity] = None
    skills: Optional[SkillsSelection] = None
    psychometric: Optional[Psychometric] = None
    resumeSignals: Optional[Dict[str, Any]] = None
    githubSignals: Optional[Dict[str, Any]] = None
    linkedinSignals: Optional[Dict[str, Any]] = None
    portfolioScore: Optional[float] = None
    updatedAt: Optional[datetime] = None
