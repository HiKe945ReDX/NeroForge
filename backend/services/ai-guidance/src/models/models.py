from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
from enum import Enum
import uuid

# Enums for type safety
class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    EXPERT = "expert"

class PersonaStep(str, Enum):
    BASIC_INFO = "basic_info"
    CAREER_GOALS = "career_goals"
    INTERESTS = "interests"
    PREFERENCES = "preferences"
    EXPERIENCE = "experience"

class RoadmapStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class PsychometricTrait(str, Enum):
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"

class LinkedInSectionType(str, Enum):
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    CERTIFICATIONS = "certifications"
    PROJECTS = "projects"

# Base Models
class TimestampedModel(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserBaseModel(TimestampedModel):
    user_id: str = Field(..., description="User ID", min_length=1)
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError('user_id cannot be empty')
        return v.strip()

# Existing Models
class PersonaStepData(UserBaseModel):
    step: PersonaStep = Field(..., description="Persona wizard step identifier")
    data: Dict[str, Any] = Field(..., description="Step data")
    is_completed: bool = Field(default=False)
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)

class PsychometricAnswers(UserBaseModel):
    answers: Dict[PsychometricTrait, List[int]] = Field(..., description="Psychometric answers by traits")
    total_score: Optional[float] = Field(None)
    trait_scores: Optional[Dict[PsychometricTrait, float]] = Field(None)

class ResumeParseResponse(UserBaseModel):
    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="File type")
    extracted_text: str = Field(..., description="Extracted resume text")
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    skills: List[str] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)

class AIInsightResponse(UserBaseModel):
    insight_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ats_score: float = Field(..., ge=0.0, le=100.0)
    resume_strength_score: float = Field(..., ge=0.0, le=10.0)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

# NEW REQUEST MODELS - FIXED VALIDATORS
class RoadmapGenerationRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    target_role: str = Field(..., description="Target career role")
    current_role: Optional[str] = Field(None, description="Current role")
    include_resume_data: bool = Field(default=True)
    include_github_data: bool = Field(default=True)
    include_linkedin_data: bool = Field(default=True)
    include_psychometric_data: bool = Field(default=True)
    include_persona_data: bool = Field(default=True)
    target_duration_weeks: Optional[int] = Field(None, ge=1, le=104)
    weekly_learning_hours: Optional[int] = Field(None, ge=1, le=40)

class LinkedInScrapingRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    profile_url: str = Field(..., description="LinkedIn profile URL")
    sections_to_scrape: List[LinkedInSectionType] = Field(default_factory=lambda: list(LinkedInSectionType))
    use_proxy: bool = Field(default=True)
    
    @field_validator('profile_url')  # FIXED: was @validator
    @classmethod
    def validate_linkedin_url(cls, v):
        if not v.startswith(('https://linkedin.com', 'https://www.linkedin.com')):
            raise ValueError('Must be a valid LinkedIn profile URL')
        return v

class GitHubAnalysisRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    repository_urls: List[str] = Field(..., min_length=1, max_length=10)
    analyze_code_quality: bool = Field(default=True)
    analyze_activity: bool = Field(default=True)
    
    @field_validator('repository_urls')  # FIXED: was @validator
    @classmethod
    def validate_github_urls(cls, v):
        for url in v:
            if not url.startswith(('https://github.com', 'https://www.github.com')):
                raise ValueError(f'Invalid GitHub URL: {url}')
        return v

# NEW COMPLEX MODELS
class RoadmapSkill(BaseModel):
    skill_name: str = Field(..., description="Name of the skill")
    current_level: SkillLevel = Field(default=SkillLevel.BEGINNER)
    target_level: SkillLevel = Field(..., description="Target proficiency level")
    priority: int = Field(..., ge=1, le=10)
    estimated_hours: int = Field(..., ge=1)
    resources: List[Dict[str, str]] = Field(default_factory=list)
    milestones: List[str] = Field(default_factory=list)

class RoadmapPhase(BaseModel):
    phase_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Phase title")
    description: str = Field(..., description="Phase description")
    duration_weeks: int = Field(..., ge=1)
    skills: List[RoadmapSkill] = Field(..., description="Skills to develop")
    order: int = Field(..., ge=1)

class Roadmap(UserBaseModel):
    roadmap_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Roadmap title")
    description: str = Field(..., description="Roadmap description")
    target_role: str = Field(..., description="Target career role")
    current_role: Optional[str] = Field(None)
    phases: List[RoadmapPhase] = Field(..., description="Roadmap phases")
    total_duration_weeks: int = Field(..., ge=1)
    difficulty_level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE)
    status: RoadmapStatus = Field(default=RoadmapStatus.DRAFT)
    generated_by: str = Field(default="gemini")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    based_on_resume: bool = Field(default=False)
    based_on_github: bool = Field(default=False)
    based_on_linkedin: bool = Field(default=False)
    based_on_psychometrics: bool = Field(default=False)
    based_on_persona: bool = Field(default=False)

class RoadmapProgress(UserBaseModel):
    roadmap_id: str = Field(..., description="Associated roadmap ID")
    progress_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    overall_completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    current_phase: int = Field(default=1, ge=1)
    phase_progress: Dict[str, float] = Field(default_factory=dict)
    skill_progress: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    total_hours_spent: float = Field(default=0.0, ge=0.0)

class Repository(UserBaseModel):
    repo_id: str = Field(..., description="GitHub repository ID")
    repo_name: str = Field(..., description="Repository name")
    repo_url: str = Field(..., description="Repository URL")
    owner: str = Field(..., description="Repository owner")
    description: Optional[str] = Field(None)
    primary_language: str = Field(..., description="Primary programming language")
    languages: Dict[str, float] = Field(default_factory=dict)
    total_commits: int = Field(default=0, ge=0)
    contributors: int = Field(default=0, ge=0)
    stars: int = Field(default=0, ge=0)
    forks: int = Field(default=0, ge=0)
    technologies: List[str] = Field(default_factory=list)

class LinkedInProfile(UserBaseModel):
    profile_url: str = Field(..., description="LinkedIn profile URL")
    scraping_session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    full_name: Optional[str] = Field(None)
    headline: Optional[str] = Field(None)
    location: Optional[str] = Field(None)
    summary: Optional[str] = Field(None)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    skills: List[Dict[str, Union[str, int]]] = Field(default_factory=list)
    scraping_success: bool = Field(default=True)
    sections_scraped: List[LinkedInSectionType] = Field(default_factory=list)
