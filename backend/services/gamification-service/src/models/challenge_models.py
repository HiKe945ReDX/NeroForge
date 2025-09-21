from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from bson import ObjectId
from enum import Enum
from pydantic_core import core_schema

# PYDANTIC V2 COMPATIBLE PyObjectId
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

# ENUMS
class ChallengeType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIAL_EVENT = "special_event"
    MILESTONE = "milestone"
    COMMUNITY = "community"

class ChallengeCategory(str, Enum):
    LEARNING = "learning"
    STREAK = "streak"
    ACTIVITY = "activity"
    SOCIAL = "social"
    SKILL_BUILDING = "skill_building"
    CAREER_DEVELOPMENT = "career_development"

class ChallengeDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ChallengeStatus(str, Enum):
    ACTIVE = "active"
    UPCOMING = "upcoming"
    COMPLETED = "completed"
    EXPIRED = "expired"
    PAUSED = "paused"

# CORE MODELS
class ChallengeRequirement(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
    
    type: str
    target_value: int
    measurement_unit: str
    specific_criteria: Optional[Dict[str, Any]] = {}

class ChallengeReward(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
    
    points: int = 0
    badge_id: Optional[str] = None
    special_item: Optional[str] = None
    title: Optional[str] = None
    additional_rewards: Optional[Dict[str, Any]] = {}

class Challenge(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    short_description: Optional[str] = None
    
    challenge_type: ChallengeType
    category: ChallengeCategory
    difficulty: ChallengeDifficulty
    
    requirements: List[ChallengeRequirement]
    completion_criteria: str
    
    rewards: ChallengeReward
    bonus_rewards: Optional[ChallengeReward] = None
    
    start_date: datetime
    end_date: datetime
    duration_days: int
    
    max_participants: Optional[int] = None
    current_participants: int = 0
    status: ChallengeStatus = ChallengeStatus.UPCOMING
    
    is_public: bool = True
    required_level: int = 1
    required_achievements: List[str] = []
    
    icon_url: Optional[str] = None
    banner_url: Optional[str] = None
    instructions: Optional[str] = None
    tips: List[str] = []
    
    total_completions: int = 0
    success_rate: float = 0.0
    average_completion_time: Optional[float] = None
    
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []

class UserChallenge(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    challenge_id: PyObjectId
    
    status: str = "active"
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    current_progress: Dict[str, Any] = {}
    progress_percentage: float = 0.0
    milestones_reached: List[str] = []
    
    start_value: Dict[str, Any] = {}
    best_performance: Dict[str, Any] = {}
    daily_progress: List[Dict[str, Any]] = []
    
    points_earned: int = 0
    rewards_claimed: bool = False
    bonus_earned: bool = False
    
    attempt_number: int = 1
    previous_attempts: List[datetime] = []
    
    shared_publicly: bool = False
    encouragement_received: int = 0

class ChallengeEvent(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_challenge_id: PyObjectId
    user_id: PyObjectId
    challenge_id: PyObjectId
    
    event_type: str
    event_data: Dict[str, Any] = {}
    progress_before: Dict[str, Any] = {}
    progress_after: Dict[str, Any] = {}
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "system"

class ChallengeStatistics(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    challenge_id: PyObjectId
    
    total_participants: int = 0
    active_participants: int = 0
    completed_participants: int = 0
    dropout_rate: float = 0.0
    
    average_completion_time_hours: Optional[float] = None
    fastest_completion_time_hours: Optional[float] = None
    slowest_completion_time_hours: Optional[float] = None
    
    progress_distribution: Dict[str, int] = {}
    common_drop_points: List[Dict[str, Any]] = []
    
    peak_activity_hours: List[int] = []
    completion_by_day: Dict[str, int] = {}
    
    last_calculated: datetime = Field(default_factory=datetime.utcnow)
    calculation_version: str = "1.0"

# REQUEST/RESPONSE MODELS
class CreateChallengeRequest(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
    
    title: str
    description: str
    short_description: Optional[str] = None
    
    challenge_type: ChallengeType
    category: ChallengeCategory
    difficulty: ChallengeDifficulty
    
    requirements: List[ChallengeRequirement]
    completion_criteria: str
    
    rewards: ChallengeReward
    bonus_rewards: Optional[ChallengeReward] = None
    
    start_date: datetime
    end_date: datetime
    
    max_participants: Optional[int] = None
    is_public: bool = True
    required_level: int = 1
    required_achievements: List[str] = []
    
    icon_url: Optional[str] = None
    banner_url: Optional[str] = None
    instructions: Optional[str] = None
    tips: List[str] = []
    tags: List[str] = []

class JoinChallengeRequest(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
    
    user_id: str
    challenge_id: str
    motivation_message: Optional[str] = None

class UpdateProgressRequest(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
    
    user_id: str
    challenge_id: str
    activity_data: Dict[str, Any]
    timestamp: Optional[datetime] = None

class ChallengeResponse(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
    
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ChallengeListResponse(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
    
    success: bool
    challenges: List[Dict[str, Any]]
    total_count: int
    pagination: Optional[Dict[str, Any]] = None
    filters_applied: Optional[Dict[str, Any]] = None

class UserChallengeResponse(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
    
    success: bool
    user_id: str
    active_challenges: List[Dict[str, Any]] = []
    completed_challenges: List[Dict[str, Any]] = []
    failed_challenges: List[Dict[str, Any]] = []
    total_points_earned: int = 0
