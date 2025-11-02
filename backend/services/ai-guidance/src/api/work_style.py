"""
API endpoints for Work Style Assessment
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

router = APIRouter()

# 25 RELATABLE, CONVERSATIONAL QUESTIONS (inline to avoid import issues)
WORK_STYLE_QUESTIONS: List[Dict] = [
    {"id": 1, "text": "I enjoy working in teams and collaborating with others", "trait": "extraversion", "reverse": False},
    {"id": 2, "text": "I prefer working independently rather than in groups", "trait": "extraversion", "reverse": True},
    {"id": 3, "text": "I feel energized after networking events or team meetings", "trait": "extraversion", "reverse": False},
    {"id": 4, "text": "I tend to be quiet in group settings", "trait": "extraversion", "reverse": True},
    {"id": 5, "text": "I enjoy leading discussions and presenting ideas", "trait": "extraversion", "reverse": False},
    {"id": 6, "text": "I always plan ahead before starting a new project", "trait": "conscientiousness", "reverse": False},
    {"id": 7, "text": "I often leave tasks unfinished", "trait": "conscientiousness", "reverse": True},
    {"id": 8, "text": "I pay close attention to details", "trait": "conscientiousness", "reverse": False},
    {"id": 9, "text": "I prefer to keep my workspace organized", "trait": "conscientiousness", "reverse": False},
    {"id": 10, "text": "I sometimes procrastinate on important tasks", "trait": "conscientiousness", "reverse": True},
    {"id": 11, "text": "I enjoy learning new skills and exploring new ideas", "trait": "openness", "reverse": False},
    {"id": 12, "text": "I prefer routine and familiar tasks", "trait": "openness", "reverse": True},
    {"id": 13, "text": "I'm comfortable adapting to changes in plans", "trait": "openness", "reverse": False},
    {"id": 14, "text": "I enjoy creative problem-solving", "trait": "openness", "reverse": False},
    {"id": 15, "text": "I stick to traditional methods rather than trying new approaches", "trait": "openness", "reverse": True},
    {"id": 16, "text": "I value harmony and avoid conflicts with teammates", "trait": "agreeableness", "reverse": False},
    {"id": 17, "text": "I'm comfortable challenging others' ideas", "trait": "agreeableness", "reverse": True},
    {"id": 18, "text": "I enjoy helping colleagues solve their problems", "trait": "agreeableness", "reverse": False},
    {"id": 19, "text": "I prioritize team success over individual recognition", "trait": "agreeableness", "reverse": False},
    {"id": 20, "text": "I tend to be direct and assertive in discussions", "trait": "agreeableness", "reverse": True},
    {"id": 21, "text": "I stay calm under pressure and tight deadlines", "trait": "neuroticism", "reverse": True},
    {"id": 22, "text": "I often worry about work-related tasks", "trait": "neuroticism", "reverse": False},
    {"id": 23, "text": "I handle criticism and feedback well", "trait": "neuroticism", "reverse": True},
    {"id": 24, "text": "I get stressed when things don't go as planned", "trait": "neuroticism", "reverse": False},
    {"id": 25, "text": "I maintain a positive outlook even during challenges", "trait": "neuroticism", "reverse": True}
]

class AssessmentResponse(BaseModel):
    userId: str
    answers: Dict[int, int]

@router.get("/psychometric/questions")
async def get_questions():
    """Get 25 work style questions"""
    try:
        return {
            "questions": WORK_STYLE_QUESTIONS,
            "total": len(WORK_STYLE_QUESTIONS),
            "title": "Discover Your Work Style",
            "instructions": "Rate each statement from 1 (Strongly Disagree) to 5 (Strongly Agree)",
            "estimated_time_minutes": 6
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/psychometric/complete")
async def complete_assessment(response: AssessmentResponse):
    """Submit completed assessment"""
    if len(response.answers) < 20:
        raise HTTPException(status_code=400, detail="Please answer at least 20 questions")
    
    # Calculate scores
    trait_scores = {"extraversion": [], "conscientiousness": [], "openness": [], "agreeableness": [], "neuroticism": []}
    
    for question in WORK_STYLE_QUESTIONS:
        qid = question["id"]
        if qid not in response.answers:
            continue
        score = response.answers[qid]
        trait = question["trait"]
        if question["reverse"]:
            score = 6 - score
        trait_scores[trait].append(score)
    
    final_scores = {}
    for trait, scores in trait_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            final_scores[trait] = round((avg - 1) * 25, 1)
        else:
            final_scores[trait] = 50.0
    
    return {
        "userId": response.userId,
        "trait_scores": final_scores,
        "assessed_at": datetime.utcnow().isoformat(),
        "completeness": len(response.answers) / 25 * 100
    }
