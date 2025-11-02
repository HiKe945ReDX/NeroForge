from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any, Annotated
from datetime import datetime
from bson import ObjectId
from enum import Enum
from pydantic_core import core_schema

# FIXED: Pydantic v2 compatible PyObjectId
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x), when_used='json'
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

class ActivityType(str, Enum):
    COURSE_COMPLETION = "course_completion"
    SKILL_ASSESSMENT = "skill_assessment"
    PROFILE_COMPLETION = "profile_completion"
    DAILY_LOGIN = "daily_login"
    CAREER_PATH_PROGRESS = "career_path_progress"
    RESUME_UPDATE = "resume_update"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"

class AchievementCategory(str, Enum):
    LEARNING = "learning"
    CAREER = "career"
    MILESTONE = "milestone"
    SPECIAL = "special"
    SOCIAL = "social"

# User Gamification Profile
class SkillPoints(BaseModel):
    technical: int = 0
    soft_skills: int = 0
    leadership: int = 0
    communication: int = 0

class ProgressTracking(BaseModel):
    career_path_completion: float = 0.0
    goals_completed: int = 0
    courses_completed: int = 0
    assessments_taken: int = 0
    profile_completeness: float = 0.0

class UserGamification(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    username: str

    # Points & Level System
    total_xp: int = 0
    current_level: int = 1
    xp_to_next_level: int = 1000
    skill_points: SkillPoints = Field(default_factory=SkillPoints)

    # Streak System
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[datetime] = None

    # Achievements
    achievements_unlocked: List[PyObjectId] = []
    total_achievements: int = 0

    # Progress Tracking
    progress_tracking: ProgressTracking = Field(default_factory=ProgressTracking)

    # Activity History
    total_activities: int = 0
    weekly_activities: int = 0
    monthly_activities: int = 0

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Achievement System
class UnlockCriteria(BaseModel):
    type: str  # activity_count, streak, completion, level, points
    threshold: int
    specific_action: Optional[str] = None
    time_frame: Optional[str] = None  # daily, weekly, monthly, all_time

class Achievement(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    category: AchievementCategory
    points_reward: int
    icon_url: Optional[str] = None
    rarity: str = "common"  # common, rare, epic, legendary

    # Unlock Requirements
    unlock_criteria: UnlockCriteria

    # Stats
    unlock_count: int = 0
    unlock_percentage: float = 0.0

    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

# User Achievement Record
class UserAchievement(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    achievement_id: PyObjectId
    unlocked_at: datetime = Field(default_factory=datetime.utcnow)
    points_earned: int

# Leaderboard Models
class LeaderboardType(str, Enum):
    GLOBAL = "global"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SKILL_SPECIFIC = "skill_specific"

class LeaderboardEntry(BaseModel):
    user_id: PyObjectId
    username: str
    score: int
    rank: int
    avatar_url: Optional[str] = None
    level: int = 1
    achievements_count: int = 0

class Leaderboard(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    type: LeaderboardType
    category: Optional[str] = None  # For skill-specific boards
    period: str  # all-time, weekly, monthly
    entries: List[LeaderboardEntry] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# Activity Tracking
class ActivityRecord(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    activity_type: ActivityType
    points_earned: int
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# API Response Models
class UserGamificationResponse(BaseModel):
    user_id: str
    username: str
    total_xp: int
    current_level: int
    xp_to_next_level: int
    current_streak: int
    achievements_count: int
    rank_position: Optional[int] = None

class PointsAwardRequest(BaseModel):
    user_id: str
    activity_type: ActivityType
    points: Optional[int] = None
    metadata: Dict[str, Any] = {}

class PointsAwardResponse(BaseModel):
    success: bool
    points_awarded: int
    new_total_xp: int
    level_up: bool = False
    new_level: Optional[int] = None
    achievements_unlocked: List[str] = []
