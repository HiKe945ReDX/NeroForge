from typing import Dict, Tuple
import logging
from datetime import datetime
from ..core.config import settings
from ..models.gamification_models import ActivityType

logger = logging.getLogger(__name__)

class PointsEngine:
    """Core engine for calculating points and levels"""
    
    def __init__(self):
        self.points_config = settings.points_config
        self.level_up_threshold = settings.level_up_threshold
        self.max_level = settings.max_level
        self.daily_streak_bonus = settings.daily_streak_bonus
    
    def calculate_points(self, activity_type: ActivityType, metadata: Dict) -> int:
        """Calculate points for an activity"""
        try:
            # Base points from configuration
            base_points = self.points_config.get(activity_type.value, 50)
            
            # Apply multipliers based on metadata
            multiplier = 1.0
            
            # Completion rate multiplier for assessments/courses
            if "completion_rate" in metadata:
                completion_rate = float(metadata["completion_rate"])
                multiplier = max(0.5, completion_rate)  # Minimum 50% of points
            
            # Difficulty multiplier
            if "difficulty" in metadata:
                difficulty_multipliers = {
                    "easy": 1.0,
                    "medium": 1.2,
                    "hard": 1.5,
                    "expert": 2.0
                }
                difficulty_multiplier = difficulty_multipliers.get(metadata["difficulty"].lower(), 1.0)
                multiplier *= difficulty_multiplier
            
            # First-time completion bonus
            if metadata.get("first_time_completion", False):
                multiplier *= 1.5
            
            final_points = int(base_points * multiplier)
            
            logger.info(f"Calculated {final_points} points for {activity_type.value} (base: {base_points}, multiplier: {multiplier})")
            return final_points
            
        except Exception as e:
            logger.error(f"Error calculating points for {activity_type}: {e}")
            return self.points_config.get("default", 25)  # Fallback points
    
    def calculate_level(self, total_xp: int) -> Tuple[int, int]:
        """Calculate current level and XP needed for next level"""
        if total_xp <= 0:
            return 1, self.level_up_threshold
        
        # Calculate level based on XP thresholds
        current_level = min(int(total_xp / self.level_up_threshold) + 1, self.max_level)
        
        # XP needed for next level
        if current_level >= self.max_level:
            xp_to_next_level = 0  # Max level reached
        else:
            xp_for_current_level = (current_level - 1) * self.level_up_threshold
            xp_to_next_level = (current_level * self.level_up_threshold) - total_xp
        
        return current_level, max(0, xp_to_next_level)
    
    def check_level_up(self, old_level: int, new_level: int) -> bool:
        """Check if user leveled up"""
        return new_level > old_level
    
    def calculate_streak_bonus(self, current_streak: int) -> int:
        """Calculate bonus points for daily streak"""
        if current_streak <= 1:
            return 0
        
        # Bonus increases with streak length
        if current_streak <= 7:
            return self.daily_streak_bonus
        elif current_streak <= 30:
            return int(self.daily_streak_bonus * 1.5)
        elif current_streak <= 100:
            return int(self.daily_streak_bonus * 2.0)
        else:
            return int(self.daily_streak_bonus * 2.5)  # Max bonus
    
    def get_level_info(self, level: int) -> Dict:
        """Get information about a specific level"""
        if level <= 0:
            level = 1
        elif level > self.max_level:
            level = self.max_level
        
        xp_required = (level - 1) * self.level_up_threshold
        
        return {
            "level": level,
            "xp_required": xp_required,
            "xp_for_next_level": self.level_up_threshold if level < self.max_level else 0,
            "is_max_level": level >= self.max_level,
            "title": self._get_level_title(level)
        }
    
    def _get_level_title(self, level: int) -> str:
        """Get title/rank for a level"""
        if level >= 90:
            return "Grandmaster"
        elif level >= 80:
            return "Master"
        elif level >= 70:
            return "Expert"
        elif level >= 60:
            return "Advanced"
        elif level >= 50:
            return "Proficient"
        elif level >= 40:
            return "Skilled"
        elif level >= 30:
            return "Competent"
        elif level >= 20:
            return "Intermediate"
        elif level >= 10:
            return "Beginner"
        else:
            return "Novice"
    
    def get_points_breakdown(self, activity_type: ActivityType, metadata: Dict) -> Dict:
        """Get detailed breakdown of point calculation"""
        base_points = self.points_config.get(activity_type.value, 50)
        breakdown = {
            "activity_type": activity_type.value,
            "base_points": base_points,
            "multipliers": [],
            "total_multiplier": 1.0,
            "final_points": base_points
        }
        
        # Apply and track multipliers
        total_multiplier = 1.0
        
        if "completion_rate" in metadata:
            completion_rate = float(metadata["completion_rate"])
            multiplier = max(0.5, completion_rate)
            breakdown["multipliers"].append({
                "type": "completion_rate",
                "value": completion_rate,
                "multiplier": multiplier
            })
            total_multiplier *= multiplier
        
        if "difficulty" in metadata:
            difficulty_multipliers = {
                "easy": 1.0,
                "medium": 1.2,
                "hard": 1.5,
                "expert": 2.0
            }
            difficulty_multiplier = difficulty_multipliers.get(metadata["difficulty"].lower(), 1.0)
            breakdown["multipliers"].append({
                "type": "difficulty",
                "value": metadata["difficulty"],
                "multiplier": difficulty_multiplier
            })
            total_multiplier *= difficulty_multiplier
        
        if metadata.get("first_time_completion", False):
            breakdown["multipliers"].append({
                "type": "first_time_bonus",
                "value": True,
                "multiplier": 1.5
            })
            total_multiplier *= 1.5
        
        breakdown["total_multiplier"] = total_multiplier
        breakdown["final_points"] = int(base_points * total_multiplier)
        
        return breakdown
