from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

EMPATHY_QUESTIONS = [
    {
        "id": "eq1",
        "text": "How often do you consider others' feelings before making decisions?",
        "type": "scale",  # 1-5 scale
        "weight": 5
    },
    {
        "id": "eq2",
        "text": "Describe a time you helped someone without expecting anything in return.",
        "type": "text",
        "weight": 8
    },
    {
        "id": "eq3",
        "text": "Rate your ability to understand different perspectives.",
        "type": "scale",
        "weight": 6
    },
    {
        "id": "eq4",
        "text": "How do you typically respond when a colleague is upset?",
        "type": "multiple_choice",
        "options": [
            "Listen actively and offer support",
            "Give practical advice",
            "Change the subject",
            "Avoid the situation"
        ],
        "weight": 7
    },
    # ... 16 more questions to reach 20 total
]

class EmpathyAnalyzer:
    """Analyzes empathy responses using Gemini Pro"""
    
    def __init__(self, genai_client):
        self.client = genai_client
        
    async def analyze_empathy(self, user_id: str, responses: Dict) -> Dict:
        """Calculate empathy score (0-100) from responses"""
        
        # Step 1: Calculate base score from scale questions
        scale_score = self._calculate_scale_score(responses)
        
        # Step 2: Analyze text responses with Gemini
        text_score = await self._analyze_text_responses(responses)
        
        # Step 3: Score multiple choice
        choice_score = self._calculate_choice_score(responses)
        
        # Weighted average
        empathy_score = (
            scale_score * 0.3 +
            text_score * 0.5 +
            choice_score * 0.2
        )
        
        # Determine empathy level
        if empathy_score >= 80:
            level = "Highly Empathetic"
        elif empathy_score >= 60:
            level = "Empathetic"
        elif empathy_score >= 40:
            level = "Moderately Empathetic"
        else:
            level = "Developing Empathy"
        
        return {
            "user_id": user_id,
            "empathy_score": round(empathy_score, 1),
            "empathy_level": level,
            "breakdown": {
                "emotional_awareness": scale_score,
                "perspective_taking": text_score,
                "compassionate_action": choice_score
            }
        }
    
    def _calculate_scale_score(self, responses: Dict) -> float:
        """Score 1-5 scale questions"""
        scale_questions = [q for q in EMPATHY_QUESTIONS if q["type"] == "scale"]
        total_score = 0
        max_score = 0
        
        for q in scale_questions:
            if q["id"] in responses:
                total_score += responses[q["id"]] * q["weight"]
                max_score += 5 * q["weight"]
        
        return (total_score / max_score * 100) if max_score > 0 else 0
    
    async def _analyze_text_responses(self, responses: Dict) -> float:
        """Use Gemini to score text responses"""
        text_questions = [q for q in EMPATHY_QUESTIONS if q["type"] == "text"]
        
        prompt = f"""
        Analyze the following empathy-related responses on a scale of 0-100:
        
        {json.dumps({q["text"]: responses.get(q["id"], "") for q in text_questions}, indent=2)}
        
        Rate empathy based on:
        - Depth of emotional understanding
        - Perspective-taking ability
        - Genuine compassion shown
        
        Return only a number between 0-100.
        """
        
        response = await self.client.generate(prompt)
        return float(response.strip())
    
    def _calculate_choice_score(self, responses: Dict) -> float:
        """Score multiple choice questions"""
        # Scoring matrix for each question
        choice_scores = {
            "eq4": {
                "Listen actively and offer support": 100,
                "Give practical advice": 70,
                "Change the subject": 30,
                "Avoid the situation": 10
            }
        }
        
        total_score = 0
        count = 0
        
        for q_id, scores in choice_scores.items():
            if q_id in responses:
                total_score += scores.get(responses[q_id], 0)
                count += 1
        
        return total_score / count if count > 0 else 0

