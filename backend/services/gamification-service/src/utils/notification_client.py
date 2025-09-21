import httpx
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.config import settings

logger = logging.getLogger(__name__)

class NotificationClient:
    """Client for communicating with the notification service"""
    
    def __init__(self):
        self.base_url = settings.notification_service_url
        self.timeout = 10.0
        self.max_retries = 3
    
    async def send_notification(self, notification_data: Dict[str, Any]) -> bool:
        """Send notification via the notification service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare notification payload for your notification service
                payload = {
                    "user_id": notification_data.get("user_id"),
                    "type": notification_data.get("type", "gamification"),
                    "title": notification_data.get("title", "Gamification Update"),
                    "message": notification_data.get("message", ""),
                    "data": notification_data.get("data", {}),
                    "priority": notification_data.get("priority", "medium"),
                    "channels": notification_data.get("channels", ["push", "in_app"]),
                    "timestamp": datetime.utcnow().isoformat(),
                    "source_service": "gamification-service"
                }
                
                # Send to notification service
                response = await client.post(
                    f"{self.base_url}/api/v1/notifications/send",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Notification sent successfully for user {notification_data.get('user_id')}")
                    return True
                else:
                    logger.warning(f"Notification service responded with {response.status_code}: {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error("Notification service timeout")
            return False
        except httpx.ConnectError:
            logger.error("Cannot connect to notification service")
            return False
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def send_achievement_notification(self, user_id: str, achievement_data: Dict[str, Any]) -> bool:
        """Send achievement unlock notification"""
        notification_data = {
            "user_id": user_id,
            "type": "achievement_unlocked",
            "title": "🏆 Achievement Unlocked!",
            "message": f"Congratulations! You've earned '{achievement_data.get('name', 'New Achievement')}'",
            "data": {
                "achievement_id": achievement_data.get("achievement_id"),
                "achievement_name": achievement_data.get("name"),
                "points_reward": achievement_data.get("points_reward", 0),
                "category": achievement_data.get("category", "general"),
                "rarity": achievement_data.get("rarity", "common")
            },
            "priority": "high",
            "channels": ["push", "in_app"]
        }
        
        return await self.send_notification(notification_data)
    
    async def send_level_up_notification(self, user_id: str, level_data: Dict[str, Any]) -> bool:
        """Send level up notification"""
        notification_data = {
            "user_id": user_id,
            "type": "level_up",
            "title": "🚀 Level Up!",
            "message": f"Amazing! You've reached level {level_data.get('new_level', 'N/A')}",
            "data": {
                "old_level": level_data.get("old_level", 0),
                "new_level": level_data.get("new_level", 0),
                "points_earned": level_data.get("points_earned", 0),
                "total_xp": level_data.get("total_xp", 0)
            },
            "priority": "medium",
            "channels": ["push", "in_app"]
        }
        
        return await self.send_notification(notification_data)
    
    async def send_streak_notification(self, user_id: str, streak_data: Dict[str, Any]) -> bool:
        """Send streak milestone notification"""
        streak_count = streak_data.get("streak_count", 0)
        
        # Only send notifications for significant streaks
        if streak_count not in [3, 7, 14, 30, 60, 100]:
            return True  # Don't send notification, but return success
        
        # Customize message based on streak length
        if streak_count >= 100:
            emoji = "🔥🔥🔥"
            message_tone = "Incredible"
        elif streak_count >= 30:
            emoji = "🔥🔥"
            message_tone = "Outstanding"
        elif streak_count >= 7:
            emoji = "🔥"
            message_tone = "Great"
        else:
            emoji = "⚡"
            message_tone = "Nice"
        
        notification_data = {
            "user_id": user_id,
            "type": "streak_milestone",
            "title": f"{emoji} Streak Milestone!",
            "message": f"{message_tone}! You've maintained a {streak_count}-day streak!",
            "data": {
                "streak_count": streak_count,
                "streak_bonus": streak_data.get("streak_bonus", 0),
                "longest_streak": streak_data.get("longest_streak", 0)
            },
            "priority": "medium",
            "channels": ["push", "in_app"]
        }
        
        return await self.send_notification(notification_data)
    
    async def send_leaderboard_notification(self, user_id: str, leaderboard_data: Dict[str, Any]) -> bool:
        """Send leaderboard position notification"""
        rank = leaderboard_data.get("rank", 0)
        leaderboard_type = leaderboard_data.get("type", "global")
        
        # Only notify for top 10 positions or significant rank improvements
        if rank > 10:
            return True  # Don't send notification
        
        notification_data = {
            "user_id": user_id,
            "type": "leaderboard_update",
            "title": "📊 Leaderboard Update!",
            "message": f"You're now #{rank} on the {leaderboard_type} leaderboard!",
            "data": {
                "rank": rank,
                "leaderboard_type": leaderboard_type,
                "score": leaderboard_data.get("score", 0),
                "previous_rank": leaderboard_data.get("previous_rank")
            },
            "priority": "low",
            "channels": ["in_app"]
        }
        
        return await self.send_notification(notification_data)
    
    async def send_batch_notifications(self, notifications: list) -> Dict[str, Any]:
        """Send multiple notifications in batch"""
        results = {
            "total": len(notifications),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Process notifications in batches to avoid overwhelming the notification service
        batch_size = 5
        for i in range(0, len(notifications), batch_size):
            batch = notifications[i:i + batch_size]
            
            # Send batch concurrently
            tasks = [self.send_notification(notif) for notif in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results["failed"] += 1
                    results["errors"].append(f"Notification {i+j}: {str(result)}")
                elif result:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
            
            # Small delay between batches to be nice to the notification service
            if i + batch_size < len(notifications):
                await asyncio.sleep(0.1)
        
        return results
    
    async def send_daily_summary_notification(self, user_id: str, summary_data: Dict[str, Any]) -> bool:
        """Send daily activity summary notification"""
        points_earned = summary_data.get("points_earned_today", 0)
        activities_completed = summary_data.get("activities_completed", 0)
        
        # Only send if user was active
        if points_earned == 0 and activities_completed == 0:
            return True
        
        notification_data = {
            "user_id": user_id,
            "type": "daily_summary",
            "title": "📈 Your Daily Progress",
            "message": f"Today you earned {points_earned} points and completed {activities_completed} activities!",
            "data": {
                "points_earned_today": points_earned,
                "activities_completed": activities_completed,
                "current_level": summary_data.get("current_level", 1),
                "current_streak": summary_data.get("current_streak", 0)
            },
            "priority": "low",
            "channels": ["in_app", "email"]
        }
        
        return await self.send_notification(notification_data)
    
    async def health_check(self) -> bool:
        """Check if notification service is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False

# Global notification client instance
notification_client = NotificationClient()
