from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from ..models.models import AssessmentResponse
from ..services.work_style_assessment import WorkStyleAssessment
from ..services.empathy_map import EmpathyMap
from ..core.database import get_database
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI Services"])

@router.post("/work-style/evaluate", response_model=AssessmentResponse)
async def evaluate_work_style(
    responses: Dict[int, int],
    user_id: str = Query(...),
    db = Depends(get_database)
):
    try:
        assessor = WorkStyleAssessment()
        traits = await assessor.evaluate(responses)
        
        await db.work_styles.insert_one({
            "user_id": user_id,
            "traits": traits,
            "timestamp": datetime.utcnow()
        })
        
        return AssessmentResponse(user_id=user_id, traits=traits, score=sum(v for v in traits.values()) / len(traits))
    except Exception as e:
        logger.error(f"Work style evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/work-style/questions")
async def get_work_style_questions(language: str = Query("en")):
    assessor = WorkStyleAssessment()
    return await assessor.get_questions(language)

@router.post("/empathy-map/evaluate")
async def evaluate_empathy_map(
    responses: Dict[str, List[int]],
    user_id: str = Query(...),
    db = Depends(get_database)
):
    try:
        mapper = EmpathyMap()
        result = await mapper.evaluate(responses)
        
        await db.empathy_maps.insert_one({
            "user_id": user_id,
            "result": result,
            "timestamp": datetime.utcnow()
        })
        
        return result
    except Exception as e:
        logger.error(f"Empathy map evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-guidance"}
