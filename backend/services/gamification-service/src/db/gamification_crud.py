from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime, timedelta
import logging
from ..models.gamification_models import (
    UserGamification, Achievement, UserAchievement, 
    ActivityRecord, Leaderboard, LeaderboardEntry,
    ActivityType, AchievementCategory, LeaderboardType
)

logger = logging.getLogger(__name__)

class GamificationCRUD:
    """Database operations for gamification system"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.user_gamification = database.user_gamification
        self.achievements = database.achievements
        self.user_achievements = database.user_achievements
        self.activity_records = database.activity_records
        self.leaderboards = database.leaderboards
    
    # User Gamification Profile Operations
    async def get_user_gamification(self, user_id: str) -> Optional[UserGamification]:
        """Get user's gamification profile"""
        try:
            doc = await self.user_gamification.find_one({"user_id": ObjectId(user_id)})
            return UserGamification(**doc) if doc else None
        except Exception as e:
            logger.error(f"Error getting user gamification: {e}")
            return None
    
    async def create_user_gamification(self, user_data: Dict[str, Any]) -> UserGamification:
        """Create new user gamification profile"""
        try:
            # Ensure user_id is ObjectId
            if isinstance(user_data["user_id"], str):
                user_data["user_id"] = ObjectId(user_data["user_id"])
            
            gamification_profile = UserGamification(**user_data)
            result = await self.user_gamification.insert_one(
                gamification_profile.dict(by_alias=True, exclude={"id"})
            )
            gamification_profile.id = result.inserted_id
            return gamification_profile
        except Exception as e:
            logger.error(f"Error creating user gamification: {e}")
            raise
    
    async def update_user_gamification(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user gamification profile"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = await self.user_gamification.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user gamification: {e}")
            return False
    
    async def update_user_points(self, user_id: str, points_to_add: int, activity_type: str) -> Dict[str, Any]:
        """Update user points and return the new state"""
        try:
            # Get current user data
            current_user = await self.get_user_gamification(user_id)
            if not current_user:
                return {"success": False, "error": "User not found"}
            
            # Calculate new totals
            new_total_xp = current_user.total_xp + points_to_add
            
            # Update the user
            update_result = await self.user_gamification.update_one(
                {"user_id": ObjectId(user_id)},
                {
                    "$inc": {
                        "total_xp": points_to_add,
                        "total_activities": 1,
                        "weekly_activities": 1,
                        "monthly_activities": 1
                    },
                    "$set": {
                        "updated_at": datetime.utcnow(),
                        "last_activity_date": datetime.utcnow()
                    }
                }
            )
            
            if update_result.modified_count > 0:
                return {
                    "success": True,
                    "new_total_xp": new_total_xp,
                    "points_added": points_to_add
                }
            return {"success": False, "error": "Update failed"}
            
        except Exception as e:
            logger.error(f"Error updating user points: {e}")
            return {"success": False, "error": str(e)}
    
    # Activity Tracking
    async def record_activity(self, activity_data: Dict[str, Any]) -> bool:
        """Record a user activity"""
        try:
            # Ensure user_id is ObjectId
            if isinstance(activity_data["user_id"], str):
                activity_data["user_id"] = ObjectId(activity_data["user_id"])
            
            activity = ActivityRecord(**activity_data)
            await self.activity_records.insert_one(
                activity.dict(by_alias=True, exclude={"id"})
            )
            return True
        except Exception as e:
            logger.error(f"Error recording activity: {e}")
            return False
    
    async def get_user_activities(self, user_id: str, limit: int = 50) -> List[ActivityRecord]:
        """Get user's recent activities"""
        try:
            cursor = self.activity_records.find(
                {"user_id": ObjectId(user_id)}
            ).sort("timestamp", -1).limit(limit)
            
            activities = []
            async for doc in cursor:
                activities.append(ActivityRecord(**doc))
            return activities
        except Exception as e:
            logger.error(f"Error getting user activities: {e}")
            return []
    
    # Achievement Operations
    async def get_all_achievements(self) -> List[Achievement]:
        """Get all available achievements"""
        try:
            cursor = self.achievements.find({"is_active": True})
            achievements = []
            async for doc in cursor:
                achievements.append(Achievement(**doc))
            return achievements
        except Exception as e:
            logger.error(f"Error getting achievements: {e}")
            return []
    
    async def get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """Get user's unlocked achievements"""
        try:
            cursor = self.user_achievements.find(
                {"user_id": ObjectId(user_id)}
            ).sort("unlocked_at", -1)
            
            user_achievements = []
            async for doc in cursor:
                user_achievements.append(UserAchievement(**doc))
            return user_achievements
        except Exception as e:
            logger.error(f"Error getting user achievements: {e}")
            return []
    
    async def unlock_achievement(self, user_id: str, achievement_id: str, points_earned: int) -> bool:
        """Unlock an achievement for user"""
        try:
            user_achievement = UserAchievement(
                user_id=ObjectId(user_id),
                achievement_id=ObjectId(achievement_id),
                points_earned=points_earned
            )
            
            # Check if already unlocked
            existing = await self.user_achievements.find_one({
                "user_id": ObjectId(user_id),
                "achievement_id": ObjectId(achievement_id)
            })
            
            if existing:
                return False  # Already unlocked
            
            # Insert new achievement
            await self.user_achievements.insert_one(
                user_achievement.dict(by_alias=True, exclude={"id"})
            )
            
            # Update user's achievement count
            await self.user_gamification.update_one(
                {"user_id": ObjectId(user_id)},
                {
                    "$inc": {"total_achievements": 1},
                    "$push": {"achievements_unlocked": ObjectId(achievement_id)},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error unlocking achievement: {e}")
            return False
    
    # Leaderboard Operations
    async def get_leaderboard(self, leaderboard_type: LeaderboardType, limit: int = 100) -> Optional[Leaderboard]:
        """Get leaderboard by type"""
        try:
            doc = await self.leaderboards.find_one({"type": leaderboard_type.value})
            return Leaderboard(**doc) if doc else None
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return None
    
    async def update_leaderboard(self, leaderboard_type: LeaderboardType, entries: List[Dict[str, Any]]) -> bool:
        """Update leaderboard with new entries"""
        try:
            leaderboard_data = {
                "type": leaderboard_type.value,
                "entries": entries,
                "last_updated": datetime.utcnow()
            }
            
            result = await self.leaderboards.update_one(
                {"type": leaderboard_type.value},
                {"$set": leaderboard_data},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error updating leaderboard: {e}")
            return False
    
    async def get_top_users_by_xp(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get top users by XP for leaderboard"""
        try:
            pipeline = [
                {"$sort": {"total_xp": -1}},
                {"$limit": limit},
                {"$project": {
                    "user_id": 1,
                    "username": 1,
                    "total_xp": 1,
                    "current_level": 1,
                    "total_achievements": 1
                }}
            ]
            
            cursor = self.user_gamification.aggregate(pipeline)
            users = []
            async for doc in cursor:
                users.append(doc)
            return users
        except Exception as e:
            logger.error(f"Error getting top users: {e}")
            return []
    
    # Analytics & Statistics
    async def get_user_rank(self, user_id: str) -> Optional[int]:
        """Get user's current rank based on XP"""
        try:
            user = await self.get_user_gamification(user_id)
            if not user:
                return None
            
            # Count users with higher XP
            higher_xp_count = await self.user_gamification.count_documents(
                {"total_xp": {"$gt": user.total_xp}}
            )
            
            return higher_xp_count + 1
        except Exception as e:
            logger.error(f"Error getting user rank: {e}")
            return None
    
    async def get_gamification_stats(self) -> Dict[str, Any]:
        """Get overall gamification statistics"""
        try:
            stats = {}
            
            # User stats
            stats["total_users"] = await self.user_gamification.count_documents({})
            stats["active_users_today"] = await self.user_gamification.count_documents({
                "last_activity_date": {"$gte": datetime.utcnow() - timedelta(days=1)}
            })
            
            # Achievement stats
            stats["total_achievements"] = await self.achievements.count_documents({"is_active": True})
            stats["total_unlocks"] = await self.user_achievements.count_documents({})
            
            # Activity stats
            stats["activities_today"] = await self.activity_records.count_documents({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=1)}
            })
            
            return stats
        except Exception as e:
            logger.error(f"Error getting gamification stats: {e}")
            return {}
    
    # Utility Methods
    async def ensure_indexes(self):
        """Create necessary database indexes"""
        try:
            # User gamification indexes
            await self.user_gamification.create_index("user_id", unique=True)
            await self.user_gamification.create_index([("total_xp", -1)])
            await self.user_gamification.create_index("last_activity_date")
            
            # User achievements indexes
            await self.user_achievements.create_index([("user_id", 1), ("achievement_id", 1)], unique=True)
            await self.user_achievements.create_index("unlocked_at")
            
            # Activity records indexes
            await self.activity_records.create_index([("user_id", 1), ("timestamp", -1)])
            await self.activity_records.create_index("activity_type")
            
            # Leaderboard indexes
            await self.leaderboards.create_index("type", unique=True)
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
