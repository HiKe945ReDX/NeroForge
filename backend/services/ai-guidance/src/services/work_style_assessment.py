"""
🎯 DISCOVER YOUR WORK STYLE - 25 Conversational Questions
Big Five Personality + Work Style Analysis
Production-ready for Guidora
"""
from typing import Dict, List
from pydantic import BaseModel

class WorkStyleQuestion(BaseModel):
    id: int
    text: str
    trait: str  # openness, conscientiousness, extraversion, agreeableness, neuroticism
    reverse_scored: bool = False

# 25 RELATABLE, CONVERSATIONAL QUESTIONS
WORK_STYLE_QUESTIONS: List[Dict] = [
    # Extraversion (5 questions)
    {"id": 1, "text": "I enjoy working in teams and collaborating with others", "trait": "extraversion", "reverse": False},
    {"id": 2, "text": "I prefer working independently rather than in groups", "trait": "extraversion", "reverse": True},
    {"id": 3, "text": "I feel energized after networking events or team meetings", "trait": "extraversion", "reverse": False},
    {"id": 4, "text": "I tend to be quiet in group settings", "trait": "extraversion", "reverse": True},
    {"id": 5, "text": "I enjoy leading discussions and presenting ideas", "trait": "extraversion", "reverse": False},
    
    # Conscientiousness (5 questions)
    {"id": 6, "text": "I always plan ahead before starting a new project", "trait": "conscientiousness", "reverse": False},
    {"id": 7, "text": "I often leave tasks unfinished", "trait": "conscientiousness", "reverse": True},
    {"id": 8, "text": "I pay close attention to details", "trait": "conscientiousness", "reverse": False},
    {"id": 9, "text": "I prefer to keep my workspace organized", "trait": "conscientiousness", "reverse": False},
    {"id": 10, "text": "I sometimes procrastinate on important tasks", "trait": "conscientiousness", "reverse": True},
    
    # Openness (5 questions)
    {"id": 11, "text": "I enjoy learning new skills and exploring new ideas", "trait": "openness", "reverse": False},
    {"id": 12, "text": "I prefer routine and familiar tasks", "trait": "openness", "reverse": True},
    {"id": 13, "text": "I'm comfortable adapting to changes in plans", "trait": "openness", "reverse": False},
    {"id": 14, "text": "I enjoy creative problem-solving", "trait": "openness", "reverse": False},
    {"id": 15, "text": "I stick to traditional methods rather than trying new approaches", "trait": "openness", "reverse": True},
    
    # Agreeableness (5 questions)
    {"id": 16, "text": "I value harmony and avoid conflicts with teammates", "trait": "agreeableness", "reverse": False},
    {"id": 17, "text": "I'm comfortable challenging others' ideas", "trait": "agreeableness", "reverse": True},
    {"id": 18, "text": "I enjoy helping colleagues solve their problems", "trait": "agreeableness", "reverse": False},
    {"id": 19, "text": "I prioritize team success over individual recognition", "trait": "agreeableness", "reverse": False},
    {"id": 20, "text": "I tend to be direct and assertive in discussions", "trait": "agreeableness", "reverse": True},
    
    # Neuroticism/Emotional Stability (5 questions)
    {"id": 21, "text": "I stay calm under pressure and tight deadlines", "trait": "neuroticism", "reverse": True},
    {"id": 22, "text": "I often worry about work-related tasks", "trait": "neuroticism", "reverse": False},
    {"id": 23, "text": "I handle criticism and feedback well", "trait": "neuroticism", "reverse": True},
    {"id": 24, "text": "I get stressed when things don't go as planned", "trait": "neuroticism", "reverse": False},
    {"id": 25, "text": "I maintain a positive outlook even during challenges", "trait": "neuroticism", "reverse": True}
]

def calculate_scores(answers: Dict[int, int]) -> Dict[str, float]:
    """
    Calculate Big Five trait scores from answers
    answers: {question_id: score (1-5)}
    Returns: {trait: score (0-100)}
    """
    trait_scores = {
        "extraversion": [],
        "conscientiousness": [],
        "openness": [],
        "agreeableness": [],
        "neuroticism": []
    }
    
    for question in WORK_STYLE_QUESTIONS:
        qid = question["id"]
        if qid not in answers:
            continue
        
        score = answers[qid]
        trait = question["trait"]
        
        # Reverse score if needed
        if question["reverse"]:
            score = 6 - score  # 1->5, 2->4, 3->3, 4->2, 5->1
        
        trait_scores[trait].append(score)
    
    # Average and convert to 0-100 scale
    final_scores = {}
    for trait, scores in trait_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            final_scores[trait] = round((avg - 1) * 25, 1)  # Scale 1-5 to 0-100
        else:
            final_scores[trait] = 50.0  # Default to middle
    
    return final_scores

def get_work_style_profile(scores: Dict[str, float]) -> Dict[str, str]:
    """Generate work style profile from scores"""
    profile = {}
    
    # Extraversion
    if scores["extraversion"] >= 70:
        profile["social_style"] = "Team Player - You thrive in collaborative environments"
    elif scores["extraversion"] >= 40:
        profile["social_style"] = "Balanced - You adapt well to solo or team work"
    else:
        profile["social_style"] = "Independent Contributor - You excel in focused, solo work"
    
    # Conscientiousness
    if scores["conscientiousness"] >= 70:
        profile["work_approach"] = "Structured Planner - You excel at organization and follow-through"
    elif scores["conscientiousness"] >= 40:
        profile["work_approach"] = "Flexible Executor - You balance planning with adaptability"
    else:
        profile["work_approach"] = "Spontaneous Creator - You thrive with flexibility and freedom"
    
    # Openness
    if scores["openness"] >= 70:
        profile["learning_style"] = "Innovative Explorer - You love learning and trying new approaches"
    elif scores["openness"] >= 40:
        profile["learning_style"] = "Pragmatic Learner - You balance new ideas with proven methods"
    else:
        profile["learning_style"] = "Consistent Specialist - You master established techniques"
    
    # Agreeableness
    if scores["agreeableness"] >= 70:
        profile["team_role"] = "Collaborative Supporter - You build consensus and help others"
    elif scores["agreeableness"] >= 40:
        profile["team_role"] = "Balanced Contributor - You collaborate while maintaining independence"
    else:
        profile["team_role"] = "Direct Leader - You drive results and challenge status quo"
    
    # Neuroticism (inverted to Emotional Stability)
    stability = 100 - scores["neuroticism"]
    if stability >= 70:
        profile["stress_management"] = "Calm Under Pressure - You maintain composure in challenges"
    elif stability >= 40:
        profile["stress_management"] = "Resilient Adapter - You manage stress effectively"
    else:
        profile["stress_management"] = "Mindful Responder - You benefit from structured support"
    
    return profile

def get_career_recommendations(scores: Dict[str, float]) -> List[str]:
    """Recommend careers based on personality profile"""
    recommendations = []
    
    # High Extraversion + High Conscientiousness
    if scores["extraversion"] >= 60 and scores["conscientiousness"] >= 60:
        recommendations.extend(["Product Manager", "Sales Engineer", "Team Lead"])
    
    # High Openness + High Conscientiousness
    if scores["openness"] >= 60 and scores["conscientiousness"] >= 60:
        recommendations.extend(["Software Architect", "Data Scientist", "UX Researcher"])
    
    # Low Extraversion + High Conscientiousness
    if scores["extraversion"] < 40 and scores["conscientiousness"] >= 60:
        recommendations.extend(["Backend Engineer", "Data Analyst", "Quality Assurance"])
    
    # High Extraversion + High Agreeableness
    if scores["extraversion"] >= 60 and scores["agreeableness"] >= 60:
        recommendations.extend(["Customer Success", "HR Manager", "Teacher"])
    
    # High Openness + Low Neuroticism
    if scores["openness"] >= 60 and scores["neuroticism"] < 40:
        recommendations.extend(["Entrepreneur", "Creative Director", "Innovation Consultant"])
    
    # Fallback recommendations
    if not recommendations:
        recommendations = ["Full-Stack Developer", "Business Analyst", "Project Manager"]
    
    return list(set(recommendations))[:5]  # Return max 5 unique recommendations
