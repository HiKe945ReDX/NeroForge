from fastapi import APIRouter, HTTPException, Depends, Query, Path, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from ..models.gamification_models import Achievement, AchievementCategory
from ..services.achievement_service import AchievementService
from ..services.progress_tracker import ProgressTracker
from ..utils.cache_manager import CacheManager
from ..db.client import get_database
from ..db.gamification_crud import GamificationCRUD

logger = logging.getLogger(__name__)

# Initialize router with prefix and tags
router = APIRouter(prefix="/api/v1/achievements", tags=["Achievements"])

# Service dependencies
async def get_achievement_service():
    service = AchievementService()
    await service.initialize()
    return service

async def get_progress_tracker():
    tracker = ProgressTracker()
    await tracker.initialize()
    return tracker

async def get_cache_manager():
    manager = CacheManager()
    await manager.initialize()
    return manager

async def get_crud():
    db = await get_database()
    return GamificationCRUD(db)

# Achievement Discovery Endpoints
@router.get("/", summary="Get All Achievements", response_model=Dict[str, Any])
async def get_all_achievements(
    category: Optional[str] = Query(None, description="Filter by category (learning, career, milestone, special)"),
    rarity: Optional[str] = Query(None, description="Filter by rarity (common, rare, epic, legendary)"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of achievements to return"),
    crud: GamificationCRUD = Depends(get_crud)
):
    """
    Get all available achievements with optional filtering
    
    - **category**: Filter achievements by category
    - **rarity**: Filter achievements by rarity level
    - **limit**: Maximum number of results to return
    """
    try:
        # Get all achievements
        all_achievements = await crud.get_all_achievements()
        
        # Apply filters
        filtered_achievements = all_achievements
        
        if category:
            try:
                category_enum = AchievementCategory(category.lower())
                filtered_achievements = [ach for ach in filtered_achievements if ach.category == category_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        if rarity:
            valid_rarities = ["common", "uncommon", "rare", "epic", "legendary"]
            if rarity.lower() not in valid_rarities:
                raise HTTPException(status_code=400, detail=f"Invalid rarity. Must be one of: {valid_rarities}")
            filtered_achievements = [ach for ach in filtered_achievements if ach.rarity.lower() == rarity.lower()]
        
        # Apply limit
        filtered_achievements = filtered_achievements[:limit]
        
        # Format response
        achievements_data = []
        for achievement in filtered_achievements:
            achievements_data.append({
                "id": str(achievement.id),
                "name": achievement.name,
                "description": achievement.description,
                "category": achievement.category.value,
                "points_reward": achievement.points_reward,
                "rarity": achievement.rarity,
                "icon_url": achievement.icon_url,
                "unlock_count": achievement.unlock_count,
                "unlock_percentage": achievement.unlock_percentage,
                "unlock_criteria": {
                    "type": achievement.unlock_criteria.type,
                    "threshold": achievement.unlock_criteria.threshold,
                    "specific_action": achievement.unlock_criteria.specific_action
                },
                "is_active": achievement.is_active,
                "created_at": achievement.created_at.isoformat()
            })
        
        return {
            "success": True,
            "total_achievements": len(achievements_data),
            "filters_applied": {
                "category": category,
                "rarity": rarity,
                "limit": limit
            },
            "data": achievements_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/categories", summary="Get Achievement Categories")
async def get_achievement_categories():
    """Get all available achievement categories with descriptions"""
    try:
        categories = {
            "learning": {
                "name": "Learning",
                "description": "Achievements related to course completion and skill development",
                "icon": "🎓"
            },
            "career": {
                "name": "Career",
                "description": "Achievements related to career progress and professional development",
                "icon": "💼"
            },
            "milestone": {
                "name": "Milestone",
                "description": "Achievements for reaching significant milestones",
                "icon": "🏆"
            },
            "special": {
                "name": "Special",
                "description": "Unique achievements with special unlock conditions",
                "icon": "⭐"
            },
            "social": {
                "name": "Social",
                "description": "Achievements related to community and collaboration",
                "icon": "👥"
            }
        }
        
        return {
            "success": True,
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error getting achievement categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User-Specific Achievement Endpoints
@router.get("/user/{user_id}", summary="Get User's Achievements")
async def get_user_achievements(
    user_id: str = Path(..., description="User ID"),
    include_details: bool = Query(True, description="Include detailed achievement information"),
    cache_manager: CacheManager = Depends(get_cache_manager),
    crud: GamificationCRUD = Depends(get_crud)
):
    """
    Get all achievements unlocked by a specific user
    
    - **user_id**: The ID of the user
    - **include_details**: Whether to include detailed achievement information
    """
    try:
        # Try cache first if details not required
        if not include_details:
            cached_achievements = await cache_manager.get_cached_user_achievements(user_id)
            if cached_achievements:
                return {
                    "success": True,
                    "user_id": user_id,
                    "total_unlocked": len(cached_achievements),
                    "data": cached_achievements,
                    "cached": True
                }
        
        # Get user achievements from database
        user_achievements = await crud.get_user_achievements(user_id)
        
        if not include_details:
            # Simple format
            achievements_data = [
                {
                    "achievement_id": str(ua.achievement_id),
                    "unlocked_at": ua.unlocked_at.isoformat(),
                    "points_earned": ua.points_earned
                }
                for ua in user_achievements
            ]
        else:
            # Detailed format - get full achievement info
            all_achievements = await crud.get_all_achievements()
            achievement_dict = {str(ach.id): ach for ach in all_achievements}
            
            achievements_data = []
            for ua in user_achievements:
                achievement_id = str(ua.achievement_id)
                if achievement_id in achievement_dict:
                    ach = achievement_dict[achievement_id]
                    achievements_data.append({
                        "achievement_id": achievement_id,
                        "name": ach.name,
                        "description": ach.description,
                        "category": ach.category.value,
                        "rarity": ach.rarity,
                        "icon_url": ach.icon_url,
                        "points_earned": ua.points_earned,
                        "unlocked_at": ua.unlocked_at.isoformat()
                    })
        
        # Cache simple format
        if not include_details:
            await cache_manager.cache_user_achievements(user_id, achievements_data)
        
        return {
            "success": True,
            "user_id": user_id,
            "total_unlocked": len(achievements_data),
            "data": achievements_data,
            "cached": False,
            "include_details": include_details
        }
        
    except Exception as e:
        logger.error(f"Error getting user achievements for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}/progress", summary="Get User's Achievement Progress")
async def get_user_achievement_progress(
    user_id: str = Path(..., description="User ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    show_completed: bool = Query(True, description="Include completed achievements"),
    achievement_service: AchievementService = Depends(get_achievement_service)
):
    """
    Get user's progress towards all achievements with completion percentages
    
    - **user_id**: The ID of the user
    - **category**: Filter achievements by category
    - **show_completed**: Whether to include already unlocked achievements
    """
    try:
        # Get comprehensive progress data
        progress_data = await achievement_service.get_user_achievement_progress(user_id)
        
        if "error" in progress_data:
            raise HTTPException(status_code=404, detail=progress_data["error"])
        
        # Apply filters
        filtered_achievements = progress_data["achievements"]
        
        if category:
            filtered_achievements = [ach for ach in filtered_achievements if ach["category"] == category.lower()]
        
        if not show_completed:
            filtered_achievements = [ach for ach in filtered_achievements if not ach["unlocked"]]
        
        # Sort by progress (unlocked first, then by progress percentage)
        filtered_achievements.sort(key=lambda x: (not x["unlocked"], -x["progress"]))
        
        return {
            "success": True,
            "user_id": user_id,
            "summary": {
                "total_achievements": progress_data["total_achievements"],
                "unlocked_count": progress_data["unlocked_count"],
                "completion_percentage": progress_data["completion_percentage"],
                "filtered_count": len(filtered_achievements)
            },
            "filters": {
                "category": category,
                "show_completed": show_completed
            },
            "achievements": filtered_achievements
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting achievement progress for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}/suggestions", summary="Get Achievement Suggestions")
async def get_achievement_suggestions(
    user_id: str = Path(..., description="User ID"),
    limit: int = Query(5, ge=1, le=10, description="Number of suggestions to return"),
    achievement_service: AchievementService = Depends(get_achievement_service),
    crud: GamificationCRUD = Depends(get_crud)
):
    """
    Get personalized achievement suggestions for the user
    
    - **user_id**: The ID of the user
    - **limit**: Maximum number of suggestions to return
    """
    try:
        # Get user profile
        user_profile = await crud.get_user_gamification(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get all achievements and user's unlocked achievements
        all_achievements = await crud.get_all_achievements()
        user_achievements = await crud.get_user_achievements(user_id)
        unlocked_ids = [str(ua.achievement_id) for ua in user_achievements]
        
        # Get suggestions using achievement engine
        from ..core.achievement_engine import AchievementEngine
        suggestions = AchievementEngine.suggest_next_achievements(
            user_profile, all_achievements, unlocked_ids, limit
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "user_level": user_profile.current_level,
            "user_xp": user_profile.total_xp,
            "suggestions_count": len(suggestions),
            "suggestions": suggestions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting achievement suggestions for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Achievement Analytics Endpoints
@router.get("/stats/global", summary="Get Global Achievement Statistics")
async def get_global_achievement_stats(
    crud: GamificationCRUD = Depends(get_crud)
):
    """Get global statistics about achievement unlocks and popularity"""
    try:
        # Get all achievements with unlock stats
        all_achievements = await crud.get_all_achievements()
        
        # Calculate global stats
        total_achievements = len(all_achievements)
        total_unlocks = sum(ach.unlock_count for ach in all_achievements)
        
        # Category breakdown
        category_stats = {}
        rarity_stats = {}
        
        for ach in all_achievements:
            # Category stats
            category = ach.category.value
            if category not in category_stats:
                category_stats[category] = {"count": 0, "total_unlocks": 0}
            category_stats[category]["count"] += 1
            category_stats[category]["total_unlocks"] += ach.unlock_count
            
            # Rarity stats
            rarity = ach.rarity
            if rarity not in rarity_stats:
                rarity_stats[rarity] = {"count": 0, "total_unlocks": 0}
            rarity_stats[rarity]["count"] += 1
            rarity_stats[rarity]["total_unlocks"] += ach.unlock_count
        
        # Most popular achievements (top 10)
        popular_achievements = sorted(all_achievements, key=lambda x: x.unlock_count, reverse=True)[:10]
        popular_list = [
            {
                "id": str(ach.id),
                "name": ach.name,
                "category": ach.category.value,
                "rarity": ach.rarity,
                "unlock_count": ach.unlock_count,
                "unlock_percentage": ach.unlock_percentage
            }
            for ach in popular_achievements
        ]
        
        # Rarest achievements (lowest unlock percentage, but with at least 1 unlock)
        rare_achievements = sorted(
            [ach for ach in all_achievements if ach.unlock_count > 0], 
            key=lambda x: x.unlock_percentage
        )[:5]
        rare_list = [
            {
                "id": str(ach.id),
                "name": ach.name,
                "category": ach.category.value,
                "rarity": ach.rarity,
                "unlock_count": ach.unlock_count,
                "unlock_percentage": ach.unlock_percentage
            }
            for ach in rare_achievements
        ]
        
        return {
            "success": True,
            "global_stats": {
                "total_achievements": total_achievements,
                "total_unlocks": total_unlocks,
                "average_unlocks_per_achievement": round(total_unlocks / total_achievements if total_achievements > 0 else 0, 2)
            },
            "category_breakdown": category_stats,
            "rarity_breakdown": rarity_stats,
            "most_popular": popular_list,
            "rarest_achievements": rare_list,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting global achievement stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/leaderboard", summary="Get Achievement Leaderboard")
async def get_achievement_leaderboard(
    limit: int = Query(50, ge=1, le=100, description="Number of top users to return"),
    achievement_service: AchievementService = Depends(get_achievement_service)
):
    """
    Get leaderboard of users with most achievements unlocked
    
    - **limit**: Maximum number of users to return in leaderboard
    """
    try:
        leaderboard = await achievement_service.get_achievement_leaderboard(limit)
        
        return {
            "success": True,
            "leaderboard_type": "achievements",
            "total_entries": len(leaderboard),
            "data": leaderboard,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting achievement leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Achievement Management Endpoints (Admin)
@router.post("/admin/create-defaults", summary="Create Default Achievements (Admin)", tags=["Admin"])
async def create_default_achievements(
    background_tasks: BackgroundTasks,
    achievement_service: AchievementService = Depends(get_achievement_service)
):
    """
    Create default achievements for the platform (Admin only)
    
    This endpoint creates a set of predefined achievements covering:
    - Learning milestones
    - Streak achievements  
    - Level progression
    - Career development
    - Special challenges
    """
    try:
        # Create achievements in background to avoid timeout
        background_tasks.add_task(create_achievements_background, achievement_service)
        
        return {
            "success": True,
            "message": "Default achievement creation initiated",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error initiating default achievement creation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def create_achievements_background(achievement_service: AchievementService):
    """Background task to create default achievements"""
    try:
        await achievement_service.create_default_achievements()
        logger.info("Default achievements created successfully")
    except Exception as e:
        logger.error(f"Error creating default achievements in background: {e}")

@router.post("/admin/recalculate-stats", summary="Recalculate Achievement Statistics (Admin)", tags=["Admin"])
async def recalculate_achievement_stats(
    background_tasks: BackgroundTasks,
    crud: GamificationCRUD = Depends(get_crud)
):
    """
    Recalculate unlock statistics for all achievements (Admin only)
    
    This updates unlock counts and percentages for all achievements
    """
    try:
        background_tasks.add_task(recalculate_stats_background, crud)
        
        return {
            "success": True,
            "message": "Achievement statistics recalculation initiated",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error initiating stats recalculation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def recalculate_stats_background(crud: GamificationCRUD):
    """Background task to recalculate achievement statistics"""
    try:
        db = await get_database()
        
        # Get all achievements
        all_achievements = await crud.get_all_achievements()
        total_users = await db.user_gamification.count_documents({})
        
        for achievement in all_achievements:
            # Count unlocks for this achievement
            unlock_count = await db.user_achievements.count_documents(
                {"achievement_id": achievement.id}
            )
            
            # Calculate percentage
            unlock_percentage = (unlock_count / total_users * 100) if total_users > 0 else 0
            
            # Update achievement
            await db.achievements.update_one(
                {"_id": achievement.id},
                {
                    "$set": {
                        "unlock_count": unlock_count,
                        "unlock_percentage": round(unlock_percentage, 2)
                    }
                }
            )
        
        logger.info(f"Recalculated statistics for {len(all_achievements)} achievements")
        
    except Exception as e:
        logger.error(f"Error recalculating achievement stats: {e}")
