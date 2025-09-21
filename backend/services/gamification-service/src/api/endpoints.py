from fastapi import APIRouter
from datetime import datetime
from typing import List, Dict

router = APIRouter()

@router.post("/points/award")
async def award_points(request: dict):
    """Award points to user"""
    user_id = request.get("user_id")
    action = request.get("action")
    points = request.get("points", 0)
    
    point_values = {
        "resume_upload": 50,
        "skill_assessment": 75,
        "interview_practice": 100,
        "portfolio_update": 40,
        "course_completion": 200
    }
    
    awarded_points = point_values.get(action, points)
    
    return {
        "user_id": user_id,
        "action": action,
        "points_awarded": awarded_points,
        "total_points": 1250 + awarded_points,  # Mock total
        "level": "Intermediate",
        "next_level_threshold": 2000,
        "achievement_unlocked": "Quick Learner" if awarded_points >= 100 else None,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/points/{user_id}")
async def get_user_points(user_id: str):
    """Get user points summary"""
    return {
        "user_id": user_id,
        "total_points": 1250,
        "current_level": "Intermediate",
        "level_progress": 75.5,
        "points_to_next_level": 350,
        "lifetime_points": 2100,
        "weekly_points": 275,
        "point_history": [
            {"date": "2024-09-21", "points": 100, "action": "interview_practice"},
            {"date": "2024-09-20", "points": 50, "action": "resume_upload"},
            {"date": "2024-09-19", "points": 75, "action": "skill_assessment"}
        ]
    }

@router.get("/achievements")
async def get_available_achievements():
    """Get all available achievements"""
    return {
        "achievements": [
            {
                "id": "first_steps",
                "name": "First Steps",
                "description": "Complete your first career assessment",
                "icon": "🚀",
                "points": 50,
                "rarity": "Common",
                "unlock_condition": "Complete 1 assessment"
            },
            {
                "id": "resume_master",
                "name": "Resume Master",
                "description": "Upload and optimize your resume",
                "icon": "📄",
                "points": 100,
                "rarity": "Uncommon",
                "unlock_condition": "Upload resume + get AI feedback"
            },
            {
                "id": "interview_ace",
                "name": "Interview Ace",
                "description": "Score 90+ on mock interview",
                "icon": "🎯",
                "points": 200,
                "rarity": "Rare",
                "unlock_condition": "Score 90+ in interview"
            }
        ],
        "total_achievements": 15,
        "categories": ["Career", "Skills", "Learning", "Social"]
    }

@router.get("/achievements/{user_id}")
async def get_user_achievements(user_id: str):
    """Get user's earned achievements"""
    return {
        "user_id": user_id,
        "earned_achievements": [
            {
                "id": "first_steps",
                "name": "First Steps",
                "earned_at": "2024-09-15T10:30:00Z",
                "points_earned": 50
            },
            {
                "id": "resume_master",
                "name": "Resume Master",
                "earned_at": "2024-09-18T14:20:00Z",
                "points_earned": 100
            }
        ],
        "total_earned": 2,
        "completion_percentage": 13.3,
        "next_achievement": {
            "id": "skill_explorer",
            "name": "Skill Explorer",
            "progress": 60,
            "requirement": "Complete 5 skill assessments"
        }
    }

@router.get("/leaderboard")
async def get_leaderboard():
    """Get global leaderboard"""
    return {
        "leaderboard_type": "global",
        "period": "all_time",
        "top_users": [
            {"rank": 1, "username": "TechMaster", "points": 5420, "level": "Expert"},
            {"rank": 2, "username": "CareerPro", "points": 4890, "level": "Expert"},
            {"rank": 3, "username": "SkillSeeker", "points": 4230, "level": "Advanced"},
            {"rank": 4, "username": "CodeNinja", "points": 3950, "level": "Advanced"},
            {"rank": 5, "username": "AIEnthusiast", "points": 3640, "level": "Advanced"}
        ],
        "user_rank": 15,
        "total_participants": 1247,
        "updated_at": datetime.utcnow().isoformat()
    }

@router.get("/leaderboard/weekly")
async def get_weekly_leaderboard():
    """Get weekly leaderboard"""
    return {
        "leaderboard_type": "weekly",
        "period": "current_week",
        "top_users": [
            {"rank": 1, "username": "QuickLearner", "points": 420, "weekly_growth": "+15%"},
            {"rank": 2, "username": "ConsistentUser", "points": 385, "weekly_growth": "+22%"},
            {"rank": 3, "username": "NewcomerStar", "points": 340, "weekly_growth": "+340%"}
        ],
        "week_start": "2024-09-16",
        "week_end": "2024-09-22"
    }

@router.get("/challenges")
async def get_active_challenges():
    """Get active challenges"""
    return {
        "active_challenges": [
            {
                "id": "skill_master",
                "name": "Skill Master Challenge",
                "description": "Complete 5 skill assessments this month",
                "type": "monthly",
                "progress": {"current": 2, "target": 5},
                "reward": {"points": 500, "badge": "Skill Master"},
                "ends_at": "2024-09-30T23:59:59Z"
            },
            {
                "id": "interview_warrior",
                "name": "Interview Warrior",
                "description": "Practice 3 mock interviews this week",
                "type": "weekly",
                "progress": {"current": 1, "target": 3},
                "reward": {"points": 200, "badge": "Interview Pro"},
                "ends_at": "2024-09-22T23:59:59Z"
            }
        ],
        "total_challenges": 8,
        "participation_count": 156
    }

@router.post("/challenges/join")
async def join_challenge(request: dict):
    """Join a challenge"""
    user_id = request.get("user_id")
    challenge_id = request.get("challenge_id")
    
    return {
        "user_id": user_id,
        "challenge_id": challenge_id,
        "status": "joined",
        "current_progress": 0,
        "joined_at": datetime.utcnow().isoformat(),
        "message": f"Successfully joined challenge: {challenge_id}"
    }

@router.get("/health")
async def gamification_health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "gamification-service",
        "features": ["points", "achievements", "leaderboards", "challenges"],
        "timestamp": datetime.utcnow().isoformat()
    }
