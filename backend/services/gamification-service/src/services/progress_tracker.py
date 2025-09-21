from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from ..models.gamification_models import UserGamification, ActivityRecord, ActivityType
from ..db.client import get_database, get_redis
from ..db.gamification_crud import GamificationCRUD
from ..utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Service for tracking user progress and analytics"""
    
    def __init__(self):
        self._crud = None
        self._redis = None
        self._cache_manager = None
    
    async def initialize(self):
        """Initialize database connections"""
        if not self._crud:
            db = await get_database()
            self._crud = GamificationCRUD(db)
        if not self._redis:
            self._redis = await get_redis()
        if not self._cache_manager:
            self._cache_manager = CacheManager()
            await self._cache_manager.initialize()
    
    async def track_activity_progress(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track progress for a specific activity"""
        await self.initialize()
        
        try:
            # Get user profile
            user_profile = await self._crud.get_user_gamification(user_id)
            if not user_profile:
                return {"error": "User profile not found"}
            
            # Calculate activity impact
            activity_impact = await self._calculate_activity_impact(user_id, activity_data)
            
            # Update progress tracking
            progress_updates = await self._update_progress_metrics(user_id, activity_data, activity_impact)
            
            # Cache recent activity
            await self._cache_manager.cache_recent_activity(user_id, {
                **activity_data,
                "impact": activity_impact,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "activity_impact": activity_impact,
                "progress_updates": progress_updates,
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Error tracking activity progress for {user_id}: {e}")
            return {"error": str(e)}
    
    async def _calculate_activity_impact(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the impact of an activity on user progress"""
        try:
            activity_type = activity_data.get("activity_type")
            metadata = activity_data.get("metadata", {})
            
            impact = {
                "xp_gained": 0,
                "skill_progress": {},
                "career_progress": 0,
                "completion_boost": 0,
                "engagement_score": 0
            }
            
            # Calculate XP impact
            impact["xp_gained"] = activity_data.get("points_earned", 0)
            
            # Calculate skill progress
            skill_category = metadata.get("skill_category")
            if skill_category:
                impact["skill_progress"][skill_category] = impact["xp_gained"]
            
            # Calculate career progress
            if activity_type in ["course_completion", "skill_assessment", "career_path_progress"]:
                impact["career_progress"] = metadata.get("completion_rate", 0) * 10
            
            # Calculate completion boost
            completion_rate = metadata.get("completion_rate", 0)
            if completion_rate >= 0.9:
                impact["completion_boost"] = 5
            elif completion_rate >= 0.75:
                impact["completion_boost"] = 3
            elif completion_rate >= 0.5:
                impact["completion_boost"] = 1
            
            # Calculate engagement score
            impact["engagement_score"] = self._calculate_engagement_score(activity_data)
            
            return impact
            
        except Exception as e:
            logger.error(f"Error calculating activity impact: {e}")
            return {}
    
    def _calculate_engagement_score(self, activity_data: Dict[str, Any]) -> float:
        """Calculate engagement score for an activity"""
        try:
            score = 0.0
            metadata = activity_data.get("metadata", {})
            
            # Base score from activity type
            activity_scores = {
                "course_completion": 8.0,
                "skill_assessment": 7.0,
                "profile_completion": 6.0,
                "career_path_progress": 7.5,
                "resume_update": 5.0,
                "daily_login": 2.0
            }
            
            activity_type = activity_data.get("activity_type", "")
            score += activity_scores.get(activity_type, 3.0)
            
            # Completion rate bonus
            completion_rate = metadata.get("completion_rate", 0)
            score += completion_rate * 2
            
            # Time spent bonus
            time_spent = metadata.get("time_spent_minutes", 0)
            if time_spent > 0:
                score += min(time_spent / 10, 3.0)  # Max 3 points for time
            
            # Difficulty bonus
            difficulty = metadata.get("difficulty", "medium")
            difficulty_multipliers = {
                "easy": 1.0,
                "medium": 1.2,
                "hard": 1.5,
                "expert": 2.0
            }
            score *= difficulty_multipliers.get(difficulty, 1.0)
            
            return round(min(score, 10.0), 2)  # Cap at 10.0
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.0
    
    async def _update_progress_metrics(self, user_id: str, activity_data: Dict[str, Any], impact: Dict[str, Any]) -> Dict[str, Any]:
        """Update user's progress tracking metrics"""
        try:
            activity_type = activity_data.get("activity_type")
            metadata = activity_data.get("metadata", {})
            
            updates = {}
            
            # Update career path completion
            if activity_type == "career_path_progress":
                career_progress = metadata.get("completion_rate", 0)
                updates["progress_tracking.career_path_completion"] = career_progress
            
            # Update course completion count
            if activity_type == "course_completion":
                updates["$inc"] = updates.get("$inc", {})
                updates["$inc"]["progress_tracking.courses_completed"] = 1
            
            # Update goals completion
            if activity_type == "goal_completion":
                updates["$inc"] = updates.get("$inc", {})
                updates["$inc"]["progress_tracking.goals_completed"] = 1
            
            # Update profile completeness
            if activity_type == "profile_completion":
                profile_completeness = metadata.get("completion_rate", 0)
                updates["progress_tracking.profile_completeness"] = profile_completeness
            
            # Update assessments taken
            if activity_type == "skill_assessment":
                updates["$inc"] = updates.get("$inc", {})
                updates["$inc"]["progress_tracking.assessments_taken"] = 1
            
            # Apply updates to database
            if updates:
                success = await self._crud.update_user_gamification(user_id, updates)
                if success:
                    logger.info(f"Updated progress metrics for user {user_id}")
                return updates
            
            return {}
            
        except Exception as e:
            logger.error(f"Error updating progress metrics: {e}")
            return {}
    
    async def get_user_progress_summary(self, user_id: str, timeframe: str = "all_time") -> Dict[str, Any]:
        """Get comprehensive progress summary for user"""
        await self.initialize()
        
        try:
            # Check cache first
            cache_key = f"progress_summary:{user_id}:{timeframe}"
            if self._redis:
                cached_summary = await self._redis.get(cache_key)
                if cached_summary:
                    import json
                    return json.loads(cached_summary)
            
            # Get user profile
            user_profile = await self._crud.get_user_gamification(user_id)
            if not user_profile:
                return {"error": "User profile not found"}
            
            # Get activities based on timeframe
            activities = await self._get_activities_by_timeframe(user_id, timeframe)
            
            # Calculate summary statistics
            summary = {
                "user_id": user_id,
                "timeframe": timeframe,
                "total_activities": len(activities),
                "total_xp_earned": sum(activity.points_earned for activity in activities),
                "average_engagement": self._calculate_average_engagement(activities),
                "progress_metrics": user_profile.progress_tracking.dict(),
                "skill_breakdown": await self._calculate_skill_breakdown(activities),
                "activity_patterns": await self._analyze_activity_patterns(activities),
                "achievement_progress": await self._get_achievement_progress_summary(user_id),
                "trends": await self._calculate_progress_trends(user_id, timeframe),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Cache the summary
            if self._redis:
                import json
                await self._redis.set(
                    cache_key, 
                    json.dumps(summary, default=str),
                    ex=1800  # 30 minutes
                )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting progress summary for {user_id}: {e}")
            return {"error": str(e)}
    
    async def _get_activities_by_timeframe(self, user_id: str, timeframe: str) -> List[ActivityRecord]:
        """Get user activities filtered by timeframe"""
        try:
            if timeframe == "all_time":
                return await self._crud.get_user_activities(user_id, limit=1000)
            
            # Calculate date range
            now = datetime.utcnow()
            if timeframe == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif timeframe == "week":
                start_date = now - timedelta(days=7)
            elif timeframe == "month":
                start_date = now - timedelta(days=30)
            elif timeframe == "year":
                start_date = now - timedelta(days=365)
            else:
                start_date = now - timedelta(days=30)  # Default to month
            
            # Get activities from database with date filter
            all_activities = await self._crud.get_user_activities(user_id, limit=1000)
            filtered_activities = [
                activity for activity in all_activities
                if activity.timestamp >= start_date
            ]
            
            return filtered_activities
            
        except Exception as e:
            logger.error(f"Error getting activities by timeframe: {e}")
            return []
    
    def _calculate_average_engagement(self, activities: List[ActivityRecord]) -> float:
        """Calculate average engagement score from activities"""
        if not activities:
            return 0.0
        
        total_engagement = 0.0
        count = 0
        
        for activity in activities:
            engagement = activity.metadata.get("engagement_score", 0)
            if engagement > 0:
                total_engagement += engagement
                count += 1
        
        return round(total_engagement / count if count > 0 else 0.0, 2)
    
    async def _calculate_skill_breakdown(self, activities: List[ActivityRecord]) -> Dict[str, Any]:
        """Calculate skill progress breakdown"""
        try:
            skill_breakdown = {
                "technical": {"points": 0, "activities": 0},
                "soft_skills": {"points": 0, "activities": 0},
                "leadership": {"points": 0, "activities": 0},
                "communication": {"points": 0, "activities": 0}
            }
            
            for activity in activities:
                skill_category = activity.metadata.get("skill_category")
                if skill_category and skill_category in skill_breakdown:
                    skill_breakdown[skill_category]["points"] += activity.points_earned
                    skill_breakdown[skill_category]["activities"] += 1
            
            return skill_breakdown
            
        except Exception as e:
            logger.error(f"Error calculating skill breakdown: {e}")
            return {}
    
    async def _analyze_activity_patterns(self, activities: List[ActivityRecord]) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        try:
            if not activities:
                return {}
            
            patterns = {
                "most_active_hour": 0,
                "most_active_day": "Monday",
                "activity_frequency": "low",
                "consistency_score": 0.0,
                "preferred_activities": []
            }
            
            # Analyze time patterns
            hour_counts = {}
            day_counts = {}
            activity_type_counts = {}
            
            for activity in activities:
                # Hour analysis
                hour = activity.timestamp.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
                
                # Day analysis
                day_name = activity.timestamp.strftime("%A")
                day_counts[day_name] = day_counts.get(day_name, 0) + 1
                
                # Activity type analysis
                activity_type = activity.activity_type.value
                activity_type_counts[activity_type] = activity_type_counts.get(activity_type, 0) + 1
            
            # Find most active hour
            if hour_counts:
                patterns["most_active_hour"] = max(hour_counts, key=hour_counts.get)
            
            # Find most active day
            if day_counts:
                patterns["most_active_day"] = max(day_counts, key=day_counts.get)
            
            # Determine activity frequency
            days_with_activity = len(set(activity.timestamp.date() for activity in activities))
            total_days = (max(activity.timestamp for activity in activities) - 
                         min(activity.timestamp for activity in activities)).days + 1
            
            frequency_ratio = days_with_activity / total_days if total_days > 0 else 0
            
            if frequency_ratio >= 0.8:
                patterns["activity_frequency"] = "very_high"
            elif frequency_ratio >= 0.6:
                patterns["activity_frequency"] = "high"
            elif frequency_ratio >= 0.4:
                patterns["activity_frequency"] = "medium"
            elif frequency_ratio >= 0.2:
                patterns["activity_frequency"] = "low"
            else:
                patterns["activity_frequency"] = "very_low"
            
            patterns["consistency_score"] = round(frequency_ratio * 100, 1)
            
            # Find preferred activities
            if activity_type_counts:
                sorted_activities = sorted(activity_type_counts.items(), key=lambda x: x[1], reverse=True)
                patterns["preferred_activities"] = [
                    {"type": activity_type, "count": count} 
                    for activity_type, count in sorted_activities[:3]
                ]
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing activity patterns: {e}")
            return {}
    
    async def _get_achievement_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of achievement progress"""
        try:
            # Get user achievements
            user_achievements = await self._crud.get_user_achievements(user_id)
            all_achievements = await self._crud.get_all_achievements()
            
            total_achievements = len(all_achievements)
            unlocked_achievements = len(user_achievements)
            
            progress_summary = {
                "total_achievements": total_achievements,
                "unlocked_achievements": unlocked_achievements,
                "completion_percentage": round((unlocked_achievements / total_achievements * 100) if total_achievements > 0 else 0, 1),
                "recent_unlocks": len([ua for ua in user_achievements if ua.unlocked_at >= datetime.utcnow() - timedelta(days=7)])
            }
            
            return progress_summary
            
        except Exception as e:
            logger.error(f"Error getting achievement progress summary: {e}")
            return {}
    
    async def _calculate_progress_trends(self, user_id: str, timeframe: str) -> Dict[str, Any]:
        """Calculate progress trends over time"""
        try:
            trends = {
                "xp_trend": "stable",
                "activity_trend": "stable",
                "engagement_trend": "stable",
                "performance_indicators": []
            }
            
            # Get activities for comparison periods
            if timeframe == "week":
                current_activities = await self._get_activities_by_timeframe(user_id, "week")
                # Get previous week for comparison
                previous_week_start = datetime.utcnow() - timedelta(days=14)
                previous_week_end = datetime.utcnow() - timedelta(days=7)
                
                all_activities = await self._crud.get_user_activities(user_id, limit=1000)
                previous_activities = [
                    activity for activity in all_activities
                    if previous_week_start <= activity.timestamp <= previous_week_end
                ]
            
            elif timeframe == "month":
                current_activities = await self._get_activities_by_timeframe(user_id, "month")
                # Get previous month for comparison
                previous_month_start = datetime.utcnow() - timedelta(days=60)
                previous_month_end = datetime.utcnow() - timedelta(days=30)
                
                all_activities = await self._crud.get_user_activities(user_id, limit=1000)
                previous_activities = [
                    activity for activity in all_activities
                    if previous_month_start <= activity.timestamp <= previous_month_end
                ]
            
            else:
                return trends  # Can't calculate trends for other timeframes
            
            # Calculate trends
            current_xp = sum(activity.points_earned for activity in current_activities)
            previous_xp = sum(activity.points_earned for activity in previous_activities)
            
            current_activity_count = len(current_activities)
            previous_activity_count = len(previous_activities)
            
            # XP trend
            if current_xp > previous_xp * 1.1:
                trends["xp_trend"] = "increasing"
            elif current_xp < previous_xp * 0.9:
                trends["xp_trend"] = "decreasing"
            
            # Activity trend
            if current_activity_count > previous_activity_count * 1.1:
                trends["activity_trend"] = "increasing"
            elif current_activity_count < previous_activity_count * 0.9:
                trends["activity_trend"] = "decreasing"
            
            # Performance indicators
            if trends["xp_trend"] == "increasing" and trends["activity_trend"] == "increasing":
                trends["performance_indicators"].append("improving_performance")
            
            if current_activity_count > 0 and previous_activity_count > 0:
                avg_points_current = current_xp / current_activity_count
                avg_points_previous = previous_xp / previous_activity_count if previous_activity_count > 0 else 0
                
                if avg_points_current > avg_points_previous * 1.1:
                    trends["performance_indicators"].append("efficiency_improvement")
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating progress trends: {e}")
            return {}
    
    async def get_progress_insights(self, user_id: str) -> Dict[str, Any]:
        """Get actionable insights about user progress"""
        await self.initialize()
        
        try:
            summary = await self.get_user_progress_summary(user_id, "month")
            
            insights = {
                "recommendations": [],
                "strengths": [],
                "areas_for_improvement": [],
                "next_milestones": []
            }
            
            # Analyze patterns and generate insights
            patterns = summary.get("activity_patterns", {})
            consistency_score = patterns.get("consistency_score", 0)
            
            # Consistency insights
            if consistency_score >= 80:
                insights["strengths"].append("Excellent consistency in learning activities")
            elif consistency_score >= 60:
                insights["strengths"].append("Good consistency in learning activities")
            elif consistency_score < 40:
                insights["areas_for_improvement"].append("Improve consistency in daily learning")
                insights["recommendations"].append("Try to complete at least one learning activity daily")
            
            # Engagement insights
            avg_engagement = summary.get("average_engagement", 0)
            if avg_engagement >= 8:
                insights["strengths"].append("High engagement with learning materials")
            elif avg_engagement < 5:
                insights["areas_for_improvement"].append("Increase engagement with learning activities")
                insights["recommendations"].append("Focus on activities that interest you most")
            
            # Achievement insights
            achievement_progress = summary.get("achievement_progress", {})
            completion_percentage = achievement_progress.get("completion_percentage", 0)
            
            if completion_percentage >= 75:
                insights["strengths"].append("Great achievement progress")
            elif completion_percentage < 25:
                insights["recommendations"].append("Focus on unlocking more achievements for motivation")
            
            # Skill development insights
            skill_breakdown = summary.get("skill_breakdown", {})
            if skill_breakdown:
                # Find strongest and weakest skills
                skill_scores = {skill: data["points"] for skill, data in skill_breakdown.items()}
                if skill_scores:
                    strongest_skill = max(skill_scores, key=skill_scores.get)
                    weakest_skill = min(skill_scores, key=skill_scores.get)
                    
                    insights["strengths"].append(f"Strong progress in {strongest_skill}")
                    if skill_scores[weakest_skill] < skill_scores[strongest_skill] * 0.3:
                        insights["areas_for_improvement"].append(f"Develop {weakest_skill} skills")
                        insights["recommendations"].append(f"Focus on {weakest_skill} related activities")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting progress insights: {e}")
            return {"error": str(e)}
