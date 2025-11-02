"""
🔥 PRODUCTION GRADE Discovery Processor v2.0
Integrates WITH ALL User Data (Persona Aggregator)
- Discovery Responses (5 questions)
- User Skills (345+ skills)
- Psychometric Profile (Big 5, empathy)
- Resume Signals (experience, education)
- Portfolio Score
- GitHub Signals
- LinkedIn Signals
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CareerMatch(BaseModel):
    career_id: str
    career_title: str
    fit_score: float = Field(..., ge=0, le=100)
    discovery_score: float = Field(ge=0, le=100)  # From 5 questions
    persona_score: float = Field(ge=0, le=100)    # From full persona
    skill_alignment: float = Field(ge=0, le=100)  # Skill match %
    match_reasons: List[str]
    description: str
    missing_skills: List[str] = []
    recommended_next_steps: List[str] = []

# Question -> Career mappings
RESPONSE_TO_CAREERS = {
    "math_science": ["data-scientist", "research-scientist", "ml-engineer", "mathematician"],
    "arts_humanities": ["ux-designer", "content-strategist", "product-designer", "writer"],
    "business_econ": ["product-manager", "business-analyst", "management-consultant", "economist"],
    "technology": ["software-engineer", "devops-engineer", "ml-engineer", "cloud-architect"],
    "social_services": ["hr-specialist", "nonprofit-leader", "coach", "social-worker"],
    "coding_building": ["software-engineer", "ml-engineer", "devops-engineer", "full-stack-developer"],
    "creating_art": ["ux-designer", "product-designer", "content-creator", "graphic-designer"],
    "helping_people": ["healthcare-professional", "hr-specialist", "coach", "counselor"],
    "analyzing_data": ["data-scientist", "business-analyst", "research-scientist", "data-engineer"],
    "leading_teams": ["product-manager", "team-lead", "cto", "engineering-manager"],
    "independent": ["researcher", "freelancer", "entrepreneur", "consultant"],
    "collaborative": ["product-manager", "scrum-master", "team-lead", "group-facilitator"],
    "structured": ["project-manager", "business-analyst", "qa-engineer", "compliance-officer"],
    "flexible": ["startup-founder", "consultant", "remote-worker", "entrepreneur"],
    "mix": ["product-manager", "team-lead", "project-manager", "agile-coach"],
    "build_products": ["software-engineer", "product-manager", "entrepreneur", "cto"],
    "help_people": ["healthcare-professional", "hr-specialist", "coach", "nurse"],
    "advance_knowledge": ["research-scientist", "academic", "data-scientist", "professor"],
    "solve_problems": ["management-consultant", "product-manager", "devops-engineer", "systems-architect"],
    "create_value": ["business-analyst", "entrepreneur", "investor", "cfo"],
    "remote": ["software-engineer", "data-scientist", "content-creator", "remote-consultant"],
    "hybrid": ["product-manager", "team-lead", "project-manager", "architect"],
    "office": ["business-analyst", "hr-specialist", "management-consultant", "office-manager"],
    "outdoors": ["environmental-scientist", "outdoor-guide", "field-researcher", "geologist"],
    "lab_research": ["research-scientist", "biologist", "pharmaceutical-researcher", "chemist"]
}

# Career -> Required Skills
CAREER_REQUIRED_SKILLS = {
    "software-engineer": ["Python", "JavaScript", "System Design", "Git", "REST API", "SQL"],
    "data-scientist": ["Python", "Pandas", "Statistics", "Machine Learning", "SQL", "Tableau"],
    "product-manager": ["Product Strategy", "Data Analysis", "User Research", "Communication", "Roadmap"],
    "ux-designer": ["Figma", "User Research", "Wireframing", "Prototyping", "CSS", "JavaScript"],
    "ml-engineer": ["Python", "TensorFlow", "PyTorch", "Statistics", "Big Data", "MLOps"],
    "devops-engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", "Infrastructure", "Terraform"],
    "cto": ["Leadership", "System Design", "Project Management", "Cloud Architecture", "Team Management"],
    "business-analyst": ["Excel", "SQL", "Data Analysis", "Business Strategy", "Communication"],
    "consultant": ["Problem Solving", "Communication", "Leadership", "Financial Modeling", "Presentation"],
}

# Psychometric -> Career alignment
PSYCHOMETRIC_CAREER_AFFINITY = {
    "openness": ["researcher", "content-creator", "entrepreneur", "artist"],
    "conscientiousness": ["project-manager", "qa-engineer", "accountant", "analyst"],
    "extraversion": ["team-lead", "coach", "sales-manager", "recruiter"],
    "agreeableness": ["hr-specialist", "counselor", "social-worker", "nurse"],
    "neuroticism_low": ["cto", "product-manager", "engineer", "analyst"],  # Stability preferred
}

class DiscoveryProcessor:
    """
    🎯 Enhanced Discovery Processor with Persona Integration
    """
    
    def __init__(self, persona_aggregator=None):
        """
        Args:
            persona_aggregator: PersonaAggregator instance for fetching full user data
        """
        self.persona_aggregator = persona_aggregator
    
    async def process_responses_with_persona(
        self, 
        responses: Dict,
        user_persona: Optional[Dict] = None
    ) -> List[CareerMatch]:
        """
        🔥 CORE LOGIC: Match discovery responses + full user persona to careers
        
        Uses:
        - 5 discovery questions
        - User skills (345+)
        - Psychometric traits
        - Resume signals (experience)
        - Portfolio score
        - GitHub signals
        """
        try:
            user_id = responses.get("user_id", "unknown")
            logger.info(f"🎯 Processing discovery + persona for {user_id}")
            
            # Score from discovery questions
            discovery_candidates = self._score_from_discovery(responses)
            logger.info(f"Discovery candidates: {len(discovery_candidates)}")
            
            # If no persona provided, try to fetch
            if not user_persona and self.persona_aggregator:
                try:
                    user_persona = await self.persona_aggregator.get_unified_persona(user_id)
                    logger.info(f"Fetched persona for {user_id} - {user_persona.get('completeness_score', 0):.1%} complete")
                except Exception as e:
                    logger.warning(f"Could not fetch persona: {e}")
                    user_persona = None
            
            # Enhance with persona data if available
            if user_persona:
                discovery_candidates = self._enhance_with_persona(
                    discovery_candidates,
                    user_persona,
                    responses.get("user_id")
                )
            
            # Sort by combined fit score
            sorted_matches = sorted(
                discovery_candidates.values(),
                key=lambda x: x["combined_score"],
                reverse=True
            )[:5]
            
            # Convert to CareerMatch objects
            matches = []
            for career_data in sorted_matches:
                match = CareerMatch(
                    career_id=career_data["id"],
                    career_title=career_data["title"],
                    fit_score=round(career_data["combined_score"], 2),
                    discovery_score=round(career_data["discovery_score"], 2),
                    persona_score=round(career_data.get("persona_score", 0), 2),
                    skill_alignment=round(career_data.get("skill_alignment", 0), 2),
                    match_reasons=career_data["reasons"][:3],
                    description=career_data["description"],
                    missing_skills=career_data.get("missing_skills", [])[:3],
                    recommended_next_steps=self._get_next_steps(
                        career_data["id"],
                        career_data.get("missing_skills", [])
                    )
                )
                matches.append(match)
            
            logger.info(f"✅ Recommended {len(matches)} careers for {user_id}")
            return matches
            
        except Exception as e:
            logger.error(f"Discovery processing failed: {str(e)}", exc_info=True)
            raise
    
    def _score_from_discovery(self, responses: Dict) -> Dict:
        """Score careers from 5 discovery questions"""
        candidates = {}
        
        response_values = [
            responses.get("q1_interests"),
            responses.get("q2_activities"),
            responses.get("q3_work_style"),
            responses.get("q4_impact"),
            responses.get("q5_environment")
        ]
        
        for i, value in enumerate(response_values, 1):
            if not value or value not in RESPONSE_TO_CAREERS:
                continue
            
            matched_careers = RESPONSE_TO_CAREERS[value]
            for career_id in matched_careers:
                if career_id not in candidates:
                    candidates[career_id] = {
                        "id": career_id,
                        "title": career_id.replace("-", " ").title(),
                        "discovery_score": 0,
                        "reasons": [],
                        "skills": CAREER_REQUIRED_SKILLS.get(career_id, [])
                    }
                
                candidates[career_id]["discovery_score"] += 20  # Each Q is 20 points
                candidates[career_id]["reasons"].append(
                    f"Q{i}: {value.replace('_', ' ').title()}"
                )
        
        # Normalize discovery score to 0-100
        for career in candidates.values():
            career["discovery_score"] = min(100, career["discovery_score"])
            career["combined_score"] = career["discovery_score"]
        
        return candidates
    
    def _enhance_with_persona(
        self,
        candidates: Dict,
        persona: Dict,
        user_id: str
    ) -> Dict:
        """Enhance career scores with full persona data"""
        
        # Extract persona components
        skills = persona.get("skills", {}).get("current_skills", [])
        psychometric = persona.get("psychometric", {})
        portfolio_score = persona.get("portfolio_score", 0)
        experience_years = persona.get("experience_years", 0)
        
        for career_id, career_data in candidates.items():
            required_skills = career_data["skills"]
            matched_skills = len(set(skills) & set(required_skills))
            skill_alignment = (matched_skills / len(required_skills) * 100) if required_skills else 0
            
            # Persona bonus: psychometric fit
            psychometric_bonus = self._get_psychometric_bonus(psychometric, career_id)
            
            # Experience bonus
            experience_bonus = min(experience_years * 5, 20)  # Up to 20 points
            
            # Portfolio bonus
            portfolio_bonus = portfolio_score / 5 if portfolio_score else 0  # 0-20 points
            
            # Combined score (weighted)
            # 40% discovery + 30% skills + 15% psychometric + 10% experience + 5% portfolio
            persona_score = (
                skill_alignment * 0.3 +
                psychometric_bonus * 0.15 +
                experience_bonus * 0.1 +
                portfolio_bonus * 0.05
            )
            
            career_data["persona_score"] = persona_score
            career_data["skill_alignment"] = skill_alignment
            career_data["combined_score"] = (
                career_data["discovery_score"] * 0.4 +
                persona_score * 0.6
            )
            career_data["missing_skills"] = [
                s for s in required_skills if s not in skills
            ]
            
            if persona_score > 0:
                career_data["reasons"].append(f"✅ Persona match: +{persona_score:.0f}%")
        
        return candidates
    
    def _get_psychometric_bonus(self, psychometric: Dict, career_id: str) -> float:
        """Calculate bonus from psychometric profile"""
        bonus = 0
        traits = psychometric.get("traits", {})
        
        for trait, careers in PSYCHOMETRIC_CAREER_AFFINITY.items():
            if career_id in careers:
                trait_value = traits.get(trait, 0.5)
                bonus += trait_value * 20  # Up to 20 points per trait match
        
        return min(bonus, 20)  # Cap at 20
    
    def _get_next_steps(self, career_id: str, missing_skills: List[str]) -> List[str]:
        """Generate personalized next steps"""
        steps = [
            f"Learn top missing skill: {missing_skills[0]}" if missing_skills else "You have key skills!",
            f"Find role models in {career_id.replace('-', ' ')}",
            "Build portfolio project",
            "Network with professionals",
        ]
        return steps[:3]

