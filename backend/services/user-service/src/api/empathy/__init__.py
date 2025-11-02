from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from src.core.database import get_database
from datetime import datetime

router = APIRouter()

EMPATHY_QUESTIONS = [
    {"id": 1, "text": "I openly share my thoughts and feelings with my team", "quadrant": "say", "reverse": False},
    {"id": 2, "text": "I find it easy to articulate my ideas clearly", "quadrant": "say", "reverse": False},
    {"id": 3, "text": "I avoid expressing disagreement even when I have concerns", "quadrant": "say", "reverse": True},
    {"id": 4, "text": "I actively participate in group discussions", "quadrant": "say", "reverse": False},
    {"id": 5, "text": "I prefer to keep my opinions to myself in meetings", "quadrant": "say", "reverse": True},
    {"id": 6, "text": "I take initiative to help colleagues without being asked", "quadrant": "do", "reverse": False},
    {"id": 7, "text": "I follow through on my commitments consistently", "quadrant": "do", "reverse": False},
    {"id": 8, "text": "I tend to wait for others to take the lead", "quadrant": "do", "reverse": True},
    {"id": 9, "text": "I actively seek feedback to improve my work", "quadrant": "do", "reverse": False},
    {"id": 10, "text": "I struggle to adapt my approach when plans change", "quadrant": "do", "reverse": True},
    {"id": 11, "text": "I genuinely consider others' perspectives before making decisions", "quadrant": "think", "reverse": False},
    {"id": 12, "text": "I find it difficult to understand why people react differently than I would", "quadrant": "think", "reverse": True},
    {"id": 13, "text": "I try to see situations from multiple angles", "quadrant": "think", "reverse": False},
    {"id": 14, "text": "I tend to judge situations based solely on my own experience", "quadrant": "think", "reverse": True},
    {"id": 15, "text": "I recognize patterns in how different people approach problems", "quadrant": "think", "reverse": False},
    {"id": 16, "text": "I notice when someone seems upset or uncomfortable", "quadrant": "feel", "reverse": False},
    {"id": 17, "text": "I'm often surprised by others' emotional reactions", "quadrant": "feel", "reverse": True},
    {"id": 18, "text": "I can sense the mood of a room when I enter", "quadrant": "feel", "reverse": False},
    {"id": 19, "text": "I struggle to connect with people's feelings", "quadrant": "feel", "reverse": True},
    {"id": 20, "text": "I feel energized when helping someone through a difficult time", "quadrant": "feel", "reverse": False}
]

@router.get("/questions")
async def get_empathy_questions():
    """Get all empathy map assessment questions"""
    return {
        "questions": EMPATHY_QUESTIONS,
        "total": len(EMPATHY_QUESTIONS)
    }

@router.post("/assess")
async def assess_empathy(data: Dict, db=Depends(get_database)):
    """Assess empathy based on answers"""
    user_id = data.get("user_id")
    responses = data.get("responses", [])
    
    # Simple scoring
    total_score = sum(r.get("score", 0) for r in responses)
    max_score = len(responses) * 5
    empathy_score = (total_score / max_score * 100) if max_score > 0 else 0
    
    result = {
        "user_id": user_id,
        "empathy_score": round(empathy_score, 2),
        "assessed_at": datetime.utcnow().isoformat()
    }
    
    # Store result
    await db.empathy_assessments.update_one(
        {"user_id": user_id},
        {"$set": result},
        upsert=True
    )
    
    return result

@router.get("/results/{user_id}")
async def get_empathy_results(user_id: str, db=Depends(get_database)):
    """Retrieve stored empathy assessment results"""
    result = await db.empathy_assessments.find_one({"user_id": user_id})
    if not result:
        raise HTTPException(status_code=404, detail="No empathy assessment found for this user")
    result.pop("_id", None)
    return result
