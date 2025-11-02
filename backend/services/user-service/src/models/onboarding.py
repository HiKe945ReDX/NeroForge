"""Onboarding data models"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from enum import Enum

class OnboardingStepEnum(str, Enum):
    IDENTITY = "identity"
    SKILLS = "skills"
    PSYCHOMETRIC = "psychometric"
    REVIEW = "review"

# ADD THIS ALIAS - This is what was missing!
OnboardingStep = OnboardingStepEnum

class IdentityData(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    role: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    current_company: Optional[str] = None
    education_level: Optional[str] = None

class SkillsData(BaseModel):
    selected_skills: List[str] = Field(..., min_items=1, max_items=15)
    proficiency_levels: Dict[str, int] = {}  # skill -> 1-5 rating
    
    @validator('selected_skills')
    def validate_skill_limit(cls, v):
        if len(v) > 15:
            raise ValueError('Maximum 15 skills allowed')
        return v

class PsychometricData(BaseModel):
    answers: Dict[str, int] = {}  # question_id -> answer
    big_five_scores: Optional[Dict[str, float]] = None

class OnboardingState(BaseModel):
    current_step: OnboardingStepEnum
    data: Dict = {}
    completed_steps: List[OnboardingStepEnum] = []
    
    identity: Optional[IdentityData] = None
    skills: Optional[SkillsData] = None
    psychometric: Optional[PsychometricData] = None
