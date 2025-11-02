from fastapi import APIRouter, HTTPException, Depends, Query, Path, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from ..models.gamification_models import LeaderboardType
from ..services.leaderboard_service import LeaderboardService
from ..utils.cache_manager import CacheManager
from ..db.client import get_database
from ..db.gamification_crud import GamificationCRUD

logger = logging.getLogger(__name__)

# Initialize router with prefix and tags
router = APIRouter(prefix="/api/v1/leaderboards", tags=["Leaderboards"])

# Service dependencies
async def get_leaderboard_service():
    service = LeaderboardService()
    await service.initialize()
    return service

async def get_cache_manager():
    manager = CacheManager()
    await manager.initialize()
    return manager

async def get_crud():
    db = await get_database()
    return GamificationCRUD(db)

# Main Leaderboard Endpoints
@router.get("/", summary="Get All Available Leaderboards")
async def get_available_leaderboards():
    """Get information about all available leaderboard types"""
    try:
        leaderboards_info = {
            "global": {
                "name": "Global Leaderboard",
                "description": "All-time ranking based on total XP earned",
                "update_frequency": "Real-time",
                "scoring_method": "Total Experience Points",
                "icon": "🌍",
                "criteria": "All users ranked by lifetime XP accumulation"
            },
            "weekly": {
                "name": "Weekly Leaderboard", 
                "description": "This week's top performers",
                "update_frequency": "Hourly",
                "scoring_method": "Weekly Points Earned",
                "icon": "📅",
                "criteria": "Points earned in the current week (Monday-Sunday)"
            },
            "monthly": {
                "name": "Monthly Leaderboard",
                "description": "This month's most active learners",
                "update_frequency": "Daily",
                "scoring_method": "Monthly Points Earned", 
                "icon": "🗓️",
                "criteria": "Points earned in the current calendar month"
            }
        }
        
        return {
            "success": True,
            "available_leaderboards": leaderboards_info,
            "total_types": len(leaderboards_info)
        }
        
    except Exception as e:
        logger.error(f"Error getting available leaderboards: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{leaderboard_type}", summary="Get Leaderboard by Type")
async def get_leaderboard(
    leaderboard_type: str = Path(..., description="Leaderboard type (global, weekly, monthly)"),
    limit: int = Query(50, ge=1, le=100, description="Number of entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip (for pagination)"),
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service)
):
    """Get leaderboard entries by type with pagination support"""
    try:
        # Validate leaderboard type
        valid_types = ["global", "weekly", "monthly"]
        if leaderboard_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid leaderboard type '{leaderboard_type}'. Must be one of: {valid_types}"
            )
        
        # Get leaderboard data
        leaderboard_data = await leaderboard_service.get_leaderboard(leaderboard_type, limit + offset)
        
        if "error" in leaderboard_data:
            raise HTTPException(status_code=404, detail=leaderboard_data["error"])
        
        # Apply pagination
        entries = leaderboard_data.get("entries", [])
        total_entries = len(entries)
        paginated_entries = entries[offset:offset + limit]
        
        # Add pagination metadata
        pagination = {
            "current_page": (offset // limit) + 1 if limit > 0 else 1,
            "per_page": limit,
            "total_entries": total_entries,
            "total_pages": (total_entries + limit - 1) // limit if limit > 0 else 1,
            "has_next": offset + limit < total_entries,
            "has_previous": offset > 0
        }
        
        return {
            "success": True,
            "leaderboard_type": leaderboard_type,
            "data": {
                "entries": paginated_entries,
                "pagination": pagination,
                "last_updated": leaderboard_data.get("last_updated"),
                "cached": leaderboard_data.get("cached", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting leaderboard {leaderboard_type}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{leaderboard_type}/top", summary="Get Top N Users")
async def get_top_users(
    leaderboard_type: str = Path(..., description="Leaderboard type"),
    count: int = Query(10, ge=1, le=25, description="Number of top users to return"),
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service)
):
    """Get the top N users from a specific leaderboard"""
    try:
        # Validate leaderboard type
        valid_types = ["global", "weekly", "monthly"]
        if leaderboard_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid leaderboard type. Must be one of: {valid_types}"
            )
        
        # Get leaderboard data
        leaderboard_data = await leaderboard_service.get_leaderboard(leaderboard_type, count)
        
        if "error" in leaderboard_data:
            raise HTTPException(status_code=404, detail=leaderboard_data["error"])
        
        entries = leaderboard_data.get("entries", [])[:count]
        
        # Enhance entries with additional info
        enhanced_entries = []
        for entry in entries:
            enhanced_entry = {
                **entry,
                "rank_suffix": get_rank_suffix(entry.get("rank", 0)),
                "score_formatted": format_score(entry.get("score", 0))
            }
            enhanced_entries.append(enhanced_entry)
        
        return {
            "success": True,
            "leaderboard_type": leaderboard_type,
            "requested_count": count,
            "actual_count": len(enhanced_entries),
            "top_users": enhanced_entries,
            "last_updated": leaderboard_data.get("last_updated")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting top users for {leaderboard_type}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User-Specific Leaderboard Endpoints
@router.get("/{leaderboard_type}/user/{user_id}", summary="Get User's Leaderboard Position")
async def get_user_position(
    leaderboard_type: str = Path(..., description="Leaderboard type"),
    user_id: str = Path(..., description="User ID"),
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service)
):
    """Get a specific user's position in a leaderboard"""
    try:
        # Validate leaderboard type
        valid_types = ["global", "weekly", "monthly"]
        if leaderboard_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid leaderboard type. Must be one of: {valid_types}"
            )
        
        # Get user position
        position_data = await leaderboard_service.get_user_leaderboard_position(user_id, leaderboard_type)
        
        if "error" in position_data:
            raise HTTPException(status_code=404, detail=position_data["error"])
        
        # Enhance position data
        position = position_data.get("position", {})
        if "rank" in position:
            position["rank_suffix"] = get_rank_suffix(position["rank"])
            position["score_formatted"] = format_score(position.get("score", 0))
        
        return {
            "success": True,
            "leaderboard_type": leaderboard_type,
            "user_id": user_id,
            "position": position,
            "total_entries": position_data.get("total_entries", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user position for {user_id} in {leaderboard_type}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{leaderboard_type}/user/{user_id}/nearby", summary="Get Users Near User's Position")
async def get_nearby_users(
    leaderboard_type: str = Path(..., description="Leaderboard type"),
    user_id: str = Path(..., description="User ID"),
    range_size: int = Query(5, ge=1, le=10, description="Number of users above and below"),
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service)
):
    """Get users ranked near a specific user's position"""
    try:
        # Validate leaderboard type
        valid_types = ["global", "weekly", "monthly"]
        if leaderboard_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid leaderboard type. Must be one of: {valid_types}"
            )
        
        # Get nearby rankings
        if leaderboard_type == "global":
            nearby_data = await leaderboard_service.get_user_nearby_rankings(user_id, range_size)
        else:
            # For weekly/monthly, get user position first
            position_data = await leaderboard_service.get_user_leaderboard_position(user_id, leaderboard_type)
            if "error" in position_data:
                raise HTTPException(status_code=404, detail=position_data["error"])
            
            user_rank = position_data.get("position", {}).get("rank", 0)
            if user_rank == 0:
                raise HTTPException(status_code=404, detail="User not found in leaderboard")
            
            # Get leaderboard around user's position
            start_rank = max(1, user_rank - range_size)
            end_rank = user_rank + range_size
            needed_entries = end_rank - start_rank + 1
            
            leaderboard_data = await leaderboard_service.get_leaderboard(leaderboard_type, needed_entries)
            all_entries = leaderboard_data.get("entries", [])
            
            # Filter to nearby entries
            nearby_entries = []
            for entry in all_entries:
                entry_rank = entry.get("rank", 0)
                if start_rank <= entry_rank <= end_rank:
                    entry["is_current_user"] = str(entry.get("user_id")) == str(user_id)
                    nearby_entries.append(entry)
            
            nearby_data = {
                "user_id": user_id,
                "user_rank": user_rank,
                "range": {"start": start_rank, "end": end_rank},
                "nearby_rankings": nearby_entries
            }
        
        if "error" in nearby_data:
            raise HTTPException(status_code=404, detail=nearby_data["error"])
        
        # Enhance nearby data with formatting
        for entry in nearby_data.get("nearby_rankings", []):
            entry["rank_suffix"] = get_rank_suffix(entry.get("rank", 0))
            entry["score_formatted"] = format_score(entry.get("score", 0))
        
        return {
            "success": True,
            "leaderboard_type": leaderboard_type,
            "data": nearby_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting nearby users for {user_id} in {leaderboard_type}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Leaderboard Analytics and Stats
@router.get("/stats/summary", summary="Get Leaderboard Statistics Summary")
async def get_leaderboard_stats(
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service)
):
    """Get comprehensive statistics about all leaderboards"""
    try:
        stats = await leaderboard_service.get_leaderboard_stats()
        
        # Add derived statistics
        enhanced_stats = {}
        for lb_type, lb_stats in stats.items():
            enhanced_stats[lb_type] = {
                **lb_stats,
                "score_range": {
                    "top_score": lb_stats.get("top_score", 0),
                    "average_score": lb_stats.get("average_score", 0),
                    "score_gap": lb_stats.get("top_score", 0) - lb_stats.get("average_score", 0)
                },
                "activity_level": get_activity_level(lb_stats.get("total_entries", 0)),
                "last_updated_formatted": format_last_updated(lb_stats.get("last_updated"))
            }
        
        return {
            "success": True,
            "statistics": enhanced_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting leaderboard stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/activity", summary="Get Leaderboard Activity Analysis")
async def get_activity_analysis(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    crud: GamificationCRUD = Depends(get_crud)
):
    """Analyze leaderboard activity over time"""
    try:
        # Get activity data from the last N days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get user activities in date range
        db = await get_database()
        
        # Aggregate activity by day
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                        "user_id": "$user_id"
                    },
                    "daily_points": {"$sum": "$points_earned"},
                    "daily_activities": {"$sum": 1}
                }
            },
            {
                "$group": {
                    "_id": "$_id.date",
                    "active_users": {"$sum": 1},
                    "total_points": {"$sum": "$daily_points"},
                    "total_activities": {"$sum": "$daily_activities"}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        cursor = db.activity_records.aggregate(pipeline)
        daily_data = []
        async for doc in cursor:
            daily_data.append({
                "date": doc["_id"],
                "active_users": doc["active_users"],
                "total_points": doc["total_points"],
                "total_activities": doc["total_activities"],
                "avg_points_per_user": round(doc["total_points"] / doc["active_users"] if doc["active_users"] > 0 else 0, 2)
            })
        
        # Calculate trends
        if len(daily_data) >= 2:
            recent_avg = sum(day["active_users"] for day in daily_data[-3:]) / min(3, len(daily_data))
            early_avg = sum(day["active_users"] for day in daily_data[:3]) / min(3, len(daily_data))
            
            if recent_avg > early_avg * 1.1:
                trend = "increasing"
            elif recent_avg < early_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "success": True,
            "analysis_period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "daily_activity": daily_data,
            "trend_analysis": {
                "activity_trend": trend,
                "total_days_analyzed": len(daily_data),
                "peak_activity_day": max(daily_data, key=lambda x: x["active_users"])["date"] if daily_data else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting activity analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ✅ FIXED LINE 419:
@router.post("/admin/update/{leaderboard_type}", summary="Update Specific Leaderboard (Admin)", tags=["Admin"])
async def update_leaderboard(
    background_tasks: BackgroundTasks,  # ✅ MOVE BackgroundTasks FIRST (no default)
    leaderboard_type: str = Path(..., description="Leaderboard type to update"),  # ✅ Now this can have default
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service)  # ✅ This can have default
):
    """Manually trigger update for a specific leaderboard (Admin only)"""
    try:
        valid_types = ["global", "weekly", "monthly"]
        if leaderboard_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid leaderboard type. Must be one of: {valid_types}"
            )
        
        # Update leaderboard in background
        background_tasks.add_task(update_single_leaderboard, leaderboard_service, leaderboard_type)
        
        return {
            "success": True,
            "message": f"{leaderboard_type.title()} leaderboard update initiated",
            "leaderboard_type": leaderboard_type,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating {leaderboard_type} leaderboard update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ✅ FIXED LINE 449:
@router.post("/admin/update-all", summary="Update All Leaderboards (Admin)", tags=["Admin"]) 
async def update_all_leaderboards(
    background_tasks: BackgroundTasks,  # ✅ MOVE BackgroundTasks FIRST (no default)
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service)  # ✅ This can have default
):
    """Manually trigger update for all leaderboards (Admin only)"""
    try:
        background_tasks.add_task(update_all_leaderboards_background, leaderboard_service)
        
        return {
            "success": True,
            "message": "All leaderboards update initiated",
            "leaderboards": ["global", "weekly", "monthly"],
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error initiating all leaderboards update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Background Tasks
async def update_single_leaderboard(leaderboard_service: LeaderboardService, leaderboard_type: str):
    """Background task to update a single leaderboard"""
    try:
        if leaderboard_type == "global":
            result = await leaderboard_service.update_global_leaderboard()
        elif leaderboard_type == "weekly":
            result = await leaderboard_service.update_weekly_leaderboard()
        elif leaderboard_type == "monthly":
            result = await leaderboard_service.update_monthly_leaderboard()
        else:
            result = False
        
        status = "success" if result else "failed"
        logger.info(f"{leaderboard_type.title()} leaderboard update {status}")
        
    except Exception as e:
        logger.error(f"Error updating {leaderboard_type} leaderboard: {e}")

async def update_all_leaderboards_background(leaderboard_service: LeaderboardService):
    """Background task to update all leaderboards"""
    try:
        results = await leaderboard_service.update_all_leaderboards()
        logger.info(f"All leaderboards update results: {results}")
    except Exception as e:
        logger.error(f"Error updating all leaderboards: {e}")

# Utility Functions
def get_rank_suffix(rank: int) -> str:
    """Get appropriate suffix for rank number (1st, 2nd, 3rd, etc.)"""
    if 10 <= rank % 100 <= 20:
        return f"{rank}th"
    else:
        suffix_map = {1: "st", 2: "nd", 3: "rd"}
        return f"{rank}{suffix_map.get(rank % 10, 'th')}"

def format_score(score: int) -> str:
    """Format score with proper number formatting"""
    if score >= 1000000:
        return f"{score/1000000:.1f}M"
    elif score >= 1000:
        return f"{score/1000:.1f}K"
    else:
        return str(score)

def get_activity_level(entry_count: int) -> str:
    """Determine activity level based on entry count"""
    if entry_count >= 1000:
        return "very_high"
    elif entry_count >= 500:
        return "high"
    elif entry_count >= 100:
        return "medium"
    elif entry_count >= 10:
        return "low"
    else:
        return "very_low"

def format_last_updated(last_updated: Optional[str] = None) -> str:
    """Format last updated time in a human-readable way"""
    if not last_updated:
        return "Never"
    
    try:
        update_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        now = datetime.utcnow()
        diff = now - update_time.replace(tzinfo=None)
        
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60} minutes ago"
        elif diff.days == 0:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.days == 1:
            return "Yesterday"
        else:
            return f"{diff.days} days ago"
    except:
        return last_updated
