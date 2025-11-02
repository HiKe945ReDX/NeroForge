from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class ExperienceLevel(str, Enum):
    """Experience levels for careers"""
    ENTRY = "entry"
    MID = "mid" 
    SENIOR = "senior"
    EXECUTIVE = "executive"

class RemoteLevel(str, Enum):
    """Remote work availability levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"

class CareerDomain(BaseModel):
    """Career domain model representing high-level career categories"""
    domain_id: str = Field(..., description="Unique identifier for the domain")
    name: str = Field(..., description="Display name of the domain")
    description: str = Field(..., description="Detailed description of the domain")
    icon: str = Field("📊", description="Emoji icon for the domain")
    subcategories: List[Dict[str, Any]] = Field(default_factory=list, description="Subcategories within domain")
    career_count: int = Field(0, ge=0, description="Total number of careers in domain")
    avg_salary: str = Field("$0", description="Average salary range for domain")
    growth_rate: str = Field("0%", description="Projected growth rate")
    top_skills: List[str] = Field(default_factory=list, description="Most important skills for domain")
    industry_overview: str = Field("", description="Overview of the industry")
    future_outlook: str = Field("", description="Future outlook and trends")
    
    class Config:
        use_enum_values = True

class Career(BaseModel):
    """Comprehensive career model with all career information"""
    # Basic Information
    career_id: str = Field(..., description="Unique career identifier")
    title: str = Field(..., description="Career title")
    category: str = Field(..., description="Primary career category/domain")
    subcategory: Optional[str] = Field(None, description="Career subcategory")
    
    # Core Description
    description: str = Field(..., description="Brief career description")
    overview: str = Field("", description="Detailed career overview")
    
    # Daily Work and Responsibilities
    day_in_life: List[str] = Field(default_factory=list, description="Typical daily activities")
    responsibilities: List[str] = Field(default_factory=list, description="Key job responsibilities")
    
    # Skills and Requirements
    required_skills: List[str] = Field(default_factory=list, description="Essential technical and soft skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Additional beneficial skills")
    
    # Education and Experience
    education_requirements: Dict[str, Any] = Field(default_factory=dict, description="Education requirements and alternatives")
    experience_levels: Dict[str, Any] = Field(default_factory=dict, description="Experience level breakdown")
    
    # Career Progression
    growth_path: List[Dict[str, Any]] = Field(default_factory=list, description="Career progression pathway")
    related_careers: List[str] = Field(default_factory=list, description="Related career paths")
    
    # Work Environment
    work_environment: Dict[str, Any] = Field(default_factory=dict, description="Work environment details")
    
    # Compensation and Benefits
    salary_data: Dict[str, Any] = Field(default_factory=dict, description="Comprehensive salary information")
    
    # Market and Demand
    job_outlook: Dict[str, Any] = Field(default_factory=dict, description="Job market outlook and growth")
    industry_trends: List[str] = Field(default_factory=list, description="Current industry trends")
    key_employers: List[str] = Field(default_factory=list, description="Top employers in the field")
    
    # Work Characteristics
    remote_opportunities: RemoteLevel = Field(RemoteLevel.MEDIUM, description="Remote work availability")
    travel_requirements: str = Field("Low", description="Travel requirement level")
    stress_level: str = Field("Medium", description="Typical stress level")
    work_life_balance: str = Field("5.0/10", description="Work-life balance rating")
    
    # Performance Metrics
    job_satisfaction_score: float = Field(3.5, ge=1.0, le=5.0, description="Job satisfaction rating (1-5)")
    demand_score: float = Field(0.5, ge=0.0, le=1.0, description="Market demand score (0-1)")
    competition_level: str = Field("Medium", description="Competition level for positions")
    
    # Transferability
    skills_transferability: List[str] = Field(default_factory=list, description="Careers with transferable skills")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        use_enum_values = True

class CareerSearchFilters(BaseModel):
    """Search filters for career exploration"""
    keywords: Optional[str] = Field(None, description="Search keywords")
    categories: Optional[List[str]] = Field(None, description="Career categories to filter by")
    salary_min: Optional[int] = Field(None, ge=0, description="Minimum salary filter")
    salary_max: Optional[int] = Field(None, ge=0, description="Maximum salary filter")
    experience_level: Optional[str] = Field(None, description="Required experience level")
    remote_friendly: Optional[bool] = Field(None, description="Remote work availability filter")
    education_level: Optional[str] = Field(None, description="Education requirement level")
    location: Optional[str] = Field(None, description="Geographic location preference")
    skills: Optional[List[str]] = Field(None, description="Required or preferred skills")

class CareerComparison(BaseModel):
    """Model for comparing multiple careers"""
    career_ids: List[str] = Field(..., min_items=2, max_items=5, description="Career IDs to compare")
    comparison_criteria: List[str] = Field(
        default=["salary", "growth", "work_life_balance", "job_satisfaction", "demand"],
        description="Criteria to compare careers on"
    )
    weights: Optional[Dict[str, float]] = Field(None, description="Weights for each criterion")
