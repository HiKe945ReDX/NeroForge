from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class OnboardingStep(str, Enum):
    """Onboarding step enumeration"""
    BASIC_INFO = "basic_info"
    EXPERIENCE_UPLOAD = "experience_upload"
    PSYCHOMETRIC_TEST = "psychometric_test"
    EMPATHY_MAPPING = "empathy_mapping"
    SKILLS_SELECTION = "skills_selection"
    CAREER_EXPLORATION = "career_exploration"
    COMPLETED = "completed"

class OnboardingState(BaseModel):
    """User onboarding state tracking"""
    user_id: str = Field(..., description="User ID")
    current_step: OnboardingStep = Field(default=OnboardingStep.BASIC_INFO)
    completed_steps: List[OnboardingStep] = Field(default_factory=list)
    step_data: Dict = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    is_completed: bool = False

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
