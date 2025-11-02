"""
🔥 GUIDORA CONTEXT SERVICE - ULTIMATE PERSONA AGGREGATOR
Production-grade implementation with intelligent fallbacks & caching
Generated: Oct 30, 2025 01:08 AM IST
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

logger = logging.getLogger(__name__)

class PersonaAggregator:
    """
    Aggregates user data from multiple sources into unified persona
    Handles missing data gracefully with intelligent fallbacks
    """
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.get_database("guidora_db")
        self.users = self.db.users
        self.resumes = self.db.resumes
        self.github = self.db.github_profiles
        self.linkedin = self.db.linkedin_profiles
        self.psychometric = self.db.psychometric_results
        self.empathy = self.db.empathy_results
        self.preferences = self.db.career_preferences
        self.cache = {}  # In-memory cache for 15min
        
    async def get_unified_persona(self, user_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Aggregate all user data sources into comprehensive persona
        Returns: Complete profile for AI roadmap generation & matching
        """
        try:
            # Check cache (15min TTL)
            if not force_refresh and user_id in self.cache:
                cached_data, cached_time = self.cache[user_id]
                if datetime.utcnow() - cached_time < timedelta(minutes=15):
                    logger.info(f"✅ Returning cached persona for {user_id}")
                    return cached_data
            
            logger.info(f"🔍 Fetching fresh persona data for {user_id}")
            
            # Fetch all data sources in parallel (non-blocking)
            results = await asyncio.gather(
                self.users.find_one({"user_id": user_id}),
                self.resumes.find_one({"user_id": user_id}),
                self.github.find_one({"user_id": user_id}),
                self.linkedin.find_one({"user_id": user_id}),
                self.psychometric.find_one({"user_id": user_id}),
                self.empathy.find_one({"user_id": user_id}),
                self.preferences.find_one({"user_id": user_id}),
                return_exceptions=True
            )
            
            user_data, resume_data, github_data, linkedin_data, psychometric_data, empathy_data, prefs_data = results
            
            # Build unified persona with intelligent defaults
            persona = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "completeness_score": 0.0,
                "readiness_tier": "beginner",  # beginner/intermediate/advanced
                "data_sources": {
                    "user": bool(user_data and not isinstance(user_data, Exception)),
                    "resume": bool(resume_data and not isinstance(resume_data, Exception)),
                    "github": bool(github_data and not isinstance(github_data, Exception)),
                    "linkedin": bool(linkedin_data and not isinstance(linkedin_data, Exception)),
                    "psychometric": bool(psychometric_data and not isinstance(psychometric_data, Exception)),
                    "empathy": bool(empathy_data and not isinstance(empathy_data, Exception)),
                    "preferences": bool(prefs_data and not isinstance(prefs_data, Exception))
                },
                
                # BASIC INFO
                "basic_info": self._extract_basic_info(user_data),
                
                # SKILLS AGGREGATION (from all sources)
                "skills": await self._aggregate_skills(resume_data, github_data, linkedin_data),
                
                # EXPERIENCE SUMMARY
                "experience": self._aggregate_experience(resume_data, linkedin_data),
                
                # PERSONALITY TRAITS (Big Five + Empathy)
                "personality": self._aggregate_personality(psychometric_data, empathy_data),
                
                # CAREER FIT INDICATORS
                "career_fit": await self._calculate_career_fit(
                    resume_data, github_data, linkedin_data, 
                    psychometric_data, empathy_data, prefs_data
                ),
                
                # LEARNING PREFERENCES (inferred from psychometric + education level)
                "learning_preferences": self._infer_learning_style(
                    psychometric_data, empathy_data, user_data
                ),
                
                # CAREER PREFERENCES (from Step 6)
                "career_preferences": self._extract_career_prefs(prefs_data),
                
                # PORTFOLIO SCORE (0-100)
                "portfolio_score": 0,
                
                # RECOMMENDATIONS (AI-suggested careers)
                "recommended_careers": []
            }
            
            # Calculate completeness (0.0 - 1.0)
            persona["completeness_score"] = self._calculate_completeness(persona)
            
            # Calculate portfolio score (0-100)
            persona["portfolio_score"] = self._calculate_portfolio_score(persona)
            
            # Determine readiness tier
            persona["readiness_tier"] = self._determine_tier(persona["portfolio_score"])
            
            # Cache result
            self.cache[user_id] = (persona, datetime.utcnow())
            
            logger.info(f"✅ Persona aggregated for {user_id}: {persona['completeness_score']:.1%} complete, {persona['portfolio_score']}/100 portfolio score")
            return persona
            
        except Exception as e:
            logger.error(f"❌ Error aggregating persona for {user_id}: {e}")
            return {
                "error": str(e),
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _extract_basic_info(self, user_data) -> Dict[str, Any]:
        """Extract basic user info with fallbacks"""
        if not user_data or isinstance(user_data, Exception):
            return {
                "name": "Unknown",
                "email": "not_provided@example.com",
                "education_level": "Unknown",
                "current_role": "Unknown",
                "phone": None
            }
        
        return {
            "name": user_data.get("name", "Unknown"),
            "email": user_data.get("email", "not_provided@example.com"),
            "education_level": user_data.get("education_level", "Unknown"),
            "current_role": user_data.get("current_role") or user_data.get("current_field", "Unknown"),
            "phone": user_data.get("phone")
        }
    
    async def _aggregate_skills(self, resume_data, github_data, linkedin_data) -> Dict[str, Any]:
        """Combine skills from all sources with deduplication"""
        technical_skills = set()
        soft_skills = set()
        domain_skills = set()
        
        # From resume
        if resume_data and not isinstance(resume_data, Exception):
            technical_skills.update(resume_data.get("technical_skills", []))
            soft_skills.update(resume_data.get("soft_skills", []))
            domain_skills.update(resume_data.get("domain_skills", []))
        
        # From GitHub (languages & technologies)
        if github_data and not isinstance(github_data, Exception):
            technical_skills.update(github_data.get("languages", []))
            technical_skills.update(github_data.get("technologies", []))
        
        # From LinkedIn
        if linkedin_data and not isinstance(linkedin_data, Exception):
            all_linkedin_skills = linkedin_data.get("skills", [])
            # Intelligent categorization
            for skill in all_linkedin_skills:
                if any(tech in skill.lower() for tech in ['python', 'java', 'react', 'aws', 'sql', 'docker']):
                    technical_skills.add(skill)
                else:
                    soft_skills.add(skill)
        
        return {
            "technical": sorted(list(technical_skills))[:50],  # Max 50 to avoid bloat
            "soft": sorted(list(soft_skills))[:30],
            "domain": sorted(list(domain_skills))[:20],
            "total_count": len(technical_skills) + len(soft_skills) + len(domain_skills),
            "technical_depth": len(technical_skills),
            "soft_depth": len(soft_skills)
        }
    
    def _aggregate_experience(self, resume_data, linkedin_data) -> Dict[str, Any]:
        """Combine experience data with intelligent parsing"""
        experience_years = 0
        roles = []
        companies = set()
        industries = set()
        
        if resume_data and not isinstance(resume_data, Exception):
            experience_years = resume_data.get("years_of_experience", 0)
            roles.extend(resume_data.get("work_experience", []))
            for exp in resume_data.get("work_experience", []):
                if "company" in exp:
                    companies.add(exp["company"])
                if "industry" in exp:
                    industries.add(exp["industry"])
        
        if linkedin_data and not isinstance(linkedin_data, Exception):
            linkedin_roles = linkedin_data.get("positions", [])
            roles.extend(linkedin_roles)
            for role in linkedin_roles:
                if "company" in role:
                    companies.add(role["company"])
                if "industry" in role:
                    industries.add(role["industry"])
        
        return {
            "years": experience_years,
            "roles_count": len(roles),
            "recent_roles": roles[:3] if roles else [],
            "companies": sorted(list(companies)),
            "industries": sorted(list(industries)),
            "has_experience": experience_years > 0 or len(roles) > 0
        }
    
    def _aggregate_personality(self, psychometric_data, empathy_data) -> Dict[str, Any]:
        """Combine personality assessments"""
        personality = {
            "big_five": {},
            "empathy_score": 0,
            "empathy_level": "Unknown",
            "team_role": "Unknown",
            "work_style": "Unknown"
        }
        
        if psychometric_data and not isinstance(psychometric_data, Exception):
            personality["big_five"] = psychometric_data.get("scores", {})
            personality["work_style"] = psychometric_data.get("work_style_summary", "Unknown")
        
        if empathy_data and not isinstance(empathy_data, Exception):
            personality["empathy_score"] = empathy_data.get("total_score", 0)
            personality["empathy_level"] = empathy_data.get("empathy_level", "Unknown")
            personality["team_role"] = empathy_data.get("team_role", "Unknown")
        
        return personality
    
    async def _calculate_career_fit(self, resume_data, github_data, linkedin_data, 
                                   psychometric_data, empathy_data, prefs_data) -> Dict[str, Any]:
        """Calculate career fit indicators with intelligent scoring"""
        fit_score = 0.0
        indicators = []
        recommendations = []
        
        # Technical depth (20 points)
        if github_data and not isinstance(github_data, Exception):
            commits = github_data.get("total_commits", 0)
            repos = github_data.get("total_repos", 0)
            if commits > 500:
                fit_score += 0.20
                indicators.append("🔥 Strong technical activity (500+ commits)")
            elif commits > 100:
                fit_score += 0.15
                indicators.append("💻 Moderate technical activity (100+ commits)")
        
        # Professional experience (20 points)
        if resume_data and not isinstance(resume_data, Exception):
            years = resume_data.get("years_of_experience", 0)
            if years >= 5:
                fit_score += 0.20
                indicators.append("🎖️ Extensive experience (5+ years)")
            elif years >= 2:
                fit_score += 0.15
                indicators.append("📈 Solid experience (2+ years)")
            elif years >= 1:
                fit_score += 0.10
                indicators.append("🌱 Some experience (1+ year)")
        
        # Personality alignment (20 points)
        if psychometric_data and not isinstance(psychometric_data, Exception):
            scores = psychometric_data.get("scores", {})
            conscientiousness = scores.get("conscientiousness", 0)
            openness = scores.get("openness", 0)
            
            if conscientiousness > 4.0:
                fit_score += 0.15
                indicators.append("⚡ Strong work ethic (high conscientiousness)")
            if openness > 4.0:
                fit_score += 0.05
                indicators.append("🌟 Open to learning (high openness)")
        
        # Empathy for people-facing roles (20 points)
        if empathy_data and not isinstance(empathy_data, Exception):
            empathy_score = empathy_data.get("total_score", 0)
            if empathy_score > 75:
                fit_score += 0.20
                indicators.append("❤️ High emotional intelligence (75+ empathy)")
                recommendations.extend(["Product Manager", "UX Designer", "Healthcare Professional", "Teacher"])
            elif empathy_score > 60:
                fit_score += 0.15
                indicators.append("🤝 Good emotional intelligence (60+ empathy)")
        
        # Network strength (10 points)
        if linkedin_data and not isinstance(linkedin_data, Exception):
            connections = linkedin_data.get("connections", 0)
            if connections > 500:
                fit_score += 0.10
                indicators.append("🌐 Strong professional network (500+ connections)")
            elif connections > 200:
                fit_score += 0.05
                indicators.append("�� Growing professional network (200+ connections)")
        
        # Career preferences alignment (10 points)
        if prefs_data and not isinstance(prefs_data, Exception):
            target_career = prefs_data.get("targetCareer")
            if target_career:
                fit_score += 0.10
                indicators.append(f"🎯 Clear career goal ({target_career})")
        
        return {
            "score": round(fit_score, 2),
            "percentage": round(fit_score * 100, 1),
            "indicators": indicators,
            "ready_for_senior_roles": fit_score >= 0.70,
            "ready_for_mid_roles": fit_score >= 0.50,
            "recommended_careers": list(set(recommendations))[:5]
        }
    
    def _infer_learning_style(self, psychometric_data, empathy_data, user_data) -> Dict[str, Any]:
        """Infer learning preferences from personality & education level"""
        style = {
            "preferred_format": "mixed",
            "pace": "moderate",
            "interaction": "balanced",
            "difficulty": "intermediate"
        }
        
        # Education level influences pace & difficulty
        if user_data and not isinstance(user_data, Exception):
            edu_level = user_data.get("education_level", "").lower()
            if "high school" in edu_level or "ug" in edu_level:
                style["pace"] = "slow"
                style["difficulty"] = "beginner"
                style["needs_warm_up"] = True
            elif "pg" in edu_level or "phd" in edu_level:
                style["pace"] = "fast"
                style["difficulty"] = "advanced"
                style["needs_warm_up"] = False
            elif "professional" in edu_level and ("experienced" in edu_level or "senior" in edu_level):
                style["pace"] = "fast"
                style["difficulty"] = "advanced"
        
        # Psychometric influences format & interaction
        if psychometric_data and not isinstance(psychometric_data, Exception):
            scores = psychometric_data.get("scores", {})
            openness = scores.get("openness", 3.0)
            extraversion = scores.get("extraversion", 3.0)
            
            if openness > 4.0:
                style["preferred_format"] = "hands-on projects"
            elif openness < 2.5:
                style["preferred_format"] = "structured tutorials"
            
            if extraversion > 4.0:
                style["interaction"] = "collaborative"
            elif extraversion < 2.5:
                style["interaction"] = "self-paced"
        
        return style
    
    def _extract_career_prefs(self, prefs_data) -> Dict[str, Any]:
        """Extract career preferences with fallbacks"""
        if not prefs_data or isinstance(prefs_data, Exception):
            return {
                "target_career": None,
                "industries": [],
                "work_style": None,
                "salary_expectation": None,
                "geographic": None
            }
        
        return {
            "target_career": prefs_data.get("targetCareer"),
            "industries": prefs_data.get("industries", []),
            "work_style": prefs_data.get("workStyle"),
            "salary_expectation": prefs_data.get("salaryExpectation"),
            "geographic": prefs_data.get("geographic"),
            "exploration_answers": prefs_data.get("explorationData")
        }
    
    def _calculate_completeness(self, persona: Dict[str, Any]) -> float:
        """Calculate persona data completeness (0.0 to 1.0)"""
        checks = [
            bool(persona["basic_info"].get("name")) and persona["basic_info"]["name"] != "Unknown",
            bool(persona["basic_info"].get("education_level")) and persona["basic_info"]["education_level"] != "Unknown",
            persona["data_sources"]["resume"],
            persona["data_sources"]["github"],
            persona["data_sources"]["linkedin"],
            persona["data_sources"]["psychometric"],
            persona["data_sources"]["empathy"],
            persona["data_sources"]["preferences"],
            persona["skills"]["total_count"] > 5,
            persona["experience"]["years"] > 0 or persona["experience"]["has_experience"]
        ]
        return sum(checks) / len(checks)
    
    def _calculate_portfolio_score(self, persona: Dict[str, Any]) -> int:
        """Calculate portfolio score (0-100) using formula from spec"""
        score = 0
        
        # GitHub quality (25 points)
        if persona["data_sources"]["github"]:
            score += 25
        elif persona["skills"]["technical_depth"] > 10:
            score += 15  # Partial credit if many technical skills
        
        # Resume strength (25 points)
        if persona["data_sources"]["resume"]:
            if persona["experience"]["years"] >= 3:
                score += 25
            elif persona["experience"]["years"] >= 1:
                score += 20
            else:
                score += 15
        
        # Psychometric (25 points)
        if persona["data_sources"]["psychometric"]:
            score += 25
        
        # Empathy (25 points)
        if persona["data_sources"]["empathy"]:
            empathy_score = persona["personality"]["empathy_score"]
            if empathy_score >= 70:
                score += 25
            elif empathy_score >= 50:
                score += 20
            else:
                score += 15
        
        return min(score, 100)
    
    def _determine_tier(self, portfolio_score: int) -> str:
        """Determine readiness tier based on portfolio score"""
        if portfolio_score >= 71:
            return "advanced"
        elif portfolio_score >= 41:
            return "intermediate"
        else:
            return "beginner"

# Singleton instance
_aggregator: Optional[PersonaAggregator] = None

async def get_aggregator(db_client: AsyncIOMotorClient) -> PersonaAggregator:
    """Get or create PersonaAggregator singleton"""
    global _aggregator
    if _aggregator is None:
        _aggregator = PersonaAggregator(db_client)
    return _aggregator
