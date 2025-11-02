from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

try:
    with open("src/data/empathy_map_questions.json", "r") as f:
        EMPATHY_QUESTIONS_DATA = json.load(f)
except:
    EMPATHY_QUESTIONS_DATA = []

@router.get("/questions")
async def get_empathy_questions():
    try:
        if not EMPATHY_QUESTIONS_DATA:
            fallback_questions = [
                {"id": 1, "text": "I openly share my thoughts with my team", "quadrant": "SAY"},
                {"id": 2, "text": "I take initiative to help colleagues", "quadrant": "DO"},
                {"id": 3, "text": "I consider others' perspectives", "quadrant": "THINK"},
                {"id": 4, "text": "I notice when someone seems upset", "quadrant": "FEEL"},
            ]
            return {
                "questions": fallback_questions + fallback_questions * 5,
                "total": 20,
                "title": "Empathy & Team Compatibility Assessment",
                "description": "Scale 1-5: Strongly Disagree to Strongly Agree",
                "estimated_time_minutes": 5,
                "instructions": "Rate each statement from 1 (Strongly Disagree) to 5 (Strongly Agree)"
            }
        
        return {
            "questions": EMPATHY_QUESTIONS_DATA.get("questions", [])[:20],
            "total": len(EMPATHY_QUESTIONS_DATA.get("questions", [])),
            "title": EMPATHY_QUESTIONS_DATA.get("title", "Empathy Assessment"),
            "description": EMPATHY_QUESTIONS_DATA.get("description", ""),
            "estimated_time_minutes": 5
        }
    except Exception as e:
        logger.error(f"Error fetching empathy questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading questions")

class EmpathySubmissionRequest(BaseModel):
    user_id: str
    answers: Dict[str, int]

@router.post("/submit")
async def submit_empathy_assessment(request: EmpathySubmissionRequest):
    try:
        if not request.answers or len(request.answers) == 0:
            raise ValueError("No answers provided")
        
        for q_id, score in request.answers.items():
            if not isinstance(score, int) or score < 1 or score > 5:
                raise ValueError(f"Invalid score for question {q_id}: {score}")
        
        quadrant_mapping = {
            "SAY": list(range(1, 6)),
            "DO": list(range(6, 11)),
            "THINK": list(range(11, 16)),
            "FEEL": list(range(16, 21))
        }
        
        quadrant_scores = {}
        total_score = 0
        
        for quadrant, questions in quadrant_mapping.items():
            scores = []
            for q in questions:
                if str(q) in request.answers:
                    scores.append(request.answers[str(q)])
            
            if scores:
                avg = sum(scores) / len(scores)
                quadrant_scores[quadrant.lower()] = round(avg * 20, 1)
                total_score += avg
        
        empathy_score = round((total_score / 4) * 20, 1) if len(quadrant_scores) > 0 else 0
        
        say_score = quadrant_scores.get("say", 0)
        do_score = quadrant_scores.get("do", 0)
        think_score = quadrant_scores.get("think", 0)
        feel_score = quadrant_scores.get("feel", 0)
        
        if say_score > 70 and do_score > 70:
            team_role = "Leader"
        elif do_score > 75:
            team_role = "Collaborator"
        elif think_score > 75:
            team_role = "Analyst"
        elif feel_score > 75:
            team_role = "Mediator"
        else:
            team_role = "Contributor"
        
        return {
            "user_id": request.user_id,
            "empathy_score": empathy_score,
            "team_role": team_role,
            "quadrant_scores": quadrant_scores,
            "say_score": say_score,
            "do_score": do_score,
            "think_score": think_score,
            "feel_score": feel_score,
            "team_compatibility": {
                "works_well_with": ["Collaborator", "Analyst"],
                "communication_style": "Balanced",
                "conflict_resolution": "Flexible",
                "strengths": ["Leadership", "Analysis", "Communication"],
                "growth_areas": ["Delegation", "Listening"]
            },
            "step_completed": 5,
            "next_step": "career_preferences"
        }
    
    except ValueError as e:
        logger.error(f"Validation error in empathy assessment: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing empathy assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing assessment")
