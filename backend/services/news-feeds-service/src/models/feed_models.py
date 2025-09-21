"""📰 NEWS FEEDS MODELS - Personalized Career News"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum

class FeedCategory(str, Enum):
    CAREER_OPPORTUNITIES = "career_opportunities"
    SKILL_TRENDS = "skill_trends"
    INDUSTRY_NEWS = "industry_news" 
    SALARY_INSIGHTS = "salary_insights"
    JOB_MARKET = "job_market"

class NewsFeed(BaseModel):
    """Individual news feed item"""
    feed_id: str
    title: str
    summary: str
    source_name: str
    source_url: str
    category: FeedCategory
    topics: List[str]
    keywords: List[str]
    relevance_score: float = Field(ge=0, le=100)
    career_insights: List[str] = Field(default_factory=list)
    skill_mentions: List[str] = Field(default_factory=list)
    published_at: datetime

class UserFeedPreferences(BaseModel):
    """User's personalized feed preferences"""
    user_id: str
    preferred_topics: List[str] = Field(default_factory=list)
    experience_level: str = "student"
    industry_focus: List[str] = Field(default_factory=list)
    daily_feed_limit: int = 20
