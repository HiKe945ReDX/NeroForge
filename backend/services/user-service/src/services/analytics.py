"""
🧠 ANALYTICS & PERSONALIZATION ENGINE - Instagram-Style Intelligence
Advanced behavioral analysis and personalized recommendations
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
from dataclasses import dataclass

from ..models.activity import (
    UserActivity, UserBehaviorPattern, PersonalizedInsight,
    ActivitySummary, ActivityType
)
from ..core.config import settings
from ..core.database import get_database

@dataclass
class EngagementMetrics:
    """Engagement metrics calculation"""
    total_time: int
    session_count: int
    avg_session_length: float
    feature_diversity: int
    return_frequency: float
    engagement_score: float

class PersonalizationEngine:
    """
    🎯 Instagram-Style Personalization Engine
    AI-powered user behavior analysis and recommendations
    """
    
    def __init__(self, db):
        self.db = db
        
    async def analyze_user_behavior(self, user_id: str, days_back: int = 30) -> UserBehaviorPattern:
        """
        🔍 Comprehensive behavior analysis like Instagram's algorithm
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Get user activities
        activities = await self.db.user_activities.find({
            "user_id": user_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        
        if not activities:
            return self._create_default_pattern(user_id)
        
        # Analyze patterns
        patterns = self._analyze_activity_patterns(activities)
        engagement = self._calculate_engagement_metrics(activities)
        career_focus = await self._analyze_career_focus(user_id, activities)
        predictions = self._generate_predictions(engagement, patterns)
        
        behavior_pattern = UserBehaviorPattern(
            user_id=user_id,
            pattern_type="comprehensive_analysis",
            frequency=self._determine_frequency(activities),
            peak_usage_hours=patterns["peak_hours"],
            preferred_features=patterns["preferred_features"],
            career_interests=career_focus["interests"],
            skill_focus_areas=career_focus["skills"],
            learning_style=career_focus["learning_style"],
            session_length_avg=engagement.avg_session_length,
            activities_per_session=patterns["avg_activities_per_session"],
            return_frequency_days=engagement.return_frequency,
            engagement_trend=predictions["engagement_trend"],
            churn_risk_score=predictions["churn_risk"],
            success_probability=predictions["success_probability"]
        )
        
        # Store the analysis
        await self.db.behavior_patterns.replace_one(
            {"user_id": user_id},
            behavior_pattern.dict(),
            upsert=True
        )
        
        return behavior_pattern

    async def generate_personalized_insights(self, user_id: str) -> List[PersonalizedInsight]:
        """
        💡 Generate personalized insights like Instagram recommendations
        """
        
        # Get user behavior pattern
        pattern = await self.db.behavior_patterns.find_one({"user_id": user_id})
        if not pattern:
            # Generate pattern first
            pattern = await self.analyze_user_behavior(user_id)
            pattern = pattern.dict()
        
        insights = []
        
        # Career development insights
        if pattern.get("churn_risk_score", 0) > 0.7:
            insights.append(PersonalizedInsight(
                user_id=user_id,
                insight_type="engagement_boost",
                title="🚀 Let's get back on track!",
                description="We noticed you've been less active lately. Here are some quick wins to boost your career progress.",
                action_recommendations=[
                    "Complete a 5-minute skill assessment",
                    "Update your resume with recent achievements", 
                    "Explore new career paths in your field"
                ],
                relevance_score=0.9,
                priority_level="high",
                category="engagement"
            ))
        
        # Skill development insights
        if pattern.get("skill_focus_areas"):
            insights.append(PersonalizedInsight(
                user_id=user_id,
                insight_type="skill_development",
                title="📈 Level up your skills",
                description=f"Based on your activity, focus on {', '.join(pattern['skill_focus_areas'][:3])} for maximum impact.",
                action_recommendations=[
                    "Take targeted skill assessments",
                    "Build projects showcasing these skills",
                    "Connect with professionals in these areas"
                ],
                relevance_score=0.8,
                priority_level="medium",
                category="skills"
            ))
        
        # Learning style optimization
        if pattern.get("learning_style") == "hands_on":
            insights.append(PersonalizedInsight(
                user_id=user_id,
                insight_type="learning_optimization",
                title="🛠️ Perfect match for your learning style",
                description="You learn best by doing! Here are hands-on opportunities tailored for you.",
                action_recommendations=[
                    "Build a portfolio project",
                    "Take on coding challenges",
                    "Contribute to open source projects"
                ],
                relevance_score=0.7,
                priority_level="medium",
                category="learning"
            ))
        
        # Store insights
        for insight in insights:
            await self.db.personalized_insights.insert_one(insight.dict())
        
        return insights

# Analytics Service Functions
async def generate_user_analytics(user_id: str, timeframe: str = "7d") -> Dict[str, Any]:
    """Generate comprehensive user analytics"""
    
    db = await get_database()
    engine = PersonalizationEngine(db)
    
    # Get behavior analysis
    behavior_pattern = await engine.analyze_user_behavior(user_id)
    
    # Generate insights
    insights = await engine.generate_personalized_insights(user_id)
    
    return {
        "engagement_score": behavior_pattern.engagement_trend,
        "patterns": behavior_pattern.dict(),
        "insights": [insight.dict() for insight in insights],
        "recommendations": behavior_pattern.career_interests,
        "next_actions": [
            "Complete skill assessments for identified focus areas",
            "Explore career paths matching your interests",
            "Build projects showcasing your skills"
        ]
    }

async def process_real_time_analytics(user_id: str, activity_data: dict):
    """Process real-time analytics for user activity"""
    try:
        # Real-time analytics processing
        activity_type = activity_data.get('activity_type', 'unknown')
        feature_name = activity_data.get('feature_name', 'unknown')
        duration = activity_data.get('duration_seconds', 0)
        
        # Update user engagement metrics
        engagement_score = calculate_engagement_score(activity_data)
        
        # Store analytics data
        from ..core.database import get_database
        db = await get_database()
        
        analytics_record = {
            'user_id': user_id,
            'activity_type': activity_type,
            'feature_name': feature_name,
            'duration_seconds': duration,
            'engagement_score': engagement_score,
            'processed_at': datetime.utcnow(),
            'metadata': activity_data
        }
        
        await db.real_time_analytics.insert_one(analytics_record)
        
        # Trigger insights generation if needed
        if engagement_score > 80:
            await generate_personalized_insights(user_id)
            
        return True
        
    except Exception as e:
        logger.error(f"Real-time analytics processing failed: {e}")
        return False

def calculate_engagement_score(activity_data: dict) -> float:
    """Calculate engagement score from activity data"""
    base_score = 50.0
    duration = activity_data.get('duration_seconds', 0)
    activity_type = activity_data.get('activity_type', '')
    
    # Duration bonus
    if duration > 60:
        base_score += 20
    elif duration > 30:
        base_score += 10
    
    # Activity type bonus
    high_engagement_activities = ['resume_upload', 'interview_practice', 'skill_assessment']
    if activity_type in high_engagement_activities:
        base_score += 15
    
    return min(100.0, base_score)

async def generate_personalized_insights(user_id: str):
    """Generate personalized insights for high-engagement users"""
    try:
        from ..core.database import get_database
        db = await get_database()
        
        insight = {
            'user_id': user_id,
            'insight_type': 'engagement',
            'title': 'High Engagement Detected!',
            'description': 'You are actively using the platform. Keep up the great work!',
            'relevance_score': 0.9,
            'created_at': datetime.utcnow(),
            'data_points': {'engagement_threshold': 80}
        }
        
        await db.personalized_insights.insert_one(insight)
        return True
        
    except Exception as e:
        logger.error(f"Insight generation failed: {e}")
        return False
