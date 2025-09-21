"""
User Activity Models for Guidora Platform
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ActivityType(str, Enum):
    """Activity types for user tracking"""
    RESUME_UPLOAD = "resume_upload"
    SKILL_ASSESSMENT = "skill_assessment" 
    INTERVIEW_PRACTICE = "interview_practice"
    PORTFOLIO_UPDATE = "portfolio_update"
    COURSE_COMPLETION = "course_completion"
    CAREER_PATH_VIEW = "career_path_view"
    JOB_APPLICATION = "job_application"
    PROFILE_UPDATE = "profile_update"
    LOGIN = "login"
    LOGOUT = "logout"

class UserActivity(BaseModel):
    """User Activity tracking model"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str = Field(..., description="User ID who performed the activity")
    activity_type: ActivityType = Field(..., description="Type of activity performed")
    activity_data: Dict[str, Any] = Field(default_factory=dict, description="Additional activity data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the activity occurred")
    ip_address: Optional[str] = Field(None, description="User's IP address")
    user_agent: Optional[str] = Field(None, description="User's browser/device info")
    session_id: Optional[str] = Field(None, description="User's session ID")
    duration: Optional[int] = Field(None, description="Activity duration in seconds")
    success: bool = Field(True, description="Whether the activity was successful")
    error_message: Optional[str] = Field(None, description="Error message if activity failed")
    
    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ActivityResponse(BaseModel):
    """Response model for activity data"""
    id: str
    user_id: str
    activity_type: ActivityType
    activity_data: Dict[str, Any]
    timestamp: datetime
    success: bool
    duration: Optional[int] = None
    
class ActivityStats(BaseModel):
    """User activity statistics"""
    total_activities: int = 0
    activities_by_type: Dict[ActivityType, int] = Field(default_factory=dict)
    most_recent_activity: Optional[datetime] = None
    most_active_day: Optional[str] = None
    average_session_duration: Optional[float] = None

class ActivityFilter(BaseModel):
    """Filter model for querying activities"""
    user_id: Optional[str] = None
    activity_types: Optional[List[ActivityType]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    success_only: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=1000)
    skip: int = Field(default=0, ge=0)

# Additional activity models
class LoginActivity(BaseModel):
    """Login activity specific data"""
    login_method: str  # "email", "google", "github"
    device_type: str   # "web", "mobile", "desktop"
    location: Optional[str] = None

class ResumeActivity(BaseModel):
    """Resume-related activity data"""
    resume_id: str
    action: str  # "upload", "update", "download", "analyze"
    file_size: Optional[int] = None
    file_type: Optional[str] = None

class InterviewActivity(BaseModel):
    """Interview practice activity data"""
    interview_id: str
    interview_type: str  # "technical", "behavioral", "mock"
    duration_minutes: int
    questions_answered: int
    score: Optional[float] = None

class PortfolioActivity(BaseModel):
    """Portfolio-related activity data"""
    portfolio_id: str
    action: str  # "create", "update", "publish", "view"
    sections_updated: Optional[List[str]] = None

class UserBehaviorPattern(BaseModel):
    """User behavior pattern analysis model"""
    user_id: str = Field(..., description="User ID")
    pattern_type: str = Field(..., description="Type of behavior pattern")
    pattern_data: Dict[str, Any] = Field(default_factory=dict, description="Pattern analysis data")
    frequency: int = Field(default=0, description="Pattern frequency")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Pattern confidence")
    first_observed: datetime = Field(default_factory=datetime.utcnow, description="First pattern observation")
    last_observed: datetime = Field(default_factory=datetime.utcnow, description="Last pattern observation")
    
class UserEngagementMetrics(BaseModel):
    """User engagement metrics for analytics"""
    user_id: str = Field(..., description="User ID")
    daily_active_time: int = Field(default=0, description="Daily active time in minutes")
    weekly_sessions: int = Field(default=0, description="Weekly session count")
    feature_usage: Dict[str, int] = Field(default_factory=dict, description="Feature usage counts")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    engagement_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall engagement score")

class UserGoalProgress(BaseModel):
    """User goal progress tracking"""
    user_id: str = Field(..., description="User ID")
    goal_id: str = Field(..., description="Goal identifier")
    goal_type: str = Field(..., description="Type of goal")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage")
    milestones_completed: List[str] = Field(default_factory=list, description="Completed milestones")
    target_date: Optional[datetime] = Field(None, description="Target completion date")
    status: str = Field(default="active", description="Goal status")

class UserSkillAssessment(BaseModel):
    """User skill assessment results"""
    user_id: str = Field(..., description="User ID")
    skill_name: str = Field(..., description="Skill name")
    skill_category: str = Field(..., description="Skill category")
    current_level: str = Field(..., description="Current skill level")
    assessment_score: float = Field(..., ge=0.0, le=100.0, description="Assessment score")
    assessment_date: datetime = Field(default_factory=datetime.utcnow, description="Assessment date")
    recommended_resources: List[str] = Field(default_factory=list, description="Recommended learning resources")

class PersonalizedInsight(BaseModel):
    """Personalized insight for user analytics"""
    user_id: str = Field(..., description="User ID")
    insight_type: str = Field(..., description="Type of insight")
    insight_title: str = Field(..., description="Insight title")
    insight_description: str = Field(..., description="Insight description")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Insight relevance score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When insight was created")
    data_points: Dict[str, Any] = Field(default_factory=dict, description="Supporting data points")
    
class LearningPathRecommendation(BaseModel):
    """Learning path recommendation for users"""
    user_id: str = Field(..., description="User ID")
    path_id: str = Field(..., description="Learning path identifier")
    path_title: str = Field(..., description="Learning path title")
    recommended_skills: List[str] = Field(default_factory=list, description="Recommended skills")
    difficulty_level: str = Field(..., description="Difficulty level")
    estimated_duration: int = Field(default=0, description="Estimated duration in hours")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Recommendation confidence")

class CareerProgressMetric(BaseModel):
    """Career progression tracking"""
    user_id: str = Field(..., description="User ID")
    metric_name: str = Field(..., description="Metric name")
    current_value: float = Field(..., description="Current metric value")
    target_value: float = Field(..., description="Target metric value")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage")
    measurement_date: datetime = Field(default_factory=datetime.utcnow, description="Measurement date")
    
class SkillGapAnalysis(BaseModel):
    """Skill gap analysis results"""
    user_id: str = Field(..., description="User ID")
    target_role: str = Field(..., description="Target career role")
    required_skills: List[str] = Field(default_factory=list, description="Required skills for role")
    current_skills: List[str] = Field(default_factory=list, description="Current user skills")
    skill_gaps: List[str] = Field(default_factory=list, description="Identified skill gaps")
    gap_severity: Dict[str, str] = Field(default_factory=dict, description="Gap severity levels")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis date")

class ActivitySummary(BaseModel):
    """Activity summary for analytics dashboard"""
    user_id: str = Field(..., description="User ID")
    date: datetime = Field(default_factory=datetime.utcnow, description="Summary date")
    total_activities: int = Field(default=0, description="Total activity count")
    active_time_minutes: int = Field(default=0, description="Active time in minutes")
    most_used_feature: Optional[str] = Field(None, description="Most used feature")
    productivity_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Daily productivity score")
    achievement_count: int = Field(default=0, description="Achievements earned today")
    skill_progress: Dict[str, float] = Field(default_factory=dict, description="Skill progress")

class UserJourney(BaseModel):
    """User journey tracking"""
    user_id: str = Field(..., description="User ID")
    journey_stage: str = Field(..., description="Current journey stage")
    onboarding_progress: int = Field(default=0, ge=0, le=100, description="Onboarding progress")
    key_milestones: List[str] = Field(default_factory=list, description="Completed milestones")
    next_recommended_action: Optional[str] = Field(None, description="Next recommended action")
    journey_start_date: datetime = Field(default_factory=datetime.utcnow, description="Journey start date")

class PlatformUsageMetrics(BaseModel):
    """Platform usage metrics"""
    user_id: str = Field(..., description="User ID")
    session_duration: int = Field(default=0, description="Session duration in minutes")
    pages_visited: List[str] = Field(default_factory=list, description="Pages visited in session")
    features_used: List[str] = Field(default_factory=list, description="Features used")
    errors_encountered: List[str] = Field(default_factory=list, description="Errors encountered")
    device_type: Optional[str] = Field(None, description="Device type used")
    browser_info: Optional[str] = Field(None, description="Browser information")
