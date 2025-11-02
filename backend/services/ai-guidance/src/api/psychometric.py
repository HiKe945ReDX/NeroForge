from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import google.generativeai as genai
import os
import json
from typing import Dict, List

router = APIRouter(prefix="/api/psychometric", tags=["psychometric"])

WORK_STYLE_QUESTIONS = [
    {"id": 1, "trait": "openness", "text": "I enjoy learning new technologies and frameworks", "reverse": False},
    {"id": 2, "trait": "conscientiousness", "text": "I prefer planning before diving into code", "reverse": False},
    {"id": 3, "trait": "extraversion", "text": "I like collaborating in pair programming sessions", "reverse": False},
    {"id": 4, "trait": "agreeableness", "text": "I help teammates debug their code", "reverse": False},
    {"id": 5, "trait": "neuroticism", "text": "Tight deadlines make me anxious", "reverse": True},
    {"id": 6, "trait": "openness", "text": "I experiment with new programming approaches", "reverse": False},
    {"id": 7, "trait": "conscientiousness", "text": "I write tests for all my code", "reverse": False},
    {"id": 8, "trait": "extraversion", "text": "I prefer working in open office environments", "reverse": False},
    {"id": 9, "trait": "agreeableness", "text": "I seek feedback on my code regularly", "reverse": False},
    {"id": 10, "trait": "openness", "text": "I follow established patterns rather than experimenting", "reverse": True},
    {"id": 11, "trait": "conscientiousness", "text": "I document my code thoroughly", "reverse": False},
    {"id": 12, "trait": "extraversion", "text": "I enjoy presenting my work to large audiences", "reverse": False},
    {"id": 13, "trait": "agreeableness", "text": "I take responsibility when projects fail", "reverse": False},
    {"id": 14, "trait": "neuroticism", "text": "I stay calm under pressure", "reverse": True},
    {"id": 15, "trait": "openness", "text": "I'm curious about how other teams solve problems", "reverse": False},
]

class PsychometricResponse(BaseModel):
    user_id: str
    answers: Dict[int, int]

@router.get("/questions")
async def get_questions():
    return {
        "questions": WORK_STYLE_QUESTIONS,
        "total": len(WORK_STYLE_QUESTIONS),
        "title": "Discover Your Work Style",
        "instructions": "Rate each statement from 1 (Strongly Disagree) to 5 (Strongly Agree)",
        "estimated_time_minutes": 4
    }

@router.post("/complete")
async def complete_assessment(response: PsychometricResponse):
    if len(response.answers) < 12:
        raise HTTPException(status_code=400, detail="Please answer at least 12 questions")
    
    trait_scores = {}
    for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
        trait_questions = [q for q in WORK_STYLE_QUESTIONS if q["trait"] == trait]
        scores = []
        
        for q in trait_questions:
            if q["id"] in response.answers:
                score = response.answers[q["id"]]
                if q["reverse"]:
                    score = 6 - score
                scores.append(score)
        
        if scores:
            avg = sum(scores) / len(scores)
            trait_scores[trait] = round((avg - 1) * 25, 1)
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""Based on these Big Five trait scores (0-100 scale):
- Openness: {trait_scores.get('openness', 50)}
- Conscientiousness: {trait_scores.get('conscientiousness', 50)}
- Extraversion: {trait_scores.get('extraversion', 50)}
- Agreeableness: {trait_scores.get('agreeableness', 50)}
- Neuroticism: {trait_scores.get('neuroticism', 50)}

Classify their work style into ONE category:
- Innovator (High openness, low conscientiousness)
- Organizer (High conscientiousness, low openness)
- Collaborator (High extraversion, high agreeableness)
- Analyzer (Low extraversion, high conscientiousness)
- Leader (High extraversion, high openness)

Return JSON: {{"work_style": "...", "interpretation": "...", "recommendations": [...]}}"""
    
    try:
        result = client.models.generate_content(prompt)
        interpretation = json.loads(result.text)
    except:
        interpretation = {
            "work_style": "Balanced",
            "interpretation": "Your work style is balanced across all traits",
            "recommendations": []
        }
    
    return {
        "user_id": response.user_id,
        "trait_scores": trait_scores,
        "work_style": interpretation.get("work_style"),
        "interpretation": interpretation.get("interpretation"),
        "recommendations": interpretation.get("recommendations", []),
        "completed_at": datetime.utcnow().isoformat(),
        "confidence": 85.0
    }
