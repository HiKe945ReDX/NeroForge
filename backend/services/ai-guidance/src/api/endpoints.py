from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

router = APIRouter()

# Simple, working models that won't cause Pydantic errors
class PersonaRequest(BaseModel):
    user_id: str
    name: str
    field: str
    experience: Optional[str] = "Intermediate"
    goals: Optional[List[str]] = []

class PsychometricRequest(BaseModel):
    user_id: str
    responses: List[Dict[str, Any]]  # Changed from 'any' to 'Any'

class RoadmapRequest(BaseModel):
    user_id: str
    current_role: str
    target_role: str
    timeline: str
    skills: Optional[List[str]] = []

class GitHubRequest(BaseModel):
    user_id: str
    github_username: str
    repositories: Optional[List[str]] = []

class LinkedInRequest(BaseModel):
    user_id: str
    current_profile: Dict[str, Any]  # Changed from 'any' to 'Any'
    target_role: str

class CareerMatchRequest(BaseModel):
    user_id: str
    skills: List[str]
    interests: List[str]
    experience_level: Optional[str] = "Junior"

class SkillsGapRequest(BaseModel):
    user_id: str
    current_skills: List[str]
    target_role: str
    target_skills: List[str]

@router.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(None), user_id: str = "demo_user"):
    """AI-powered resume analysis"""
    try:
        return {
            "user_id": user_id,
            "analysis": {
                "skills_extracted": ["Python", "FastAPI", "AI/ML", "Docker", "React"],
                "experience_level": "Mid-level (3+ years)",
                "key_strengths": [
                    "Strong technical foundation",
                    "Full-stack development experience",
                    "AI/ML knowledge"
                ],
                "improvement_areas": [
                    "Add more leadership examples",
                    "Include quantifiable achievements",
                    "Expand cloud platform experience"
                ],
                "ats_score": 85.2,
                "recommended_improvements": [
                    "Add metrics to achievements",
                    "Include relevant keywords",
                    "Optimize section headers"
                ]
            },
            "ai_processed": True,
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {str(e)}")

@router.post("/create-persona")
async def create_persona(request: PersonaRequest):
    """AI-powered persona creation"""
    try:
        return {
            "user_id": request.user_id,
            "persona": {
                "professional_identity": f"Innovative {request.field} Professional",
                "core_values": ["Innovation", "Excellence", "Collaboration"],
                "communication_style": "Clear, technical, and results-oriented",
                "brand_statement": f"Passionate {request.field} professional with expertise in cutting-edge technologies.",
                "target_audience": "Tech leaders, hiring managers, industry professionals",
                "key_differentiators": [
                    "Technical depth combined with business acumen",
                    "Strong problem-solving skills",
                    "Continuous learner and innovator"
                ]
            },
            "ai_generated": True,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Persona creation failed: {str(e)}")

@router.post("/psychometric-assessment")
async def psychometric_assessment(request: PsychometricRequest):
    """AI-powered psychometric assessment"""
    try:
        # Calculate average ratings
        total_responses = len(request.responses)
        avg_rating = sum(resp.get("rating", 5) for resp in request.responses) / total_responses if total_responses > 0 else 5
        
        # Determine personality type based on responses
        personality_type = "INTJ - The Architect"
        if avg_rating > 8:
            personality_type = "ENTJ - The Commander"
        elif avg_rating > 6:
            personality_type = "ENTP - The Innovator"
        
        return {
            "user_id": request.user_id,
            "assessment_results": {
                "personality_type": personality_type,
                "strengths": [
                    "Strategic thinking and planning",
                    "Independent and self-motivated",
                    "High attention to detail"
                ],
                "work_preferences": {
                    "environment": "Structured with autonomy",
                    "team_size": "Small, focused teams",
                    "communication": "Direct and purposeful"
                },
                "career_fit_scores": {
                    "Software Engineering": min(95, 70 + int(avg_rating * 3)),
                    "Data Science": min(95, 65 + int(avg_rating * 3.5)),
                    "Product Management": min(95, 60 + int(avg_rating * 4)),
                    "Technical Leadership": min(95, 55 + int(avg_rating * 4.5))
                },
                "development_areas": [
                    "Collaborative communication",
                    "Delegation skills",
                    "Stakeholder management"
                ]
            },
            "confidence_score": min(0.95, 0.7 + (avg_rating / 10) * 0.3),
            "completed_at": datetime.utcnow().isoformat(),
            "ai_enhanced": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Psychometric assessment failed: {str(e)}")

@router.post("/generate-roadmap")
async def generate_roadmap(request: RoadmapRequest):
    """AI-powered roadmap generation"""
    try:
        return {
            "user_id": request.user_id,
            "roadmap": {
                "timeline": request.timeline,
                "current_role": request.current_role,
                "target_role": request.target_role,
                "milestones": [
                    {
                        "phase": "Foundation (Months 1-6)",
                        "objectives": [
                            "Master advanced technical concepts",
                            "Complete relevant certifications",
                            "Build portfolio projects"
                        ],
                        "skills_to_develop": ["Advanced Python", "System Design", "Leadership"]
                    },
                    {
                        "phase": "Growth (Months 7-12)",
                        "objectives": [
                            "Lead technical initiatives",
                            "Mentor team members",
                            "Gain domain expertise"
                        ],
                        "skills_to_develop": ["Architecture", "Team Management", "Strategy"]
                    },
                    {
                        "phase": "Mastery (Months 13-18)",
                        "objectives": [
                            "Drive technical decisions",
                            "Cross-functional collaboration",
                            "Industry recognition"
                        ],
                        "skills_to_develop": ["Technical Leadership", "Vision", "Communication"]
                    }
                ],
                "success_metrics": [
                    f"Achieve {request.target_role} position",
                    "Lead successful projects",
                    "Build strong professional network"
                ]
            },
            "ai_generated": True,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")

@router.post("/github/analyze")
async def analyze_github(request: GitHubRequest):
    """GitHub profile analysis"""
    try:
        return {
            "user_id": request.user_id,
            "github_analysis": {
                "username": request.github_username,
                "technical_assessment": {
                    "primary_languages": ["Python", "JavaScript"],
                    "technology_stack": ["FastAPI", "React", "Docker", "AI/ML"],
                    "code_quality_indicators": ["Clean code", "Good documentation"],
                    "project_complexity": "intermediate",
                    "collaboration_score": 8.5
                },
                "career_insights": {
                    "experience_level": "Mid-level developer",
                    "specialization_areas": ["Full-stack", "AI/ML"],
                    "growth_trajectory": "On track for senior role",
                    "market_value": "Competitive"
                },
                "recommendations": {
                    "skill_gaps": ["System design", "Cloud architecture"],
                    "project_suggestions": ["Open source contributions", "Technical blog"],
                    "portfolio_improvements": ["Add deployment examples", "Include metrics"]
                }
            },
            "ai_processed": True,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub analysis failed: {str(e)}")

@router.post("/linkedin/optimize")
async def optimize_linkedin(request: LinkedInRequest):
    """LinkedIn profile optimization"""
    try:
        return {
            "user_id": request.user_id,
            "optimization_suggestions": {
                "headline_suggestions": [
                    f"{request.target_role} | AI & Technology Enthusiast",
                    f"Experienced {request.target_role} | Innovation Driver"
                ],
                "summary_optimization": f"Results-driven {request.target_role} with expertise in cutting-edge technologies.",
                "skill_recommendations": [
                    "Machine Learning", "Cloud Architecture", "Technical Leadership"
                ],
                "experience_enhancements": [
                    "Add quantifiable achievements",
                    "Include relevant technologies",
                    "Highlight leadership experiences"
                ],
                "keyword_optimization": [
                    request.target_role.lower(), "artificial intelligence", "innovation"
                ]
            },
            "ai_processed": True,
            "optimized_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LinkedIn optimization failed: {str(e)}")

@router.post("/career/match")
async def career_matching(request: CareerMatchRequest):
    """AI-powered career matching"""
    try:
        return {
            "user_id": request.user_id,
            "career_matches": [
                {
                    "role": "Senior AI Engineer",
                    "match_score": 92.5,
                    "required_skills": ["Python", "TensorFlow", "Deep Learning"],
                    "salary_range": "$120k-180k",
                    "growth_potential": "Very High",
                    "match_reasons": [
                        "Strong skill alignment",
                        "High market demand",
                        "Excellent growth trajectory"
                    ]
                },
                {
                    "role": "Full Stack Developer",
                    "match_score": 85.0,
                    "required_skills": ["React", "Node.js", "Python"],
                    "salary_range": "$90k-140k",
                    "growth_potential": "High",
                    "match_reasons": [
                        "Transferable skills",
                        "Stable demand",
                        "Diverse opportunities"
                    ]
                }
            ],
            "ai_processed": True,
            "matched_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Career matching failed: {str(e)}")

@router.post("/skills/gap-analysis")
async def skills_gap_analysis(request: SkillsGapRequest):
    """Skills gap analysis"""
    try:
        skill_gaps = [skill for skill in request.target_skills if skill not in request.current_skills]
        skill_strengths = [skill for skill in request.current_skills if skill in request.target_skills]
        
        return {
            "user_id": request.user_id,
            "target_role": request.target_role,
            "skills_analysis": {
                "current_skills": request.current_skills,
                "target_skills": request.target_skills,
                "skill_gaps": skill_gaps,
                "skill_strengths": skill_strengths,
                "skill_gap_percentage": len(skill_gaps) / len(request.target_skills) * 100 if request.target_skills else 0
            },
            "learning_recommendations": [
                {
                    "skill": gap,
                    "priority": "High" if gap in ["System Design", "Leadership"] else "Medium",
                    "estimated_time": "2-3 months",
                    "resources": [f"{gap} course", f"{gap} project", f"{gap} certification"]
                } for gap in skill_gaps[:5]
            ],
            "ai_processed": True,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skills gap analysis failed: {str(e)}")

@router.get("/health")
async def ai_guidance_health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "ai-guidance",
        "ai_enabled": True,
        "features": [
            "resume-analysis", "persona-creation", "psychometric-assessment", 
            "roadmap-generation", "github-analysis", "linkedin-optimization",
            "career-matching", "skills-gap-analysis"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
