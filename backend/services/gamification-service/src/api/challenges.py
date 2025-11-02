from fastapi import APIRouter, HTTPException, Depends, Query, Path, BackgroundTasks, Body
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from bson import ObjectId

from ..models.challenge_models import (
    ChallengeType, ChallengeCategory, ChallengeDifficulty, ChallengeStatus,
    CreateChallengeRequest, JoinChallengeRequest, UpdateProgressRequest
)

from ..services.challenge_manager import ChallengeManager
from ..utils.cache_manager import CacheManager
from ..db.client import get_database
from ..db.gamification_crud import GamificationCRUD

logger = logging.getLogger(__name__)

# ROUTER SETUP
router = APIRouter(prefix="/api/v1/challenges", tags=["Challenges"])

# DEPENDENCIES
async def get_challenge_manager():
    manager = ChallengeManager()
    await manager.initialize()
    return manager

async def get_cache_manager():
    manager = CacheManager()
    await manager.initialize()
    return manager

async def get_crud():
    db = await get_database()
    return GamificationCRUD(db)

# GET ENDPOINTS
@router.get("/", summary="Get Available Challenges")
async def get_challenges(
    challenge_type: Optional[str] = Query(None, description="Filter by challenge type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    status: Optional[str] = Query("active", description="Filter by status"),
    user_level: Optional[int] = Query(None, description="User level for eligibility filtering"),
    limit: int = Query(20, ge=1, le=100, description="Number of challenges to return"),
    offset: int = Query(0, ge=0, description="Number of challenges to skip"),
    challenge_manager: ChallengeManager = Depends(get_challenge_manager)
):
    """Get available challenges with filtering and pagination"""
    try:
        filters = {}
        if challenge_type:
            try:
                ChallengeType(challenge_type.lower())
                filters["challenge_type"] = challenge_type.lower()
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid challenge type: {challenge_type}")

        if category:
            try:
                ChallengeCategory(category.lower())
                filters["category"] = category.lower()
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

        if difficulty:
            try:
                ChallengeDifficulty(difficulty.lower())
                filters["difficulty"] = difficulty.lower()
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid difficulty: {difficulty}")

        if user_level:
            filters["required_level"] = user_level

        challenges = await challenge_manager.get_active_challenges(filters)
        total_challenges = len(challenges)
        paginated_challenges = challenges[offset:offset + limit]

        pagination = {
            "current_page": (offset // limit) + 1 if limit > 0 else 1,
            "per_page": limit,
            "total_challenges": total_challenges,
            "total_pages": (total_challenges + limit - 1) // limit if limit > 0 else 1,
            "has_next": offset + limit < total_challenges,
            "has_previous": offset > 0
        }

        return {
            "success": True,
            "challenges": paginated_challenges,
            "pagination": pagination,
            "filters_applied": filters
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting challenges: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/featured", summary="Get Featured Challenges")
async def get_featured_challenges(
    limit: int = Query(5, ge=1, le=10, description="Number of featured challenges"),
    challenge_manager: ChallengeManager = Depends(get_challenge_manager)
):
    """Get featured challenges - popular, trending, or editor's choice"""
    try:
        all_challenges = await challenge_manager.get_active_challenges()
        
        featured = sorted(
            all_challenges,
            key=lambda x: x.get("current_participants", 0),
            reverse=True
        )[:limit]

        for i, challenge in enumerate(featured):
            if i == 0:
                challenge["featured_reason"] = "Most Popular"
            elif challenge.get("difficulty") == "expert":
                challenge["featured_reason"] = "Expert Challenge"
            elif challenge.get("challenge_type") == "special_event":
                challenge["featured_reason"] = "Special Event"
            else:
                challenge["featured_reason"] = "Trending"

        return {
            "success": True,
            "featured_challenges": featured,
            "total_featured": len(featured)
        }

    except Exception as e:
        logger.error(f"Error getting featured challenges: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{challenge_id}", summary="Get Challenge Details")
async def get_challenge_details(
    challenge_id: str = Path(..., description="Challenge ID"),
    user_id: Optional[str] = Query(None, description="User ID to include participation status"),
    challenge_manager: ChallengeManager = Depends(get_challenge_manager)
):
    """Get detailed information about a specific challenge"""
    try:
        challenge = await challenge_manager.get_challenge_by_id(challenge_id)
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")

        if user_id:
            user_participation = await challenge_manager._get_user_challenge(user_id, challenge_id)
            challenge["user_participation"] = user_participation

            if not user_participation:
                join_check = await challenge_manager._check_challenge_joinable(user_id, challenge)
                challenge["can_join"] = join_check["can_join"]
                challenge["join_requirements"] = join_check.get("reason", "")

        return {
            "success": True,
            "challenge": challenge
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting challenge details {challenge_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# POST ENDPOINTS - FIXED PARAMETER ORDER
@router.post("/{challenge_id}/join", summary="Join a Challenge")
async def join_challenge(
    challenge_id: str = Path(..., description="Challenge ID to join"),
    user_id: str = Query(..., description="User ID"),
    challenge_manager: ChallengeManager = Depends(get_challenge_manager)
):
    """Join a specific challenge"""
    try:
        result = await challenge_manager.join_challenge(user_id, challenge_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining challenge {challenge_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ✅ FIXED: Changed Query to Body for complex object
@router.post("/{challenge_id}/progress", summary="Update Challenge Progress")
async def update_challenge_progress(
    background_tasks: BackgroundTasks,
    challenge_id: str = Path(..., description="Challenge ID"),
    user_id: str = Query(..., description="User ID"),
    activity_data: Dict[str, Any] = Body(..., description="Activity data"),  # ✅ FIXED: Use Body()
    challenge_manager: ChallengeManager = Depends(get_challenge_manager)
):
    """Update user's progress in a challenge based on activity"""
    try:
        background_tasks.add_task(
            update_progress_background,
            challenge_manager,
            user_id,
            challenge_id,
            activity_data
        )

        return {
            "success": True,
            "message": "Progress update initiated",
            "challenge_id": challenge_id,
            "user_id": user_id
        }

    except Exception as e:
        logger.error(f"Error initiating progress update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/admin/create", summary="Create New Challenge (Admin)", tags=["Admin"])
async def create_challenge(
    background_tasks: BackgroundTasks,
    challenge_data: CreateChallengeRequest,
    challenge_manager: ChallengeManager = Depends(get_challenge_manager)
):
    """Create a new challenge (Admin only)"""
    try:
        result = await challenge_manager.create_challenge(challenge_data.model_dump())
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating challenge: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# BACKGROUND TASKS
async def update_progress_background(
    challenge_manager: ChallengeManager,
    user_id: str,
    challenge_id: str,
    activity_data: Dict[str, Any]
):
    """Background task to update challenge progress"""
    try:
        await challenge_manager.update_challenge_progress(user_id, challenge_id, activity_data)
    except Exception as e:
        logger.error(f"Error updating progress in background: {e}")

# UTILITY FUNCTIONS
def get_rank_suffix(rank: int) -> str:
    """Get appropriate suffix for rank number"""
    if 10 <= rank % 100 <= 20:
        return f"{rank}th"
    else:
        suffix_map = {1: "st", 2: "nd", 3: "rd"}
        return f"{rank}{suffix_map.get(rank % 10, 'th')}"

def calculate_recommendation_score(user_profile, challenge, completed_challenges) -> float:
    """Calculate recommendation score for a challenge"""
    score = 0.5
    user_level = user_profile.current_level
    required_level = challenge.get("required_level", 1)
    
    if required_level <= user_level <= required_level + 5:
        score += 0.3
    elif required_level > user_level:
        score -= 0.2
    
    return min(1.0, score)

def generate_recommendation_reason(user_profile, challenge, score) -> str:
    """Generate human-readable reason for recommendation"""
    if score >= 0.8:
        return "Perfect match for your level and interests!"
    elif score >= 0.6:
        return "Great challenge based on your activity history"
    elif score >= 0.4:
        return "Good opportunity to try something new"
    else:
        return "Recommended for skill development"
