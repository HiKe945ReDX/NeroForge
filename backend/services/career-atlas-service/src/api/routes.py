"""
Career Atlas API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class CareerRecommendRequest(BaseModel):
    persona_embedding: List[float]
    top_k: int = 5

@router.post("/recommend")
async def recommend_careers(request: CareerRecommendRequest):
    """
    Get career recommendations based on persona embedding
    """
    try:
        from src.core.vector_db import vector_db
        matches = vector_db.search_similar_careers(
            persona_embedding=request.persona_embedding,
            top_k=request.top_k
        )
        return {"matches": matches}
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """Get Pinecone index statistics"""
    try:
        from src.core.vector_db import vector_db
        stats = vector_db.index.describe_index_stats()
        return {
            "total_careers": stats.total_vector_count,
            "dimension": stats.dimension,
            "index_fullness": stats.index_fullness
        }
    except Exception as e:
        logger.error(f"Stats fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
