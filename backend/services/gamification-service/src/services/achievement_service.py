from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from ..models.gamification_models import (
    Achievement, UserAchievement, UserGamification, 
    ActivityType, AchievementCategory, ActivityRecord
)
from ..db.client import get_database, get_redis
from ..db.gamification_crud import GamificationCRUD
from ..core.config import settings
from ..utils.notification_client import NotificationClient

logger = logging.getLogger(__name__)

class AchievementService:
    """Service for managing achievements and unlocks"""
    
    def __init__(self):
        self._crud = None
        self._redis = None
        self._notification_client = NotificationClient()
    
    async def initialize(self):
        """Initialize database connections"""
        if not self._crud:
            db = await get_database()
            self._crud = GamificationCRUD(db)
        if not self._redis:
            self._redis = await get_redis()
    
    async def check_and_unlock_achievements(self, user_id: str, activity_type: ActivityType, metadata: Dict = None) -> List[Dict[str, Any]]:
        """Check for new achievement unlocks after user activity"""
        await self.initialize()
        
        try:
            # Get user profile and achievements
            user_profile = await self._crud.get_user_gamification(user_id)
            if not user_profile:
                return []
            
            # Get all available achievements
            all_achievements = await self._crud.get_all_achievements()
            user_achievements = await self._crud.get_user_achievements(user_id)
            unlocked_achievement_ids = {ua.achievement_id for ua in user_achievements}
            
            # Filter achievements that haven't been unlocked
            available_achievements = [
                ach for ach in all_achievements 
                if ach.id not in unlocked_achievement_ids
            ]
            
            newly_unlocked = []
            
            # Check each available achievement
            for achievement in available_achievements:
                if await self._check_achievement_criteria(user_id, achievement, user_profile, activity_type, metadata):
                    # Unlock the achievement
                    unlock_success = await self._crud.unlock_achievement(
                        user_id, 
                        str(achievement.id), 
                        achievement.points_reward
                    )
                    
                    if unlock_success:
                        newly_unlocked.append({
                            "achievement_id": str(achievement.id),
                            "name": achievement.name,
                            "description": achievement.description,
                            "points_reward": achievement.points_reward,
                            "category": achievement.category,
                            "rarity": achievement.rarity,
                            "unlocked_at": datetime.utcnow().isoformat()
                        })
                        
                        # Send notification
                        await self._send_achievement_notification(user_id, achievement)
                        
                        # Update achievement unlock stats
                        await self._update_achievement_stats(str(achievement.id))
            
            # Cache the result
            if newly_unlocked and self._redis:
                cache_key = f"recent_unlocks:{user_id}"
                await self._redis.lpush(cache_key, *[str(ach["achievement_id"]) for ach in newly_unlocked])
                await self._redis.expire(cache_key, 3600)  # 1 hour
            
            return newly_unlocked
            
        except Exception as e:
            logger.error(f"Error checking achievements for user {user_id}: {e}")
            return []
    
    async def _check_achievement_criteria(
        self, 
        user_id: str, 
        achievement: Achievement, 
        user_profile: UserGamification,
        current_activity: ActivityType,
        metadata: Dict = None
    ) -> bool:
        """Check if user meets achievement criteria"""
        try:
            criteria = achievement.unlock_criteria
            
            # Activity count based achievements
            if criteria.type == "activity_count":
                if criteria.specific_action:
                    # Count specific activity type
                    activities = await self._crud.get_user_activities(user_id, limit=1000)
                    count = sum(1 for activity in activities if activity.activity_type.value == criteria.specific_action)
                else:
                    # Total activities
                    count = user_profile.total_activities
                
                return count >= criteria.threshold
            
            # Streak based achievements
            elif criteria.type == "streak":
                return user_profile.current_streak >= criteria.threshold
            
            # Level based achievements
            elif criteria.type == "level":
                return user_profile.current_level >= criteria.threshold
            
            # Points based achievements
            elif criteria.type == "points":
                if criteria.specific_action == "skill_points":
                    # Check skill-specific points
                    skill_category = metadata.get("skill_category") if metadata else None
                    if skill_category and hasattr(user_profile.skill_points, skill_category):
                        skill_points = getattr(user_profile.skill_points, skill_category)
                        return skill_points >= criteria.threshold
                else:
                    # Total XP
                    return user_profile.total_xp >= criteria.threshold
            
            # Completion based achievements
            elif criteria.type == "completion":
                if criteria.specific_action == "profile_completion":
                    return user_profile.progress_tracking.profile_completeness >= (criteria.threshold / 100.0)
                elif criteria.specific_action == "career_path_completion":
                    return user_profile.progress_tracking.career_path_completion >= (criteria.threshold / 100.0)
                elif criteria.specific_action == "courses":
                    return user_profile.progress_tracking.courses_completed >= criteria.threshold
            
            # Time-based achievements
            elif criteria.type == "time_active":
                if user_profile.created_at:
                    days_active = (datetime.utcnow() - user_profile.created_at).days
                    return days_active >= criteria.threshold
            
            # Special achievements
            elif criteria.type == "special":
                return await self._check_special_achievement(user_id, criteria, user_profile, current_activity, metadata)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking achievement criteria: {e}")
            return False
    
    async def _check_special_achievement(
        self, 
        user_id: str, 
        criteria: Any,
        user_profile: UserGamification,
        current_activity: ActivityType,
        metadata: Dict = None
    ) -> bool:
        """Check special achievement criteria"""
        try:
            if criteria.specific_action == "first_day_completion":
                # User completed multiple activities on first day
                if user_profile.created_at and user_profile.created_at.date() == datetime.utcnow().date():
                    return user_profile.total_activities >= criteria.threshold
            
            elif criteria.specific_action == "weekend_warrior":
                # Activity on weekend
                current_day = datetime.utcnow().weekday()  # 5=Saturday, 6=Sunday
                if current_day in [5, 6]:
                    weekend_activities = await self._count_weekend_activities(user_id)
                    return weekend_activities >= criteria.threshold
            
            elif criteria.specific_action == "early_bird":
                # Activity before 8 AM
                current_hour = datetime.utcnow().hour
                if current_hour < 8:
                    early_activities = await self._count_early_morning_activities(user_id)
                    return early_activities >= criteria.threshold
            
            elif criteria.specific_action == "perfectionist":
                # High completion rates
                if metadata and metadata.get("completion_rate", 0) >= 0.95:
                    perfect_completions = await self._count_perfect_completions(user_id)
                    return perfect_completions >= criteria.threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking special achievement: {e}")
            return False
    
    async def _count_weekend_activities(self, user_id: str) -> int:
        """Count activities done on weekends"""
        try:
            activities = await self._crud.get_user_activities(user_id, limit=500)
            weekend_count = 0
            
            for activity in activities:
                if activity.timestamp.weekday() in [5, 6]:  # Saturday, Sunday
                    weekend_count += 1
            
            return weekend_count
        except:
            return 0
    
    async def _count_early_morning_activities(self, user_id: str) -> int:
        """Count activities done before 8 AM"""
        try:
            activities = await self._crud.get_user_activities(user_id, limit=500)
            early_count = 0
            
            for activity in activities:
                if activity.timestamp.hour < 8:
                    early_count += 1
            
            return early_count
        except:
            return 0
    
    async def _count_perfect_completions(self, user_id: str) -> int:
        """Count activities with 95%+ completion rate"""
        try:
            activities = await self._crud.get_user_activities(user_id, limit=500)
            perfect_count = 0
            
            for activity in activities:
                completion_rate = activity.metadata.get("completion_rate", 0)
                if completion_rate >= 0.95:
                    perfect_count += 1
            
            return perfect_count
        except:
            return 0
    
    async def _send_achievement_notification(self, user_id: str, achievement: Achievement):
        """Send notification for achievement unlock"""
        try:
            notification_data = {
                "user_id": user_id,
                "type": "achievement_unlocked",
                "title": "🏆 Achievement Unlocked!",
                "message": f"Congratulations! You've earned '{achievement.name}'",
                "data": {
                    "achievement_id": str(achievement.id),
                    "achievement_name": achievement.name,
                    "points_reward": achievement.points_reward,
                    "category": achievement.category.value,
                    "rarity": achievement.rarity
                }
            }
            
            await self._notification_client.send_notification(notification_data)
            
        except Exception as e:
            logger.error(f"Error sending achievement notification: {e}")
    
    async def _update_achievement_stats(self, achievement_id: str):
        """Update achievement unlock statistics"""
        try:
            # Increment unlock count
            from bson import ObjectId
            achievement_oid = ObjectId(achievement_id)
            
            db = await get_database()
            await db.achievements.update_one(
                {"_id": achievement_oid},
                {"$inc": {"unlock_count": 1}}
            )
            
            # Calculate unlock percentage (you might want to do this periodically instead)
            total_users = await db.user_gamification.count_documents({})
            if total_users > 0:
                achievement = await db.achievements.find_one({"_id": achievement_oid})
                if achievement:
                    unlock_percentage = (achievement.get("unlock_count", 0) / total_users) * 100
                    await db.achievements.update_one(
                        {"_id": achievement_oid},
                        {"$set": {"unlock_percentage": round(unlock_percentage, 2)}}
                    )
            
        except Exception as e:
            logger.error(f"Error updating achievement stats: {e}")
    
    async def get_user_achievement_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's progress towards all achievements"""
        await self.initialize()
        
        try:
            # Get user profile and achievements
            user_profile = await self._crud.get_user_gamification(user_id)
            if not user_profile:
                return {"error": "User not found"}
            
            all_achievements = await self._crud.get_all_achievements()
            user_achievements = await self._crud.get_user_achievements(user_id)
            unlocked_ids = {str(ua.achievement_id) for ua in user_achievements}
            
            progress_data = {
                "unlocked_count": len(user_achievements),
                "total_achievements": len(all_achievements),
                "completion_percentage": (len(user_achievements) / len(all_achievements) * 100) if all_achievements else 0,
                "achievements": []
            }
            
            # Calculate progress for each achievement
            for achievement in all_achievements:
                achievement_data = {
                    "id": str(achievement.id),
                    "name": achievement.name,
                    "description": achievement.description,
                    "category": achievement.category.value,
                    "points_reward": achievement.points_reward,
                    "rarity": achievement.rarity,
                    "unlocked": str(achievement.id) in unlocked_ids,
                    "progress": 0,
                    "progress_text": ""
                }
                
                if not achievement_data["unlocked"]:
                    # Calculate progress towards achievement
                    progress_info = await self._calculate_achievement_progress(user_id, achievement, user_profile)
                    achievement_data.update(progress_info)
                else:
                    # Find unlock date
                    for ua in user_achievements:
                        if str(ua.achievement_id) == str(achievement.id):
                            achievement_data["unlocked_at"] = ua.unlocked_at.isoformat()
                            achievement_data["progress"] = 100
                            achievement_data["progress_text"] = "Unlocked!"
                            break
                
                progress_data["achievements"].append(achievement_data)
            
            return progress_data
            
        except Exception as e:
            logger.error(f"Error getting achievement progress for user {user_id}: {e}")
            return {"error": str(e)}
    
    async def _calculate_achievement_progress(self, user_id: str, achievement: Achievement, user_profile: UserGamification) -> Dict[str, Any]:
        """Calculate progress percentage towards an achievement"""
        try:
            criteria = achievement.unlock_criteria
            current_value = 0
            
            if criteria.type == "activity_count":
                if criteria.specific_action:
                    activities = await self._crud.get_user_activities(user_id, limit=1000)
                    current_value = sum(1 for activity in activities if activity.activity_type.value == criteria.specific_action)
                else:
                    current_value = user_profile.total_activities
            
            elif criteria.type == "streak":
                current_value = user_profile.current_streak
            
            elif criteria.type == "level":
                current_value = user_profile.current_level
            
            elif criteria.type == "points":
                current_value = user_profile.total_xp
            
            elif criteria.type == "completion":
                if criteria.specific_action == "profile_completion":
                    current_value = int(user_profile.progress_tracking.profile_completeness * 100)
                elif criteria.specific_action == "courses":
                    current_value = user_profile.progress_tracking.courses_completed
            
            # Calculate progress percentage
            progress = min(100, (current_value / criteria.threshold) * 100) if criteria.threshold > 0 else 0
            
            return {
                "progress": round(progress, 1),
                "progress_text": f"{current_value}/{criteria.threshold}",
                "current_value": current_value,
                "target_value": criteria.threshold
            }
            
        except Exception as e:
            logger.error(f"Error calculating achievement progress: {e}")
            return {"progress": 0, "progress_text": "Error"}
    
    async def get_achievement_leaderboard(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get users with most achievements"""
        await self.initialize()
        
        try:
            # Use aggregation to get top users by achievement count
            pipeline = [
                {"$sort": {"total_achievements": -1}},
                {"$limit": limit},
                {"$project": {
                    "user_id": 1,
                    "username": 1,
                    "total_achievements": 1,
                    "current_level": 1,
                    "total_xp": 1
                }}
            ]
            
            db = await get_database()
            cursor = db.user_gamification.aggregate(pipeline)
            
            leaderboard = []
            rank = 1
            async for doc in cursor:
                leaderboard.append({
                    "rank": rank,
                    "user_id": str(doc["user_id"]),
                    "username": doc["username"],
                    "total_achievements": doc["total_achievements"],
                    "current_level": doc["current_level"],
                    "total_xp": doc["total_xp"]
                })
                rank += 1
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting achievement leaderboard: {e}")
            return []
    
    async def create_default_achievements(self):
        """Create default achievements for the platform"""
        await self.initialize()
        
        default_achievements = [
            # Learning Achievements
            {
                "name": "First Steps",
                "description": "Complete your first learning activity",
                "category": AchievementCategory.LEARNING,
                "points_reward": 100,
                "rarity": "common",
                "unlock_criteria": {
                    "type": "activity_count",
                    "threshold": 1,
                    "specific_action": None
                }
            },
            {
                "name": "Knowledge Seeker",
                "description": "Complete 10 learning activities",
                "category": AchievementCategory.LEARNING,
                "points_reward": 250,
                "rarity": "common",
                "unlock_criteria": {
                    "type": "activity_count",
                    "threshold": 10,
                    "specific_action": None
                }
            },
            {
                "name": "Course Master",
                "description": "Complete 5 courses",
                "category": AchievementCategory.LEARNING,
                "points_reward": 500,
                "rarity": "rare",
                "unlock_criteria": {
                    "type": "completion",
                    "threshold": 5,
                    "specific_action": "courses"
                }
            },
            # Streak Achievements
            {
                "name": "Consistency",
                "description": "Maintain a 3-day streak",
                "category": AchievementCategory.MILESTONE,
                "points_reward": 150,
                "rarity": "common",
                "unlock_criteria": {
                    "type": "streak",
                    "threshold": 3,
                    "specific_action": None
                }
            },
            {
                "name": "Dedication",
                "description": "Maintain a 7-day streak",
                "category": AchievementCategory.MILESTONE,
                "points_reward": 300,
                "rarity": "rare",
                "unlock_criteria": {
                    "type": "streak",
                    "threshold": 7,
                    "specific_action": None
                }
            },
            {
                "name": "Unstoppable",
                "description": "Maintain a 30-day streak",
                "category": AchievementCategory.MILESTONE,
                "points_reward": 1000,
                "rarity": "legendary",
                "unlock_criteria": {
                    "type": "streak",
                    "threshold": 30,
                    "specific_action": None
                }
            },
            # Level Achievements
            {
                "name": "Rising Star",
                "description": "Reach level 10",
                "category": AchievementCategory.MILESTONE,
                "points_reward": 500,
                "rarity": "rare",
                "unlock_criteria": {
                    "type": "level",
                    "threshold": 10,
                    "specific_action": None
                }
            },
            {
                "name": "Expert",
                "description": "Reach level 25",
                "category": AchievementCategory.MILESTONE,
                "points_reward": 1000,
                "rarity": "epic",
                "unlock_criteria": {
                    "type": "level",
                    "threshold": 25,
                    "specific_action": None
                }
            },
            # Career Achievements
            {
                "name": "Profile Complete",
                "description": "Complete 100% of your profile",
                "category": AchievementCategory.CAREER,
                "points_reward": 200,
                "rarity": "common",
                "unlock_criteria": {
                    "type": "completion",
                    "threshold": 100,
                    "specific_action": "profile_completion"
                }
            },
            {
                "name": "Career Explorer",
                "description": "Complete 50% of your career path",
                "category": AchievementCategory.CAREER,
                "points_reward": 400,
                "rarity": "rare",
                "unlock_criteria": {
                    "type": "completion",
                    "threshold": 50,
                    "specific_action": "career_path_completion"
                }
            },
            # Special Achievements
            {
                "name": "Early Bird",
                "description": "Complete 5 activities before 8 AM",
                "category": AchievementCategory.SPECIAL,
                "points_reward": 300,
                "rarity": "epic",
                "unlock_criteria": {
                    "type": "special",
                    "threshold": 5,
                    "specific_action": "early_bird"
                }
            },
            {
                "name": "Weekend Warrior",
                "description": "Complete 10 activities on weekends",
                "category": AchievementCategory.SPECIAL,
                "points_reward": 400,
                "rarity": "epic",
                "unlock_criteria": {
                    "type": "special",
                    "threshold": 10,
                    "specific_action": "weekend_warrior"
                }
            }
        ]
        
        try:
            db = await get_database()
            for ach_data in default_achievements:
                # Check if achievement already exists
                existing = await db.achievements.find_one({"name": ach_data["name"]})
                if not existing:
                    await db.achievements.insert_one(ach_data)
            
            logger.info(f"Created {len(default_achievements)} default achievements")
            
        except Exception as e:
            logger.error(f"Error creating default achievements: {e}")
