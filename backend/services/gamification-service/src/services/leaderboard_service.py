from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from ..models.gamification_models import (
    Leaderboard, LeaderboardEntry, LeaderboardType, UserGamification
)
from ..db.client import get_database, get_redis
from ..db.gamification_crud import GamificationCRUD
from ..core.config import settings

logger = logging.getLogger(__name__)

class LeaderboardService:
    """Service for managing leaderboards and rankings"""
    
    def __init__(self):
        self._crud = None
        self._redis = None
    
    async def initialize(self):
        """Initialize database connections"""
        if not self._crud:
            db = await get_database()
            self._crud = GamificationCRUD(db)
        if not self._redis:
            self._redis = await get_redis()
    
    async def update_global_leaderboard(self) -> bool:
        """Update global leaderboard with current rankings"""
        await self.initialize()
        
        try:
            # Get top users by total XP
            top_users = await self._crud.get_top_users_by_xp(settings.max_leaderboard_size)
            
            # Create leaderboard entries
            entries = []
            for rank, user_data in enumerate(top_users, 1):
                entry = {
                    "user_id": user_data["user_id"],
                    "username": user_data["username"],
                    "score": user_data["total_xp"],
                    "rank": rank,
                    "level": user_data.get("current_level", 1),
                    "achievements_count": user_data.get("total_achievements", 0)
                }
                entries.append(entry)
            
            # Update leaderboard in database
            success = await self._crud.update_leaderboard(LeaderboardType.GLOBAL, entries)
            
            if success:
                # Cache the leaderboard
                await self._cache_leaderboard("global", entries)
                logger.info(f"Updated global leaderboard with {len(entries)} entries")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating global leaderboard: {e}")
            return False
    
    async def update_weekly_leaderboard(self) -> bool:
        """Update weekly leaderboard based on this week's activities"""
        await self.initialize()
        
        try:
            # Calculate start of current week
            now = datetime.utcnow()
            week_start = now - timedelta(days=now.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Get weekly activity points for all users
            weekly_scores = await self._calculate_weekly_scores(week_start)
            
            # Sort by score and create entries
            sorted_scores = sorted(weekly_scores.items(), key=lambda x: x[1]["total_points"], reverse=True)
            
            entries = []
            for rank, (user_id, user_data) in enumerate(sorted_scores[:settings.max_leaderboard_size], 1):
                entry = {
                    "user_id": user_id,
                    "username": user_data["username"],
                    "score": user_data["total_points"],
                    "rank": rank,
                    "level": user_data.get("level", 1),
                    "achievements_count": user_data.get("achievements_count", 0)
                }
                entries.append(entry)
            
            # Update leaderboard in database
            success = await self._crud.update_leaderboard(LeaderboardType.WEEKLY, entries)
            
            if success:
                # Cache the leaderboard
                await self._cache_leaderboard("weekly", entries)
                logger.info(f"Updated weekly leaderboard with {len(entries)} entries")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating weekly leaderboard: {e}")
            return False
    
    async def update_monthly_leaderboard(self) -> bool:
        """Update monthly leaderboard based on this month's activities"""
        await self.initialize()
        
        try:
            # Calculate start of current month
            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get monthly activity points for all users
            monthly_scores = await self._calculate_monthly_scores(month_start)
            
            # Sort by score and create entries
            sorted_scores = sorted(monthly_scores.items(), key=lambda x: x[1]["total_points"], reverse=True)
            
            entries = []
            for rank, (user_id, user_data) in enumerate(sorted_scores[:settings.max_leaderboard_size], 1):
                entry = {
                    "user_id": user_id,
                    "username": user_data["username"],
                    "score": user_data["total_points"],
                    "rank": rank,
                    "level": user_data.get("level", 1),
                    "achievements_count": user_data.get("achievements_count", 0)
                }
                entries.append(entry)
            
            # Update leaderboard in database
            success = await self._crud.update_leaderboard(LeaderboardType.MONTHLY, entries)
            
            if success:
                # Cache the leaderboard
                await self._cache_leaderboard("monthly", entries)
                logger.info(f"Updated monthly leaderboard with {len(entries)} entries")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating monthly leaderboard: {e}")
            return False
    
    async def _calculate_weekly_scores(self, week_start: datetime) -> Dict[str, Dict[str, Any]]:
        """Calculate weekly points for all users"""
        try:
            db = await get_database()
            
            # Aggregate weekly activities
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": week_start}
                    }
                },
                {
                    "$group": {
                        "_id": "$user_id",
                        "total_points": {"$sum": "$points_earned"},
                        "activity_count": {"$sum": 1}
                    }
                },
                {
                    "$lookup": {
                        "from": "user_gamification",
                        "localField": "_id",
                        "foreignField": "user_id",
                        "as": "user_info"
                    }
                },
                {
                    "$unwind": "$user_info"
                },
                {
                    "$project": {
                        "user_id": {"$toString": "$_id"},
                        "total_points": 1,
                        "activity_count": 1,
                        "username": "$user_info.username",
                        "level": "$user_info.current_level",
                        "achievements_count": "$user_info.total_achievements"
                    }
                }
            ]
            
            cursor = db.activity_records.aggregate(pipeline)
            weekly_scores = {}
            
            async for doc in cursor:
                weekly_scores[doc["user_id"]] = {
                    "total_points": doc["total_points"],
                    "activity_count": doc["activity_count"],
                    "username": doc["username"],
                    "level": doc["level"],
                    "achievements_count": doc["achievements_count"]
                }
            
            return weekly_scores
            
        except Exception as e:
            logger.error(f"Error calculating weekly scores: {e}")
            return {}
    
    async def _calculate_monthly_scores(self, month_start: datetime) -> Dict[str, Dict[str, Any]]:
        """Calculate monthly points for all users"""
        try:
            db = await get_database()
            
            # Similar to weekly but for month range
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": month_start}
                    }
                },
                {
                    "$group": {
                        "_id": "$user_id",
                        "total_points": {"$sum": "$points_earned"},
                        "activity_count": {"$sum": 1}
                    }
                },
                {
                    "$lookup": {
                        "from": "user_gamification",
                        "localField": "_id",
                        "foreignField": "user_id",
                        "as": "user_info"
                    }
                },
                {
                    "$unwind": "$user_info"
                },
                {
                    "$project": {
                        "user_id": {"$toString": "$_id"},
                        "total_points": 1,
                        "activity_count": 1,
                        "username": "$user_info.username",
                        "level": "$user_info.current_level",
                        "achievements_count": "$user_info.total_achievements"
                    }
                }
            ]
            
            cursor = db.activity_records.aggregate(pipeline)
            monthly_scores = {}
            
            async for doc in cursor:
                monthly_scores[doc["user_id"]] = {
                    "total_points": doc["total_points"],
                    "activity_count": doc["activity_count"],
                    "username": doc["username"],
                    "level": doc["level"],
                    "achievements_count": doc["achievements_count"]
                }
            
            return monthly_scores
            
        except Exception as e:
            logger.error(f"Error calculating monthly scores: {e}")
            return {}
    
    async def get_leaderboard(self, leaderboard_type: str, limit: int = 50) -> Dict[str, Any]:
        """Get leaderboard by type"""
        await self.initialize()
        
        try:
            # Try cache first
            cached_leaderboard = await self._get_cached_leaderboard(leaderboard_type)
            if cached_leaderboard:
                return {
                    "type": leaderboard_type,
                    "entries": cached_leaderboard[:limit],
                    "cached": True,
                    "last_updated": "cached"
                }
            
            # Get from database
            leaderboard_enum = LeaderboardType(leaderboard_type.upper())
            leaderboard = await self._crud.get_leaderboard(leaderboard_enum, limit)
            
            if leaderboard:
                return {
                    "type": leaderboard_type,
                    "entries": [entry.dict() for entry in leaderboard.entries[:limit]],
                    "cached": False,
                    "last_updated": leaderboard.last_updated.isoformat()
                }
            else:
                return {
                    "type": leaderboard_type,
                    "entries": [],
                    "cached": False,
                    "last_updated": None,
                    "message": "Leaderboard not found or empty"
                }
                
        except Exception as e:
            logger.error(f"Error getting leaderboard {leaderboard_type}: {e}")
            return {
                "type": leaderboard_type,
                "entries": [],
                "error": str(e)
            }
    
    async def get_user_leaderboard_position(self, user_id: str, leaderboard_type: str = "global") -> Dict[str, Any]:
        """Get user's position in specific leaderboard"""
        await self.initialize()
        
        try:
            leaderboard_data = await self.get_leaderboard(leaderboard_type, settings.max_leaderboard_size)
            entries = leaderboard_data.get("entries", [])
            
            # Find user in leaderboard
            user_position = None
            for entry in entries:
                if str(entry["user_id"]) == str(user_id):
                    user_position = entry
                    break
            
            if user_position:
                return {
                    "user_id": user_id,
                    "leaderboard_type": leaderboard_type,
                    "position": user_position,
                    "total_entries": len(entries)
                }
            else:
                # User not in top entries, get their approximate rank
                rank = await self._crud.get_user_rank(user_id)
                return {
                    "user_id": user_id,
                    "leaderboard_type": leaderboard_type,
                    "position": {
                        "rank": rank,
                        "message": "Not in top rankings"
                    },
                    "total_entries": len(entries)
                }
                
        except Exception as e:
            logger.error(f"Error getting user leaderboard position: {e}")
            return {"error": str(e)}
    
    async def _cache_leaderboard(self, leaderboard_type: str, entries: List[Dict[str, Any]]):
        """Cache leaderboard in Redis"""
        try:
            if self._redis:
                cache_key = f"leaderboard:{leaderboard_type}"
                
                # Store as JSON string
                import json
                cache_data = {
                    "entries": entries,
                    "last_updated": datetime.utcnow().isoformat(),
                    "type": leaderboard_type
                }
                
                await self._redis.set(
                    cache_key, 
                    json.dumps(cache_data, default=str),
                    ex=settings.leaderboard_cache_duration
                )
                
        except Exception as e:
            logger.error(f"Error caching leaderboard {leaderboard_type}: {e}")
    
    async def _get_cached_leaderboard(self, leaderboard_type: str) -> Optional[List[Dict[str, Any]]]:
        """Get leaderboard from cache"""
        try:
            if self._redis:
                cache_key = f"leaderboard:{leaderboard_type}"
                cached_data = await self._redis.get(cache_key)
                
                if cached_data:
                    import json
                    data = json.loads(cached_data)
                    return data.get("entries", [])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached leaderboard {leaderboard_type}: {e}")
            return None
    
    async def get_leaderboard_stats(self) -> Dict[str, Any]:
        """Get statistics about all leaderboards"""
        await self.initialize()
        
        try:
            stats = {}
            
            # Get stats for each leaderboard type
            for lb_type in ["global", "weekly", "monthly"]:
                leaderboard_data = await self.get_leaderboard(lb_type, 10)
                entries = leaderboard_data.get("entries", [])
                
                if entries:
                    stats[lb_type] = {
                        "total_entries": len(entries),
                        "top_score": entries[0].get("score", 0) if entries else 0,
                        "average_score": sum(entry.get("score", 0) for entry in entries) // len(entries) if entries else 0,
                        "last_updated": leaderboard_data.get("last_updated")
                    }
                else:
                    stats[lb_type] = {
                        "total_entries": 0,
                        "top_score": 0,
                        "average_score": 0,
                        "last_updated": None
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting leaderboard stats: {e}")
            return {}
    
    async def update_all_leaderboards(self) -> Dict[str, bool]:
        """Update all leaderboards"""
        results = {}
        
        results["global"] = await self.update_global_leaderboard()
        results["weekly"] = await self.update_weekly_leaderboard()
        results["monthly"] = await self.update_monthly_leaderboard()
        
        return results
    
    async def clear_leaderboard_caches(self):
        """Clear all leaderboard caches"""
        try:
            if self._redis:
                keys = await self._redis.keys("leaderboard:*")
                if keys:
                    await self._redis.delete(*keys)
                    logger.info(f"Cleared {len(keys)} leaderboard caches")
                    
        except Exception as e:
            logger.error(f"Error clearing leaderboard caches: {e}")
    
    async def get_user_nearby_rankings(self, user_id: str, range_size: int = 5) -> Dict[str, Any]:
        """Get rankings around user's position"""
        await self.initialize()
        
        try:
            # Get user's current rank
            user_rank = await self._crud.get_user_rank(user_id)
            if not user_rank:
                return {"error": "User not found"}
            
            # Calculate range
            start_rank = max(1, user_rank - range_size)
            end_rank = user_rank + range_size
            
            # Get users in range
            db = await get_database()
            pipeline = [
                {"$sort": {"total_xp": -1}},
                {"$skip": start_rank - 1},
                {"$limit": (end_rank - start_rank + 1)},
                {"$project": {
                    "user_id": {"$toString": "$user_id"},
                    "username": 1,
                    "total_xp": 1,
                    "current_level": 1,
                    "total_achievements": 1
                }}
            ]
            
            cursor = db.user_gamification.aggregate(pipeline)
            nearby_users = []
            rank = start_rank
            
            async for doc in cursor:
                nearby_users.append({
                    "rank": rank,
                    "user_id": doc["user_id"],
                    "username": doc["username"],
                    "score": doc["total_xp"],
                    "level": doc["current_level"],
                    "achievements_count": doc["total_achievements"],
                    "is_current_user": doc["user_id"] == user_id
                })
                rank += 1
            
            return {
                "user_id": user_id,
                "user_rank": user_rank,
                "range": {
                    "start": start_rank,
                    "end": end_rank
                },
                "nearby_rankings": nearby_users
            }
            
        except Exception as e:
            logger.error(f"Error getting nearby rankings for user {user_id}: {e}")
            return {"error": str(e)}
