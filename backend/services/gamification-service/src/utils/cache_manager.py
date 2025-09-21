import redis.asyncio as redis
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from ..core.config import settings
from ..db.client import get_redis

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis cache management for gamification data"""
    
    def __init__(self):
        self._redis = None
        self.default_ttl = settings.redis_ttl_seconds
    
    async def initialize(self):
        """Initialize Redis connection"""
        if not self._redis:
            self._redis = await get_redis()
    
    # User Profile Caching
    async def cache_user_profile(self, user_id: str, profile_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache user gamification profile"""
        await self.initialize()
        
        try:
            cache_key = f"user_profile:{user_id}"
            cache_data = {
                **profile_data,
                "cached_at": datetime.utcnow().isoformat(),
                "cache_version": "v1"
            }
            
            ttl = ttl or self.default_ttl
            serialized_data = json.dumps(cache_data, default=str)
            
            await self._redis.set(cache_key, serialized_data, ex=ttl)
            logger.debug(f"Cached user profile for {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching user profile {user_id}: {e}")
            return False
    
    async def get_cached_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user profile"""
        await self.initialize()
        
        try:
            cache_key = f"user_profile:{user_id}"
            cached_data = await self._redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached user profile {user_id}: {e}")
            return None
    
    # Leaderboard Caching
    async def cache_leaderboard(self, leaderboard_type: str, entries: List[Dict[str, Any]], ttl: Optional[int] = None) -> bool:
        """Cache leaderboard data"""
        await self.initialize()
        
        try:
            cache_key = f"leaderboard:{leaderboard_type}"
            cache_data = {
                "entries": entries,
                "type": leaderboard_type,
                "cached_at": datetime.utcnow().isoformat(),
                "total_entries": len(entries)
            }
            
            ttl = ttl or settings.leaderboard_cache_duration
            serialized_data = json.dumps(cache_data, default=str)
            
            await self._redis.set(cache_key, serialized_data, ex=ttl)
            logger.debug(f"Cached leaderboard {leaderboard_type} with {len(entries)} entries")
            return True
            
        except Exception as e:
            logger.error(f"Error caching leaderboard {leaderboard_type}: {e}")
            return False
    
    async def get_cached_leaderboard(self, leaderboard_type: str) -> Optional[Dict[str, Any]]:
        """Get cached leaderboard"""
        await self.initialize()
        
        try:
            cache_key = f"leaderboard:{leaderboard_type}"
            cached_data = await self._redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached leaderboard {leaderboard_type}: {e}")
            return None
    
    # Achievement Caching
    async def cache_user_achievements(self, user_id: str, achievements: List[Dict[str, Any]], ttl: Optional[int] = None) -> bool:
        """Cache user achievements"""
        await self.initialize()
        
        try:
            cache_key = f"user_achievements:{user_id}"
            cache_data = {
                "achievements": achievements,
                "count": len(achievements),
                "cached_at": datetime.utcnow().isoformat()
            }
            
            ttl = ttl or self.default_ttl
            serialized_data = json.dumps(cache_data, default=str)
            
            await self._redis.set(cache_key, serialized_data, ex=ttl)
            return True
            
        except Exception as e:
            logger.error(f"Error caching user achievements {user_id}: {e}")
            return False
    
    async def get_cached_user_achievements(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached user achievements"""
        await self.initialize()
        
        try:
            cache_key = f"user_achievements:{user_id}"
            cached_data = await self._redis.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                return data.get("achievements", [])
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached user achievements {user_id}: {e}")
            return None
    
    # Activity Tracking Cache
    async def cache_recent_activity(self, user_id: str, activity_data: Dict[str, Any]) -> bool:
        """Cache recent user activity"""
        await self.initialize()
        
        try:
            cache_key = f"recent_activity:{user_id}"
            
            # Get existing activities
            existing_data = await self._redis.get(cache_key)
            if existing_data:
                activities = json.loads(existing_data)
            else:
                activities = []
            
            # Add new activity at the beginning
            activity_with_timestamp = {
                **activity_data,
                "cached_at": datetime.utcnow().isoformat()
            }
            activities.insert(0, activity_with_timestamp)
            
            # Keep only recent 20 activities
            activities = activities[:20]
            
            # Cache updated activities
            serialized_data = json.dumps(activities, default=str)
            await self._redis.set(cache_key, serialized_data, ex=3600)  # 1 hour TTL
            
            return True
            
        except Exception as e:
            logger.error(f"Error caching recent activity for {user_id}: {e}")
            return False
    
    async def get_cached_recent_activities(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get cached recent activities"""
        await self.initialize()
        
        try:
            cache_key = f"recent_activity:{user_id}"
            cached_data = await self._redis.get(cache_key)
            
            if cached_data:
                activities = json.loads(cached_data)
                return activities[:limit]
            return []
            
        except Exception as e:
            logger.error(f"Error getting cached activities {user_id}: {e}")
            return []
    
    # Statistics Caching
    async def cache_user_stats(self, user_id: str, stats_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache user statistics"""
        await self.initialize()
        
        try:
            cache_key = f"user_stats:{user_id}"
            cache_data = {
                **stats_data,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            ttl = ttl or 1800  # 30 minutes default for stats
            serialized_data = json.dumps(cache_data, default=str)
            
            await self._redis.set(cache_key, serialized_data, ex=ttl)
            return True
            
        except Exception as e:
            logger.error(f"Error caching user stats {user_id}: {e}")
            return False
    
    async def get_cached_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user statistics"""
        await self.initialize()
        
        try:
            cache_key = f"user_stats:{user_id}"
            cached_data = await self._redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached user stats {user_id}: {e}")
            return None
    
    # System-wide Caching
    async def cache_global_stats(self, stats_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache global gamification statistics"""
        await self.initialize()
        
        try:
            cache_key = "global_gamification_stats"
            cache_data = {
                **stats_data,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            ttl = ttl or 900  # 15 minutes default for global stats
            serialized_data = json.dumps(cache_data, default=str)
            
            await self._redis.set(cache_key, serialized_data, ex=ttl)
            return True
            
        except Exception as e:
            logger.error(f"Error caching global stats: {e}")
            return False
    
    async def get_cached_global_stats(self) -> Optional[Dict[str, Any]]:
        """Get cached global statistics"""
        await self.initialize()
        
        try:
            cache_key = "global_gamification_stats"
            cached_data = await self._redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached global stats: {e}")
            return None
    
    # Cache Management Utilities
    async def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cached data for a user"""
        await self.initialize()
        
        try:
            patterns = [
                f"user_profile:{user_id}",
                f"user_achievements:{user_id}",
                f"user_stats:{user_id}",
                f"recent_activity:{user_id}",
                f"user_summary:{user_id}"
            ]
            
            for pattern in patterns:
                await self._redis.delete(pattern)
            
            logger.info(f"Invalidated cache for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating user cache {user_id}: {e}")
            return False
    
    async def invalidate_leaderboard_caches(self) -> bool:
        """Invalidate all leaderboard caches"""
        await self.initialize()
        
        try:
            # Get all leaderboard cache keys
            keys = await self._redis.keys("leaderboard:*")
            
            if keys:
                await self._redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} leaderboard caches")
            
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating leaderboard caches: {e}")
            return False
    
    async def set_rate_limit(self, key: str, limit: int, window_seconds: int) -> bool:
        """Set rate limit using Redis"""
        await self.initialize()
        
        try:
            current_count = await self._redis.incr(key)
            
            if current_count == 1:
                # First request in window, set expiry
                await self._redis.expire(key, window_seconds)
            
            return current_count <= limit
            
        except Exception as e:
            logger.error(f"Error setting rate limit for {key}: {e}")
            return False
    
    async def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics and information"""
        await self.initialize()
        
        try:
            info = await self._redis.info("memory")
            keyspace = await self._redis.info("keyspace")
            
            # Count keys by pattern
            patterns = {
                "user_profiles": "user_profile:*",
                "leaderboards": "leaderboard:*",
                "user_achievements": "user_achievements:*",
                "user_stats": "user_stats:*",
                "recent_activities": "recent_activity:*"
            }
            
            key_counts = {}
            for name, pattern in patterns.items():
                keys = await self._redis.keys(pattern)
                key_counts[name] = len(keys)
            
            return {
                "memory_usage": info.get("used_memory_human", "N/A"),
                "total_keys": sum(key_counts.values()),
                "key_breakdown": key_counts,
                "keyspace_info": keyspace,
                "redis_version": info.get("redis_version", "N/A")
            }
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_keys(self) -> Dict[str, Any]:
        """Cleanup expired keys and optimize cache"""
        await self.initialize()
        
        try:
            # Get current key count
            initial_count = await self._redis.dbsize()
            
            # Run cleanup commands
            await self._redis.flushall()  # Use with caution in production
            
            # Get final count
            final_count = await self._redis.dbsize()
            
            return {
                "initial_keys": initial_count,
                "final_keys": final_count,
                "keys_cleaned": initial_count - final_count,
                "cleanup_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return {"error": str(e)}

# Global cache manager instance
cache_manager = CacheManager()
