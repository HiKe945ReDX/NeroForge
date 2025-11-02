from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import google.generativeai as genai
import os
import json
from typing import Dict

router = APIRouter(prefix="/api/empathy", tags=["empathy"])

EMPATHY_QUESTIONS = [
    {"id": 1, "quadrant": "say", "text": "When someone shares a problem, I usually...", "options": ["Give my immediate opinion", "Ask clarifying questions first"]},
    {"id": 2, "quadrant": "say", "text": "In meetings, my approach is...", "options": ["Voice ideas confidently", "Listen and build on others' ideas"]},
    {"id": 3, "quadrant": "say", "text": "When disagreeing, I...", "options": ["State my view clearly", "Try to understand their perspective first"]},
    {"id": 4, "quadrant": "say", "text": "I communicate my feelings...", "options": ["Directly and immediately", "After reflecting"]},
    {"id": 5, "quadrant": "say", "text": "With my team, I...", "options": ["Keep conversations professional", "Share personal experiences"]},
    {"id": 6, "quadrant": "do", "text": "When someone needs help, I...", "options": ["Help them find the solution", "Solve it for them"]},
    {"id": 7, "quadrant": "do", "text": "My team knows me as someone who...", "options": ["Gets things done independently", "Supports others' success"]},
    {"id": 8, "quadrant": "do", "text": "In conflicts, I...", "options": ["Stand firm on my position", "Look for compromises"]},
    {"id": 9, "quadrant": "do", "text": "When making decisions affecting my team, I...", "options": ["Decide quickly", "Consult others first"]},
    {"id": 10, "quadrant": "do", "text": "I spend most time...", "options": ["In focused work", "In team collaboration"]},
    {"id": 11, "quadrant": "think", "text": "I believe my role is...", "options": ["Deliver my own work", "Enable team success"]},
    {"id": 12, "quadrant": "think", "text": "When things go wrong, I think...", "options": ["What I could have done differently", "Who is responsible"]},
    {"id": 13, "quadrant": "think", "text": "I value colleagues who...", "options": ["Know everything and solve problems quickly", "Admit what they don't know"]},
    {"id": 14, "quadrant": "think", "text": "Success means...", "options": ["Achieving my goals", "Team achieving together"]},
    {"id": 15, "quadrant": "think", "text": "I approach diversity as...", "options": ["Something to tolerate", "Something to learn from"]},
    {"id": 16, "quadrant": "feel", "text": "When teammates struggle, I feel...", "options": ["Frustrated we're slowing down", "Empathy for their situation"]},
    {"id": 17, "quadrant": "feel", "text": "Team celebrations make me feel...", "options": ["Meh", "Genuinely happy"]},
    {"id": 18, "quadrant": "feel", "text": "When someone disagrees with me, I feel...", "options": ["Defensive", "Curious"]},
    {"id": 19, "quadrant": "feel", "text": "Receiving feedback makes me feel...", "options": ["Criticized", "Valued"]},
    {"id": 20, "quadrant": "feel", "text": "I feel most energized when...", "options": ["Working alone on hard problems", "Helping others succeed"]},
]

class EmpathySubmission(BaseModel):
    user_id: str
    answers: Dict[int, int]

@router.get("/questions")
async def get_questions():
    return {"questions": EMPATHY_QUESTIONS, "total": len(EMPATHY_QUESTIONS), "title": "Team Compatibility Assessment", "instructions": "Choose the statement that resonates most with you", "estimated_time_minutes": 5}

@router.post("/submit")
async def submit_empathy(data: EmpathySubmission):
    if len(data.answers) < 15:
        raise HTTPException(status_code=400, detail="Please answer at least 15 questions")
    empathy_score_raw = sum(data.answers.values())
    empathy_score = (empathy_score_raw / len(data.answers)) * 100
    
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        prompt = f"Empathy score: {empathy_score:.1f}/100. Classify: Visionary (80+), Collaborator (60-79), Analyst (40-59), Individualist (<40). Return JSON: {{'team_role': '...', 'strengths': [...], 'growth_areas': [...], 'best_with': '...'}}"
        result = client.models.generate_content(prompt)
        classification = json.loads(result.text)
    except:
        if empathy_score >= 75:
            role = "Collaborator"
        elif empathy_score >= 50:
            role = "Analyst"
        else:
            role = "Individualist"
        classification = {"team_role": role, "strengths": [], "growth_areas": [], "best_with": ""}
    
    return {"user_id": data.user_id, "empathy_score": round(empathy_score, 1), "team_role": classification.get("team_role"), "strengths": classification.get("strengths", []), "growth_areas": classification.get("growth_areas", []), "best_with": classification.get("best_with", ""), "completed_at": datetime.utcnow().isoformat()}

