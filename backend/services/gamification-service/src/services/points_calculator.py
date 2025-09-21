from typing import Dict, Tuple, Optional, List
from datetime import datetime, timedelta
import logging
from ..models.gamification_models import ActivityType, UserGamification
from ..core.points_engine import PointsEngine
from ..core.config import settings
from ..db.client import get_database, get_redis
from ..db.gamification_crud import GamificationCRUD

logger = logging.getLogger(__name__)

class PointsCalculator:
    """Service for calculating and awarding points"""
    
    def __init__(self):
        self.points_engine = PointsEngine()
        self._crud = None
        self._redis = None
    
    async def initialize(self):
        """Initialize database connections"""
        if not self._crud:
            db = await get_database()
            self._crud = GamificationCRUD(db)
        if not self._redis:
            self._redis = await get_redis()
    
    async def award_points(
        self, 
        user_id: str, 
        activity_type: ActivityType, 
        metadata: Optional[Dict] = None,
        custom_points: Optional[int] = None
    ) -> Dict[str, any]:
        """Award points to user for an activity"""
        await self.initialize()
        
        try:
            # Calculate points
            if custom_points is not None:
                points = custom_points
            else:
                points = self.points_engine.calculate_points(activity_type, metadata or {})
            
            # Get or create user profile
            user_profile = await self._crud.get_user_gamification(user_id)
            if not user_profile:
                # Create new user profile
                user_data = {
                    "user_id": user_id,
                    "username": metadata.get("username", f"User_{user_id[:8]}")
                }
                user_profile = await self._crud.create_user_gamification(user_data)
            
            # Store old values for comparison
            old_level = user_profile.current_level
            old_total_xp = user_profile.total_xp
            
            # Calculate new values
            new_total_xp = old_total_xp + points
            new_level, xp_to_next_level = self.points_engine.calculate_level(new_total_xp)
            
            # Check for level up
            level_up = self.points_engine.check_level_up(old_level, new_level)
            
            # Update streak if daily login
            streak_updated = False
            streak_bonus = 0
            if activity_type == ActivityType.DAILY_LOGIN:
                streak_info = await self._update_daily_streak(user_id, user_profile)
                streak_updated = streak_info["updated"]
                streak_bonus = streak_info["bonus_points"]
                points += streak_bonus
                new_total_xp += streak_bonus
                
                # Recalculate level with bonus
                new_level, xp_to_next_level = self.points_engine.calculate_level(new_total_xp)
                level_up = self.points_engine.check_level_up(old_level, new_level)
            
            # Update user profile
            update_data = {
                "total_xp": new_total_xp,
                "current_level": new_level,
                "xp_to_next_level": xp_to_next_level,
                "last_activity_date": datetime.utcnow()
            }
            
            # Update skill-specific points if metadata provided
            if metadata and "skill_category" in metadata:
                skill_category = metadata["skill_category"]
                if hasattr(user_profile.skill_points, skill_category):
                    current_skill_points = getattr(user_profile.skill_points, skill_category)
                    skill_points_key = f"skill_points.{skill_category}"
                    update_data[skill_points_key] = current_skill_points + points
            
            # Update database
            success = await self._crud.update_user_gamification(user_id, update_data)
            
            if success:
                # Record the activity
                activity_data = {
                    "user_id": user_id,
                    "activity_type": activity_type,
                    "points_earned": points,
                    "metadata": metadata or {}
                }
                await self._crud.record_activity(activity_data)
                
                # Cache updated user data
                await self._cache_user_profile(user_id, new_total_xp, new_level)
                
                return {
                    "success": True,
                    "points_awarded": points,
                    "base_points": points - streak_bonus,
                    "streak_bonus": streak_bonus,
                    "new_total_xp": new_total_xp,
                    "old_level": old_level,
                    "new_level": new_level,
                    "level_up": level_up,
                    "xp_to_next_level": xp_to_next_level,
                    "streak_updated": streak_updated
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update user profile"
                }
                
        except Exception as e:
            logger.error(f"Error awarding points to user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_daily_streak(self, user_id: str, user_profile: UserGamification) -> Dict[str, any]:
        """Update user's daily login streak"""
        try:
            now = datetime.utcnow()
            last_activity = user_profile.last_activity_date
            
            if not last_activity:
                # First login
                new_streak = 1
                bonus_points = self.points_engine.calculate_streak_bonus(new_streak)
            else:
                days_since_last = (now - last_activity).days
                
                if days_since_last == 1:
                    # Consecutive day
                    new_streak = user_profile.current_streak + 1
                    bonus_points = self.points_engine.calculate_streak_bonus(new_streak)
                elif days_since_last == 0:
                    # Already logged in today
                    return {"updated": False, "bonus_points": 0, "streak": user_profile.current_streak}
                else:
                    # Streak broken
                    new_streak = 1
                    bonus_points = self.points_engine.calculate_streak_bonus(new_streak)
            
            # Update longest streak if needed
            longest_streak = max(user_profile.longest_streak, new_streak)
            
            # Update streak in database
            streak_update = {
                "current_streak": new_streak,
                "longest_streak": longest_streak
            }
            
            await self._crud.update_user_gamification(user_id, streak_update)
            
            return {
                "updated": True,
                "bonus_points": bonus_points,
                "old_streak": user_profile.current_streak,
                "new_streak": new_streak,
                "longest_streak": longest_streak
            }
            
        except Exception as e:
            logger.error(f"Error updating streak for user {user_id}: {e}")
            return {"updated": False, "bonus_points": 0, "error": str(e)}
    
    async def _cache_user_profile(self, user_id: str, total_xp: int, level: int):
        """Cache user profile data in Redis"""
        try:
            if self._redis:
                cache_key = f"user_profile:{user_id}"
                cache_data = {
                    "total_xp": total_xp,
                    "level": level,
                    "cached_at": datetime.utcnow().isoformat()
                }
                
                await self._redis.hset(cache_key, mapping=cache_data)
                await self._redis.expire(cache_key, settings.redis_ttl_seconds)
                
        except Exception as e:
            logger.error(f"Error caching user profile {user_id}: {e}")
    
    async def get_user_points_summary(self, user_id: str) -> Dict[str, any]:
        """Get comprehensive points summary for user"""
        await self.initialize()
        
        try:
            # Try cache first
            if self._redis:
                cache_key = f"user_summary:{user_id}"
                cached_data = await self._redis.hgetall(cache_key)
                if cached_data:
                    return {
                        "user_id": user_id,
                        "total_xp": int(cached_data.get("total_xp", 0)),
                        "current_level": int(cached_data.get("current_level", 1)),
                        "current_streak": int(cached_data.get("current_streak", 0)),
                        "cached": True
                    }
            
            # Get from database
            user_profile = await self._crud.get_user_gamification(user_id)
            if not user_profile:
                return {"error": "User not found"}
            
            # Get user rank
            rank = await self._crud.get_user_rank(user_id)
            
            # Get recent activities
            recent_activities = await self._crud.get_user_activities(user_id, limit=10)
            
            summary = {
                "user_id": user_id,
                "username": user_profile.username,
                "total_xp": user_profile.total_xp,
                "current_level": user_profile.current_level,
                "xp_to_next_level": user_profile.xp_to_next_level,
                "current_streak": user_profile.current_streak,
                "longest_streak": user_profile.longest_streak,
                "total_achievements": user_profile.total_achievements,
                "rank": rank,
                "skill_points": user_profile.skill_points.dict(),
                "progress_tracking": user_profile.progress_tracking.dict(),
                "recent_activities": len(recent_activities),
                "last_activity": user_profile.last_activity_date.isoformat() if user_profile.last_activity_date else None
            }
            
            # Cache the summary
            if self._redis:
                cache_key = f"user_summary:{user_id}"
                await self._redis.hset(cache_key, mapping={k: str(v) for k, v in summary.items()})
                await self._redis.expire(cache_key, 300)  # 5 minutes
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting user points summary {user_id}: {e}")
            return {"error": str(e)}
    
    async def calculate_bonus_points(self, user_id: str, base_activity: ActivityType) -> int:
        """Calculate bonus points based on user activity patterns"""
        await self.initialize()
        
        try:
            # Get recent user activities
            activities = await self._crud.get_user_activities(user_id, limit=20)
            
            bonus = 0
            
            # Activity frequency bonus
            if len(activities) >= 5:  # Very active user
                bonus += 10
            elif len(activities) >= 3:  # Active user
                bonus += 5
            
            # Variety bonus - reward diverse activities
            activity_types = set([activity.activity_type for activity in activities])
            if len(activity_types) >= 3:
                bonus += 15
            
            return bonus
            
        except Exception as e:
            logger.error(f"Error calculating bonus points for {user_id}: {e}")
            return 0
