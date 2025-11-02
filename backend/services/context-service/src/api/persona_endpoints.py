from fastapi import APIRouter, HTTPException, Depends, Query
from ..services.persona_aggregator import get_aggregator, PersonaAggregator
from ..core.database import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/context", tags=["context"])

@router.get("/persona/{user_id}")
async def get_user_persona(
    user_id: str,
    force_refresh: bool = Query(False, description="Force cache refresh"),
    db=Depends(get_database)
):
    """
    🔥 Get unified persona for user with all aggregated data
    Used by: AI Roadmap Generator, Career Matcher, Coach Selector
    """
    try:
        aggregator = await get_aggregator(db)
        persona = await aggregator.get_unified_persona(user_id, force_refresh)
        
        if "error" in persona:
            raise HTTPException(status_code=500, detail=persona["error"])
        
        logger.info(f"✅ Persona retrieved for {user_id}: {persona['completeness_score']:.1%} complete")
        return persona
    except Exception as e:
        logger.error(f"❌ Error retrieving persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/persona/{user_id}/summary")
async def get_persona_summary(user_id: str, db=Depends(get_database)):
    """Quick summary (basic info + scores only)"""
    try:
        aggregator = await get_aggregator(db)
        persona = await aggregator.get_unified_persona(user_id)
        
        return {
            "user_id": user_id,
            "name": persona["basic_info"]["name"],
            "completeness": persona["completeness_score"],
            "portfolio_score": persona["portfolio_score"],
            "readiness_tier": persona["readiness_tier"],
            "target_career": persona["career_preferences"]["target_career"],
            "ready_for_roadmap": persona["completeness_score"] >= 0.6
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/persona/{user_id}/invalidate-cache")
async def invalidate_cache(user_id: str, db=Depends(get_database)):
    """Force refresh persona data (call after user updates profile)"""
    try:
        aggregator = await get_aggregator(db)
        if user_id in aggregator.cache:
            del aggregator.cache[user_id]
            logger.info(f"🗑️ Cache invalidated for {user_id}")
        return {"message": "Cache invalidated", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "context-service", "version": "2.0"}
