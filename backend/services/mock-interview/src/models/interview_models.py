"""
🎙️ MOCK INTERVIEW MODELS - Voice-Enabled Interview System
Advanced interview simulation with AI feedback and voice processing
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class InterviewType(str, Enum):
    """Types of mock interviews"""
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SITUATIONAL = "situational"
    CASE_STUDY = "case_study"
    MIXED = "mixed"

class MockInterviewSession(BaseModel):
    """Complete mock interview session"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User taking the interview")
    
    # Session configuration
    interview_type: InterviewType = Field(..., description="Type of interview")
    difficulty_level: str = Field(..., description="Interview difficulty")
    target_role: Optional[str] = Field(None, description="Target job role")
    target_company: Optional[str] = Field(None, description="Target company")
    estimated_duration_minutes: int = Field(default=30, description="Planned duration")
    
    # Session results
    responses: List[str] = Field(default_factory=list, description="Response IDs")
    overall_performance: Optional[Dict[str, Any]] = Field(None, description="Overall assessment")
    
    # Scoring
    total_score: Optional[float] = Field(None, ge=0, le=100, description="Total interview score")
    skill_scores: Dict[str, float] = Field(default_factory=dict, description="Individual skill scores")
    improvement_areas: List[str] = Field(default_factory=list, description="Areas to improve")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")

class InterviewResponse(BaseModel):
    """User response to interview question"""
    response_id: str = Field(..., description="Unique response identifier")
    question_id: str = Field(..., description="Question being answered")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Interview session ID")
    
    # Response content
    text_response: Optional[str] = Field(None, description="Transcribed response text")
    audio_file_path: Optional[str] = Field(None, description="Path to audio recording")
    response_duration_seconds: int = Field(default=0, description="Response length")
    
    # AI Analysis Results
    ai_feedback: Optional[Dict[str, Any]] = Field(None, description="AI-generated feedback")
    confidence_score: Optional[float] = Field(None, ge=0, le=100, description="Confidence score")
    clarity_score: Optional[float] = Field(None, ge=0, le=100, description="Speech clarity")
    content_score: Optional[float] = Field(None, ge=0, le=100, description="Content quality")
    overall_score: Optional[float] = Field(None, ge=0, le=100, description="Overall score")
