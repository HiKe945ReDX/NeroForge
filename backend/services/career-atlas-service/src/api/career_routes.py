from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import os
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/api/careers", tags=["careers"])

class DiscoveryRequest(BaseModel):
    userId: str
    answers: dict

@router.post("/discover/suggest-careers")
async def suggest_careers(request: DiscoveryRequest):
    """Suggests careers based on AI discovery answers"""
    try:
        # Use Gemini API (injected via GCP Secret Manager)
        from google.cloud import aiplatform
        
        prompt = f"""Based on these answers, suggest 10 careers:
        {request.answers}
        Return only JSON array with career objects."""
        
        # Mock response (replace with actual Gemini call)
        careers = [
            {"id": "software-engineer", "title": "Software Engineer", "description": "Build applications"},
            {"id": "data-scientist", "title": "Data Scientist", "description": "Analyze data patterns"},
        ]
        
        return {"success": True, "careers": careers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get/{careerId}")
async def get_career(careerId: str):
    """Get detailed career information"""
    try:
        # Mock data (replace with DB lookup)
        career = {
            "id": careerId,
            "title": "Software Engineer",
            "description": "Professional who develops software applications",
            "category": "Technology",
            "avgSalary": 120000,
            "requiredSkills": ["Python", "React", "SQL"],
            "educationPath": "Bachelor's in CS"
        }
        return {"success": True, "career": career}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fit-score")
async def calculate_fit_score(userId: str, careerId: str, userSkills: List[str]):
    """Calculate fit score for user + career"""
    try:
        # Simple calculation (1-100)
        fit_score = min(100, len(userSkills) * 15)
        return {
            "success": True,
            "fitScore": fit_score,
            "quality": "Good" if fit_score > 60 else "Fair"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
