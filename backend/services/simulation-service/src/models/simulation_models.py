from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class SimulationType(str, Enum):
    CAREER_PATH = "career_path"
    FINANCIAL_PROJECTION = "financial_projection"
    RISK_ASSESSMENT = "risk_assessment"

class SimulationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class CareerRole(BaseModel):
    title: str
    industry: str
    level: str = Field(default="mid")
    salary: float
    growth_rate: float = Field(default=0.05)

class SimulationRequest(BaseModel):
    user_id: Optional[str] = None
    simulation_type: SimulationType
    name: str
    current_role: CareerRole
    target_role: CareerRole
    timeline_years: int = Field(default=5)
    parameters: Dict[str, Any] = Field(default={})

class SimulationResult(BaseModel):
    year: int
    role: str
    salary: float
    savings: float
    net_worth: float

class SimulationOutput(BaseModel):
    simulation_id: str
    user_id: Optional[str]
    status: SimulationStatus
    name: str
    results: List[SimulationResult]
    summary: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class CreateSimulationResponse(BaseModel):
    simulation_id: str
    status: SimulationStatus
    message: str
