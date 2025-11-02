from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from ..models.challenge_models import (
    Challenge, UserChallenge, ChallengeType, ChallengeCategory, 
    ChallengeStatus, ChallengeDifficulty, ChallengeRequirement,
    ChallengeReward, ChallengeEvent, ChallengeStatistics
)
from ..models.gamification_models import ActivityType
from ..db.client import get_database, get_redis
from ..db.gamification_crud import GamificationCRUD
from ..utils.cache_manager import CacheManager
from ..utils.notification_client import NotificationClient

logger = logging.getLogger(__name__)

class ChallengeManager:
    """Service for managing challenges and user participation"""
    
    def __init__(self):
        self._crud = None
        self._redis = None
        self._cache_manager = None
        self._notification_client = NotificationClient()
    
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
    
    # Challenge Creation and Management
    async def create_challenge(self, challenge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new challenge"""
        await self.initialize()
        
        try:
            # Validate and process challenge data
            processed_data = await self._process_challenge_data(challenge_data)
            
            # Create challenge object
            challenge = Challenge(**processed_data)
            
            # Store in database
            db = await get_database()
            result = await db.challenges.insert_one(
                challenge.dict(by_alias=True, exclude={"id"})
            )
            
            challenge.id = result.inserted_id
            
            # Cache the challenge
            await self._cache_challenge(str(challenge.id), challenge.dict())
            
            logger.info(f"Created challenge: {challenge.title} (ID: {challenge.id})")
            
            return {
                "success": True,
                "challenge_id": str(challenge.id),
                "challenge": challenge.dict(by_alias=True),
                "message": "Challenge created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating challenge: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_challenge_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate challenge data"""
        # Set default start date if not provided
        if "start_date" not in data or not data["start_date"]:
            data["start_date"] = datetime.utcnow()
        
        # Calculate end date based on duration
        if "duration_days" in data:
            start_date = data["start_date"]
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date)
            data["end_date"] = start_date + timedelta(days=data["duration_days"])
        
        # Process requirements
        if "requirements" in data and isinstance(data["requirements"], list):
            processed_requirements = []
            for req in data["requirements"]:
                if isinstance(req, dict):
                    processed_requirements.append(ChallengeRequirement(**req))
                else:
                    processed_requirements.append(req)
            data["requirements"] = processed_requirements
        
        # Process rewards
        if "rewards" in data and isinstance(data["rewards"], dict):
            data["rewards"] = ChallengeReward(**data["rewards"])
        
        # Set status based on start date
        now = datetime.utcnow()
        if data["start_date"] > now:
            data["status"] = ChallengeStatus.UPCOMING
        elif data.get("end_date") and data["end_date"] < now:
            data["status"] = ChallengeStatus.EXPIRED
        else:
            data["status"] = ChallengeStatus.ACTIVE
        
        return data
    
    async def get_active_challenges(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all active challenges with optional filtering"""
        await self.initialize()
        
        try:
            # Build query
            query = {"status": ChallengeStatus.ACTIVE.value}
            
            if filters:
                if "category" in filters:
                    query["category"] = filters["category"]
                if "difficulty" in filters:
                    query["difficulty"] = filters["difficulty"]
                if "challenge_type" in filters:
                    query["challenge_type"] = filters["challenge_type"]
                if "required_level" in filters:
                    query["required_level"] = {"$lte": filters["required_level"]}
            
            # Get challenges from database
            db = await get_database()
            cursor = db.challenges.find(query).sort("created_at", -1)
            
            challenges = []
            async for doc in cursor:
                challenge_dict = dict(doc)
                challenge_dict["id"] = str(challenge_dict.pop("_id"))
                
                # Add participation stats
                challenge_dict["participation_stats"] = await self._get_challenge_participation_stats(
                    challenge_dict["id"]
                )
                
                challenges.append(challenge_dict)
            
            return challenges
            
        except Exception as e:
            logger.error(f"Error getting active challenges: {e}")
            return []
    
    async def get_challenge_by_id(self, challenge_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific challenge by ID"""
        await self.initialize()
        
        try:
            # Try cache first
            cached_challenge = await self._get_cached_challenge(challenge_id)
            if cached_challenge:
                return cached_challenge
            
            # Get from database
            db = await get_database()
            from bson import ObjectId
            
            challenge_doc = await db.challenges.find_one({"_id": ObjectId(challenge_id)})
            if not challenge_doc:
                return None
            
            # Process document
            challenge_dict = dict(challenge_doc)
            challenge_dict["id"] = str(challenge_dict.pop("_id"))
            
            # Add participation stats
            challenge_dict["participation_stats"] = await self._get_challenge_participation_stats(challenge_id)
            
            # Cache the result
            await self._cache_challenge(challenge_id, challenge_dict)
            
            return challenge_dict
            
        except Exception as e:
            logger.error(f"Error getting challenge {challenge_id}: {e}")
            return None
    
    # User Participation Management
    async def join_challenge(self, user_id: str, challenge_id: str) -> Dict[str, Any]:
        """Allow user to join a challenge"""
        await self.initialize()
        
        try:
            # Get challenge details
            challenge = await self.get_challenge_by_id(challenge_id)
            if not challenge:
                return {"success": False, "error": "Challenge not found"}
            
            # Check if challenge is joinable
            join_check = await self._check_challenge_joinable(user_id, challenge)
            if not join_check["can_join"]:
                return {"success": False, "error": join_check["reason"]}
            
            # Check if user already joined
            existing_participation = await self._get_user_challenge(user_id, challenge_id)
            if existing_participation:
                return {"success": False, "error": "User already participating in this challenge"}
            
            # Get user's current stats as starting values
            user_profile = await self._crud.get_user_gamification(user_id)
            start_values = await self._calculate_start_values(user_profile, challenge["requirements"])
            
            # Create participation record
            user_challenge = UserChallenge(
                user_id=user_id,
                challenge_id=challenge_id,
                start_value=start_values,
                current_progress={req["type"]: 0 for req in challenge["requirements"]}
            )
            
            # Store in database
            db = await get_database()
            result = await db.user_challenges.insert_one(
                user_challenge.dict(by_alias=True, exclude={"id"})
            )
            
            # Update challenge participant count
            await db.challenges.update_one(
                {"_id": ObjectId(challenge_id)},
                {"$inc": {"current_participants": 1}}
            )
            
            # Record event
            await self._record_challenge_event(user_id, challenge_id, "joined", {
                "joined_at": datetime.utcnow().isoformat(),
                "start_values": start_values
            })
            
            # Send notification
            await self._notification_client.send_notification({
                "user_id": user_id,
                "type": "challenge_joined",
                "title": "🎯 Challenge Joined!",
                "message": f"You've joined the challenge: {challenge['title']}",
                "data": {
                    "challenge_id": challenge_id,
                    "challenge_title": challenge["title"],
                    "duration_days": challenge["duration_days"]
                }
            })
            
            # Clear relevant caches
            await self._invalidate_user_challenge_cache(user_id)
            
            return {
                "success": True,
                "user_challenge_id": str(result.inserted_id),
                "message": "Successfully joined challenge",
                "challenge_title": challenge["title"]
            }
            
        except Exception as e:
            logger.error(f"Error joining challenge {challenge_id} for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _check_challenge_joinable(self, user_id: str, challenge: Dict[str, Any]) -> Dict[str, Any]:
        """Check if user can join a challenge"""
        try:
            # Check if challenge is active
            if challenge["status"] != ChallengeStatus.ACTIVE.value:
                return {"can_join": False, "reason": "Challenge is not active"}
            
            # Check participant limit
            if challenge.get("max_participants") and challenge["current_participants"] >= challenge["max_participants"]:
                return {"can_join": False, "reason": "Challenge is full"}
            
            # Check user level requirement
            user_profile = await self._crud.get_user_gamification(user_id)
            if not user_profile:
                return {"can_join": False, "reason": "User profile not found"}
            
            if user_profile.current_level < challenge.get("required_level", 1):
                return {"can_join": False, "reason": f"Requires level {challenge['required_level']}"}
            
            # Check required achievements
            if challenge.get("required_achievements"):
                user_achievements = await self._crud.get_user_achievements(user_id)
                user_achievement_ids = [str(ua.achievement_id) for ua in user_achievements]
                
                for required_id in challenge["required_achievements"]:
                    if required_id not in user_achievement_ids:
                        return {"can_join": False, "reason": "Missing required achievements"}
            
            return {"can_join": True, "reason": "All requirements met"}
            
        except Exception as e:
            logger.error(f"Error checking challenge joinability: {e}")
            return {"can_join": False, "reason": "Error checking requirements"}
    
    async def update_challenge_progress(self, user_id: str, challenge_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user's progress in a challenge based on activity"""
        await self.initialize()
        
        try:
            # Get user's challenge participation
            user_challenge = await self._get_user_challenge(user_id, challenge_id)
            if not user_challenge:
                return {"success": False, "error": "User not participating in challenge"}
            
            # Get challenge details
            challenge = await self.get_challenge_by_id(challenge_id)
            if not challenge:
                return {"success": False, "error": "Challenge not found"}
            
            # Calculate progress updates
            progress_updates = await self._calculate_progress_updates(
                user_challenge, challenge, activity_data
            )
            
            if not progress_updates["has_updates"]:
                return {"success": True, "message": "No progress updates needed"}
            
            # Update database
            db = await get_database()
            from bson import ObjectId
            
            update_data = {
                "current_progress": progress_updates["new_progress"],
                "progress_percentage": progress_updates["progress_percentage"],
                "daily_progress": user_challenge.get("daily_progress", []) + [progress_updates["daily_snapshot"]]
            }
            
            # Check for milestones
            if progress_updates["milestones_reached"]:
                update_data["milestones_reached"] = user_challenge.get("milestones_reached", []) + progress_updates["milestones_reached"]
            
            # Check for completion
            if progress_updates["completed"]:
                update_data["status"] = "completed"
                update_data["completed_at"] = datetime.utcnow()
                update_data["points_earned"] = challenge["rewards"]["points"]
                
                # Award challenge completion points
                await self._award_challenge_completion(user_id, challenge, progress_updates)
            
            # Update user challenge
            await db.user_challenges.update_one(
                {"user_id": ObjectId(user_id), "challenge_id": ObjectId(challenge_id)},
                {"$set": update_data}
            )
            
            # Record progress event
            await self._record_challenge_event(user_id, challenge_id, "progress_update", progress_updates)
            
            # Send notifications for milestones and completion
            if progress_updates["milestones_reached"]:
                await self._send_milestone_notifications(user_id, challenge, progress_updates["milestones_reached"])
            
            if progress_updates["completed"]:
                await self._send_completion_notification(user_id, challenge)
            
            # Clear caches
            await self._invalidate_user_challenge_cache(user_id)
            
            return {
                "success": True,
                "progress_updated": True,
                "new_progress_percentage": progress_updates["progress_percentage"],
                "milestones_reached": progress_updates["milestones_reached"],
                "completed": progress_updates["completed"]
            }
            
        except Exception as e:
            logger.error(f"Error updating challenge progress: {e}")
            return {"success": False, "error": str(e)}
    
    async def _calculate_progress_updates(self, user_challenge: Dict[str, Any], challenge: Dict[str, Any], activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate progress updates based on activity"""
        try:
            current_progress = user_challenge.get("current_progress", {})
            new_progress = current_progress.copy()
            has_updates = False
            milestones_reached = []
            
            # Process each requirement
            for requirement in challenge["requirements"]:
                req_type = requirement["type"]
                target_value = requirement["target_value"]
                
                # Calculate progress based on requirement type
                if req_type == "activity_count":
                    # Count any activity
                    new_progress[req_type] = new_progress.get(req_type, 0) + 1
                    has_updates = True
                
                elif req_type == "points_earned":
                    # Add points from activity
                    points_earned = activity_data.get("points_earned", 0)
                    new_progress[req_type] = new_progress.get(req_type, 0) + points_earned
                    has_updates = True
                
                elif req_type == "streak_days":
                    # Update streak if daily login
                    if activity_data.get("activity_type") == "daily_login":
                        user_profile = await self._crud.get_user_gamification(user_challenge["user_id"])
                        if user_profile:
                            new_progress[req_type] = user_profile.current_streak
                            has_updates = True
                
                elif req_type == "skill_category":
                    # Track skill-specific activities
                    specific_category = requirement.get("specific_criteria", {}).get("category")
                    activity_skill = activity_data.get("metadata", {}).get("skill_category")
                    
                    if specific_category and activity_skill == specific_category:
                        new_progress[req_type] = new_progress.get(req_type, 0) + 1
                        has_updates = True
                
                elif req_type == "completion_rate":
                    # Track high completion rates
                    completion_rate = activity_data.get("metadata", {}).get("completion_rate", 0)
                    min_rate = requirement.get("specific_criteria", {}).get("min_rate", 0.8)
                    
                    if completion_rate >= min_rate:
                        new_progress[req_type] = new_progress.get(req_type, 0) + 1
                        has_updates = True
            
            # Calculate overall progress percentage
            total_progress = 0
            total_requirements = len(challenge["requirements"])
            
            for requirement in challenge["requirements"]:
                req_type = requirement["type"]
                target_value = requirement["target_value"]
                current_value = new_progress.get(req_type, 0)
                
                req_progress = min(100, (current_value / target_value) * 100)
                total_progress += req_progress
            
            progress_percentage = total_progress / total_requirements if total_requirements > 0 else 0
            
            # Check for milestones (25%, 50%, 75%, 100%)
            old_percentage = user_challenge.get("progress_percentage", 0)
            milestone_thresholds = [25, 50, 75, 100]
            
            for threshold in milestone_thresholds:
                if old_percentage < threshold <= progress_percentage:
                    milestones_reached.append(f"{threshold}%")
            
            # Check for completion
            completed = progress_percentage >= 100
            
            return {
                "has_updates": has_updates,
                "new_progress": new_progress,
                "progress_percentage": progress_percentage,
                "milestones_reached": milestones_reached,
                "completed": completed,
                "daily_snapshot": {
                    "date": datetime.utcnow().isoformat(),
                    "progress": new_progress.copy(),
                    "percentage": progress_percentage
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating progress updates: {e}")
            return {"has_updates": False}
    
    async def get_user_challenges(self, user_id: str, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get all challenges for a user with optional status filter"""
        await self.initialize()
        
        try:
            # Build query
            query = {"user_id": ObjectId(user_id)}
            if status_filter:
                query["status"] = status_filter
            
            # Get user challenges
            db = await get_database()
            cursor = db.user_challenges.find(query).sort("joined_at", -1)
            
            user_challenges = []
            async for doc in cursor:
                user_challenge = dict(doc)
                user_challenge["id"] = str(user_challenge.pop("_id"))
                user_challenge["user_id"] = str(user_challenge["user_id"])
                user_challenge["challenge_id"] = str(user_challenge["challenge_id"])
                
                # Get challenge details
                challenge = await self.get_challenge_by_id(user_challenge["challenge_id"])
                if challenge:
                    user_challenge["challenge_details"] = challenge
                
                user_challenges.append(user_challenge)
            
            # Categorize challenges
            active_challenges = [uc for uc in user_challenges if uc.get("status") == "active"]
            completed_challenges = [uc for uc in user_challenges if uc.get("status") == "completed"]
            
            return {
                "success": True,
                "user_id": user_id,
                "active_challenges": active_challenges,
                "completed_challenges": completed_challenges,
                "total_active": len(active_challenges),
                "total_completed": len(completed_challenges),
                "completion_rate": len(completed_challenges) / len(user_challenges) * 100 if user_challenges else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting user challenges for {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    # Challenge Analytics and Statistics
    async def get_challenge_statistics(self, challenge_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a challenge"""
        await self.initialize()
        
        try:
            db = await get_database()
            from bson import ObjectId
            
            # Get challenge details
            challenge = await self.get_challenge_by_id(challenge_id)
            if not challenge:
                return {"error": "Challenge not found"}
            
            # Get all participants
            participants_cursor = db.user_challenges.find({"challenge_id": ObjectId(challenge_id)})
            participants = []
            async for doc in participants_cursor:
                participants.append(dict(doc))
            
            # Calculate statistics
            total_participants = len(participants)
            completed_participants = len([p for p in participants if p.get("status") == "completed"])
            active_participants = len([p for p in participants if p.get("status") == "active"])
            
            completion_rate = (completed_participants / total_participants * 100) if total_participants > 0 else 0
            
            # Calculate average completion time
            completed_times = []
            for participant in participants:
                if participant.get("status") == "completed" and participant.get("completed_at") and participant.get("joined_at"):
                    duration = participant["completed_at"] - participant["joined_at"]
                    completed_times.append(duration.total_seconds() / 3600)  # Convert to hours
            
            avg_completion_time = sum(completed_times) / len(completed_times) if completed_times else 0
            
            # Progress distribution
            progress_distribution = {"0-25%": 0, "26-50%": 0, "51-75%": 0, "76-99%": 0, "100%": 0}
            for participant in participants:
                progress = participant.get("progress_percentage", 0)
                if progress == 100:
                    progress_distribution["100%"] += 1
                elif progress >= 76:
                    progress_distribution["76-99%"] += 1
                elif progress >= 51:
                    progress_distribution["51-75%"] += 1
                elif progress >= 26:
                    progress_distribution["26-50%"] += 1
                else:
                    progress_distribution["0-25%"] += 1
            
            statistics = {
                "challenge_id": challenge_id,
                "challenge_title": challenge["title"],
                "total_participants": total_participants,
                "active_participants": active_participants,
                "completed_participants": completed_participants,
                "completion_rate": round(completion_rate, 2),
                "average_completion_time_hours": round(avg_completion_time, 2),
                "progress_distribution": progress_distribution,
                "engagement_metrics": {
                    "daily_active_rate": await self._calculate_daily_active_rate(challenge_id),
                    "milestone_completion_rate": await self._calculate_milestone_completion_rate(challenge_id)
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return {"success": True, "statistics": statistics}
            
        except Exception as e:
            logger.error(f"Error getting challenge statistics: {e}")
            return {"error": str(e)}
    
    # Utility Methods
    async def _get_user_challenge(self, user_id: str, challenge_id: str) -> Optional[Dict[str, Any]]:
        """Get user's participation in a specific challenge"""
        try:
            db = await get_database()
            from bson import ObjectId
            
            doc = await db.user_challenges.find_one({
                "user_id": ObjectId(user_id),
                "challenge_id": ObjectId(challenge_id)
            })
            
            if doc:
                result = dict(doc)
                result["id"] = str(result.pop("_id"))
                result["user_id"] = str(result["user_id"])
                result["challenge_id"] = str(result["challenge_id"])
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user challenge: {e}")
            return None
    
    async def _record_challenge_event(self, user_id: str, challenge_id: str, event_type: str, event_data: Dict[str, Any]):
        """Record a challenge-related event"""
        try:
            db = await get_database()
            from bson import ObjectId
            
            event = ChallengeEvent(
                user_id=ObjectId(user_id),
                challenge_id=ObjectId(challenge_id),
                event_type=event_type,
                event_data=event_data
            )
            
            await db.challenge_events.insert_one(
                event.dict(by_alias=True, exclude={"id"})
            )
            
        except Exception as e:
            logger.error(f"Error recording challenge event: {e}")
    
    async def _cache_challenge(self, challenge_id: str, challenge_data: Dict[str, Any]):
        """Cache challenge data"""
        try:
            if self._cache_manager:
                cache_key = f"challenge:{challenge_id}"
                await self._cache_manager._redis.set(
                    cache_key,
                    json.dumps(challenge_data, default=str),
                    ex=1800  # 30 minutes
                )
        except Exception as e:
            logger.error(f"Error caching challenge: {e}")
    
    async def _get_cached_challenge(self, challenge_id: str) -> Optional[Dict[str, Any]]:
        """Get challenge from cache"""
        try:
            if self._cache_manager:
                cache_key = f"challenge:{challenge_id}"
                cached_data = await self._cache_manager._redis.get(cache_key)
                if cached_data:
                    import json
                    return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Error getting cached challenge: {e}")
            return None
    
    async def _invalidate_user_challenge_cache(self, user_id: str):
        """Invalidate user challenge related caches"""
        try:
            if self._cache_manager:
                patterns = [
                    f"user_challenges:{user_id}",
                    f"challenge_progress:{user_id}:*"
                ]
                
                for pattern in patterns:
                    keys = await self._cache_manager._redis.keys(pattern)
                    if keys:
                        await self._cache_manager._redis.delete(*keys)
                        
        except Exception as e:
            logger.error(f"Error invalidating user challenge cache: {e}")
    
    async def _send_completion_notification(self, user_id: str, challenge: Dict[str, Any]):
        """Send challenge completion notification"""
        try:
            await self._notification_client.send_notification({
                "user_id": user_id,
                "type": "challenge_completed",
                "title": "🏆 Challenge Completed!",
                "message": f"Congratulations! You've completed the challenge: {challenge['title']}",
                "data": {
                    "challenge_id": challenge["id"],
                    "challenge_title": challenge["title"],
                    "points_earned": challenge["rewards"]["points"]
                }
            })
        except Exception as e:
            logger.error(f"Error sending completion notification: {e}")
    
    async def _award_challenge_completion(self, user_id: str, challenge: Dict[str, Any], progress_data: Dict[str, Any]):
        """Award points and rewards for challenge completion"""
        try:
            # Award points through the points calculator
            from ..services.points_calculator import PointsCalculator
            
            points_calculator = PointsCalculator()
            await points_calculator.initialize()
            
            await points_calculator.award_points(
                user_id=user_id,
                activity_type=ActivityType.ACHIEVEMENT_UNLOCK,  # Treat as achievement
                custom_points=challenge["rewards"]["points"],
                metadata={
                    "challenge_id": challenge["id"],
                    "challenge_title": challenge["title"],
                    "challenge_type": "completion"
                }
            )
            
        except Exception as e:
            logger.error(f"Error awarding challenge completion: {e}")
