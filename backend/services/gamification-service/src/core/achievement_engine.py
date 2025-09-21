from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from ..models.gamification_models import Achievement, UserGamification, ActivityType, AchievementCategory

logger = logging.getLogger(__name__)

class AchievementEngine:
    """Core engine for achievement unlock logic and criteria checking"""
    
    @staticmethod
    def evaluate_achievement_criteria(
        achievement: Achievement,
        user_profile: UserGamification,
        user_activities: List[Dict[str, Any]],
        current_activity: Optional[ActivityType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate if user meets achievement criteria
        Returns: (should_unlock: bool, evaluation_details: dict)
        """
        try:
            criteria = achievement.unlock_criteria
            evaluation_details = {
                "achievement_id": str(achievement.id),
                "achievement_name": achievement.name,
                "criteria_type": criteria.type,
                "threshold": criteria.threshold,
                "current_value": 0,
                "progress_percentage": 0,
                "meets_criteria": False
            }
            
            # Activity count based achievements
            if criteria.type == "activity_count":
                current_value = AchievementEngine._count_activities(
                    user_activities, criteria.specific_action
                )
                evaluation_details["current_value"] = current_value
                meets_criteria = current_value >= criteria.threshold
            
            # Streak based achievements
            elif criteria.type == "streak":
                current_value = user_profile.current_streak
                evaluation_details["current_value"] = current_value
                meets_criteria = current_value >= criteria.threshold
            
            # Level based achievements
            elif criteria.type == "level":
                current_value = user_profile.current_level
                evaluation_details["current_value"] = current_value
                meets_criteria = current_value >= criteria.threshold
            
            # Points based achievements
            elif criteria.type == "points":
                if criteria.specific_action and criteria.specific_action.startswith("skill_"):
                    # Skill-specific points
                    skill_category = criteria.specific_action.replace("skill_", "")
                    current_value = getattr(user_profile.skill_points, skill_category, 0)
                else:
                    # Total XP
                    current_value = user_profile.total_xp
                
                evaluation_details["current_value"] = current_value
                meets_criteria = current_value >= criteria.threshold
            
            # Completion based achievements
            elif criteria.type == "completion":
                current_value, meets_criteria = AchievementEngine._evaluate_completion_criteria(
                    criteria, user_profile
                )
                evaluation_details["current_value"] = current_value
            
            # Time-based achievements
            elif criteria.type == "time_active":
                if user_profile.created_at:
                    days_active = (datetime.utcnow() - user_profile.created_at).days
                    current_value = days_active
                    evaluation_details["current_value"] = current_value
                    meets_criteria = days_active >= criteria.threshold
                else:
                    meets_criteria = False
            
            # Special achievements
            elif criteria.type == "special":
                current_value, meets_criteria = AchievementEngine._evaluate_special_criteria(
                    criteria, user_profile, user_activities, current_activity, metadata
                )
                evaluation_details["current_value"] = current_value
            
            else:
                logger.warning(f"Unknown criteria type: {criteria.type}")
                meets_criteria = False
            
            # Calculate progress percentage
            if criteria.threshold > 0:
                progress = min(100, (current_value / criteria.threshold) * 100)
                evaluation_details["progress_percentage"] = round(progress, 1)
            
            evaluation_details["meets_criteria"] = meets_criteria
            
            return meets_criteria, evaluation_details
            
        except Exception as e:
            logger.error(f"Error evaluating achievement criteria: {e}")
            return False, {"error": str(e)}
    
    @staticmethod
    def _count_activities(activities: List[Dict[str, Any]], specific_action: Optional[str] = None) -> int:
        """Count activities based on criteria"""
        if not activities:
            return 0
        
        if specific_action:
            # Count specific activity type
            return sum(1 for activity in activities 
                      if activity.get("activity_type") == specific_action)
        else:
            # Count all activities
            return len(activities)
    
    @staticmethod
    def _evaluate_completion_criteria(criteria: Any, user_profile: UserGamification) -> Tuple[int, bool]:
        """Evaluate completion-based criteria"""
        if criteria.specific_action == "profile_completion":
            current_value = int(user_profile.progress_tracking.profile_completeness * 100)
            meets_criteria = user_profile.progress_tracking.profile_completeness >= (criteria.threshold / 100.0)
        
        elif criteria.specific_action == "career_path_completion":
            current_value = int(user_profile.progress_tracking.career_path_completion * 100)
            meets_criteria = user_profile.progress_tracking.career_path_completion >= (criteria.threshold / 100.0)
        
        elif criteria.specific_action == "courses":
            current_value = user_profile.progress_tracking.courses_completed
            meets_criteria = current_value >= criteria.threshold
        
        elif criteria.specific_action == "goals":
            current_value = user_profile.progress_tracking.goals_completed
            meets_criteria = current_value >= criteria.threshold
        
        else:
            current_value = 0
            meets_criteria = False
        
        return current_value, meets_criteria
    
    @staticmethod
    def _evaluate_special_criteria(
        criteria: Any,
        user_profile: UserGamification,
        user_activities: List[Dict[str, Any]],
        current_activity: Optional[ActivityType],
        metadata: Optional[Dict[str, Any]]
    ) -> Tuple[int, bool]:
        """Evaluate special achievement criteria"""
        
        if criteria.specific_action == "first_day_completion":
            # Multiple activities on first day
            if user_profile.created_at and user_profile.created_at.date() == datetime.utcnow().date():
                current_value = user_profile.total_activities
                meets_criteria = current_value >= criteria.threshold
            else:
                current_value = 0
                meets_criteria = False
        
        elif criteria.specific_action == "weekend_warrior":
            # Activities on weekends
            weekend_count = sum(1 for activity in user_activities 
                              if datetime.fromisoformat(activity.get("timestamp", "")).weekday() in [5, 6])
            current_value = weekend_count
            meets_criteria = weekend_count >= criteria.threshold
        
        elif criteria.specific_action == "early_bird":
            # Activities before 8 AM
            early_count = sum(1 for activity in user_activities 
                            if datetime.fromisoformat(activity.get("timestamp", "")).hour < 8)
            current_value = early_count
            meets_criteria = early_count >= criteria.threshold
        
        elif criteria.specific_action == "perfectionist":
            # High completion rates
            perfect_count = sum(1 for activity in user_activities 
                              if activity.get("metadata", {}).get("completion_rate", 0) >= 0.95)
            current_value = perfect_count
            meets_criteria = perfect_count >= criteria.threshold
        
        elif criteria.specific_action == "night_owl":
            # Activities after 10 PM
            late_count = sum(1 for activity in user_activities 
                           if datetime.fromisoformat(activity.get("timestamp", "")).hour >= 22)
            current_value = late_count
            meets_criteria = late_count >= criteria.threshold
        
        elif criteria.specific_action == "consistency_master":
            # Activities for consecutive days
            consecutive_days = AchievementEngine._calculate_consecutive_days(user_activities)
            current_value = consecutive_days
            meets_criteria = consecutive_days >= criteria.threshold
        
        else:
            current_value = 0
            meets_criteria = False
        
        return current_value, meets_criteria
    
    @staticmethod
    def _calculate_consecutive_days(activities: List[Dict[str, Any]]) -> int:
        """Calculate consecutive days with activities"""
        if not activities:
            return 0
        
        # Group activities by date
        activity_dates = set()
        for activity in activities:
            try:
                activity_date = datetime.fromisoformat(activity.get("timestamp", "")).date()
                activity_dates.add(activity_date)
            except:
                continue
        
        if not activity_dates:
            return 0
        
        # Sort dates
        sorted_dates = sorted(activity_dates, reverse=True)
        
        # Count consecutive days from most recent
        consecutive_count = 1
        current_date = sorted_dates[0]
        
        for i in range(1, len(sorted_dates)):
            expected_date = current_date - timedelta(days=i)
            if sorted_dates[i] == expected_date:
                consecutive_count += 1
            else:
                break
        
        return consecutive_count
    
    @staticmethod
    def prioritize_achievements(achievements: List[Achievement]) -> List[Achievement]:
        """Prioritize achievements for checking (most important first)"""
        def priority_score(achievement: Achievement) -> int:
            """Calculate priority score for achievement"""
            score = 0
            
            # Category priority
            category_scores = {
                AchievementCategory.MILESTONE: 100,
                AchievementCategory.LEARNING: 80,
                AchievementCategory.CAREER: 70,
                AchievementCategory.SPECIAL: 60,
                AchievementCategory.SOCIAL: 50
            }
            score += category_scores.get(achievement.category, 0)
            
            # Rarity priority (rarer = higher priority)
            rarity_scores = {
                "legendary": 50,
                "epic": 40,
                "rare": 30,
                "uncommon": 20,
                "common": 10
            }
            score += rarity_scores.get(achievement.rarity, 0)
            
            # Points reward priority
            score += min(achievement.points_reward // 10, 50)
            
            return score
        
        return sorted(achievements, key=priority_score, reverse=True)
    
    @staticmethod
    def get_achievement_difficulty(achievement: Achievement) -> str:
        """Determine achievement difficulty level"""
        criteria = achievement.unlock_criteria
        
        # Base difficulty on criteria type and threshold
        if criteria.type == "streak":
            if criteria.threshold >= 30:
                return "very_hard"
            elif criteria.threshold >= 14:
                return "hard"
            elif criteria.threshold >= 7:
                return "medium"
            else:
                return "easy"
        
        elif criteria.type == "level":
            if criteria.threshold >= 50:
                return "very_hard"
            elif criteria.threshold >= 25:
                return "hard"
            elif criteria.threshold >= 10:
                return "medium"
            else:
                return "easy"
        
        elif criteria.type == "points":
            if criteria.threshold >= 10000:
                return "very_hard"
            elif criteria.threshold >= 5000:
                return "hard"
            elif criteria.threshold >= 1000:
                return "medium"
            else:
                return "easy"
        
        elif criteria.type == "activity_count":
            if criteria.threshold >= 100:
                return "very_hard"
            elif criteria.threshold >= 50:
                return "hard"
            elif criteria.threshold >= 20:
                return "medium"
            else:
                return "easy"
        
        elif criteria.type == "special":
            return "hard"  # Special achievements are generally harder
        
        else:
            return "medium"  # Default
    
    @staticmethod
    def suggest_next_achievements(
        user_profile: UserGamification,
        all_achievements: List[Achievement],
        unlocked_achievements: List[str],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Suggest next achievements user should work towards"""
        
        # Filter out already unlocked achievements
        available_achievements = [
            ach for ach in all_achievements 
            if str(ach.id) not in unlocked_achievements
        ]
        
        suggestions = []
        
        for achievement in available_achievements:
            # Calculate progress (simplified)
            criteria = achievement.unlock_criteria
            progress = 0
            
            if criteria.type == "level":
                progress = min(100, (user_profile.current_level / criteria.threshold) * 100)
            elif criteria.type == "points":
                progress = min(100, (user_profile.total_xp / criteria.threshold) * 100)
            elif criteria.type == "streak":
                progress = min(100, (user_profile.current_streak / criteria.threshold) * 100)
            
            # Only suggest achievements with some progress or that are achievable
            if progress >= 10 or AchievementEngine.get_achievement_difficulty(achievement) == "easy":
                suggestions.append({
                    "achievement": {
                        "id": str(achievement.id),
                        "name": achievement.name,
                        "description": achievement.description,
                        "category": achievement.category.value,
                        "points_reward": achievement.points_reward,
                        "rarity": achievement.rarity
                    },
                    "progress": round(progress, 1),
                    "difficulty": AchievementEngine.get_achievement_difficulty(achievement),
                    "estimated_effort": AchievementEngine._estimate_effort(achievement, user_profile)
                })
        
        # Sort by progress (highest first) and limit results
        suggestions.sort(key=lambda x: x["progress"], reverse=True)
        return suggestions[:limit]
    
    @staticmethod
    def _estimate_effort(achievement: Achievement, user_profile: UserGamification) -> str:
        """Estimate effort required to unlock achievement"""
        criteria = achievement.unlock_criteria
        
        if criteria.type == "level":
            levels_needed = max(0, criteria.threshold - user_profile.current_level)
            if levels_needed == 0:
                return "immediate"
            elif levels_needed <= 2:
                return "low"
            elif levels_needed <= 5:
                return "medium"
            else:
                return "high"
        
        elif criteria.type == "streak":
            days_needed = max(0, criteria.threshold - user_profile.current_streak)
            if days_needed == 0:
                return "immediate"
            elif days_needed <= 3:
                return "low"
            elif days_needed <= 7:
                return "medium"
            else:
                return "high"
        
        elif criteria.type == "points":
            points_needed = max(0, criteria.threshold - user_profile.total_xp)
            if points_needed == 0:
                return "immediate"
            elif points_needed <= 500:
                return "low"
            elif points_needed <= 2000:
                return "medium"
            else:
                return "high"
        
        return "medium"  # Default
