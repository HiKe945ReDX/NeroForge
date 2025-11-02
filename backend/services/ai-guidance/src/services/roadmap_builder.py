from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import asyncio
import hashlib
import json


from src.core.genai_client import GenAIClient
from src.core.config import settings
from src.models.models import (
    Roadmap, RoadmapPhase, RoadmapSkill, RoadmapGenerationRequest,
    SkillLevel, RoadmapStatus, PersonaStepData, PsychometricAnswers,
    ResumeParseResponse, Repository, LinkedInProfile
)
from src.db.crud import (
    PersonaCRUD, PsychometricCRUD, ResumeCRUD, RepositoryCRUD,
    LinkedInCRUD, RoadmapCRUD, AIInsightCRUD
)
from src.utils.logging import setup_logger
import redis.asyncio as redis


logger = setup_logger(__name__)



class RoadmapBuilder:
    """Core service for generating personalized career roadmaps using Gemini AI"""
    
    def __init__(self):
        self.genai_client = GenAIClient()
        self.redis_client = None
        
        # Initialize CRUD instances
        self.persona_crud = PersonaCRUD()
        self.psychometric_crud = PsychometricCRUD()
        self.resume_crud = ResumeCRUD()
        self.repository_crud = RepositoryCRUD()
        self.linkedin_crud = LinkedInCRUD()
        self.roadmap_crud = RoadmapCRUD()
        self.insight_crud = AIInsightCRUD()
        
    async def initialize(self):
        """Initialize Redis connection for caching"""
        try:
            if settings.cache_llm_responses:
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    password=settings.redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30
                )
                # Test connection
                await self.redis_client.ping()
                logger.info("Redis connection established for roadmap caching")
        except Exception as e:
            logger.warning(f"Redis connection failed, caching disabled: {e}")
            self.redis_client = None


    def normalize_skill_level(self, level_str: str) -> str:
        """Convert any case skill level to lowercase enum-compatible format"""
        if not level_str:
            return "beginner"
            
        level_mapping = {
            "beginner": "beginner",
            "intermediate": "intermediate", 
            "advanced": "advanced",
            "expert": "expert",
            # Handle common variations
            "basic": "beginner",
            "novice": "beginner", 
            "entry": "beginner",
            "junior": "beginner",
            "mid": "intermediate",
            "middle": "intermediate",
            "proficient": "intermediate",
            "senior": "advanced",
            "professional": "advanced",
            "master": "expert",
            "guru": "expert"
        }
        
        normalized = level_str.lower().strip()
        return level_mapping.get(normalized, "beginner")


    async def generate_roadmap(self, request: RoadmapGenerationRequest) -> Roadmap:
        """Generate a personalized career roadmap"""
        try:
            logger.info(f"Starting roadmap generation for user {request.user_id}, target role: {request.target_role}")
            
            # Step 1: Gather user data
            user_data = await self._gather_user_data(request)
            
            # Step 2: Check cache for similar roadmaps
            cached_roadmap = await self._get_cached_roadmap(user_data, request.target_role)
            if cached_roadmap:
                logger.info(f"Returning cached roadmap for user {request.user_id}")
                return cached_roadmap
            
            # Step 3: Generate roadmap with Gemini AI
            roadmap = await self._generate_roadmap_with_ai(user_data, request)
            
            # Step 4: Save roadmap to database
            roadmap_id = await self.roadmap_crud.save_roadmap(roadmap)
            if roadmap_id:
                roadmap.roadmap_id = roadmap_id
                logger.info(f"Roadmap saved for user {request.user_id}, ID: {roadmap_id}")
            
            # Step 5: Cache the roadmap
            await self._cache_roadmap(user_data, request.target_role, roadmap)
            
            return roadmap
            
        except Exception as e:
            logger.error(f"Error generating roadmap for user {request.user_id}: {e}")
            raise


    async def _gather_user_data(self, request: RoadmapGenerationRequest) -> Dict[str, Any]:
        """Gather all available user data for roadmap generation"""
        user_data = {
            "user_id": request.user_id,
            "target_role": request.target_role,
            "current_role": request.current_role,
            "target_duration_weeks": request.target_duration_weeks,
            "weekly_learning_hours": request.weekly_learning_hours
        }
        
        # Gather data based on request flags
        gather_tasks = []
        
        if request.include_persona_data:
            gather_tasks.append(self._get_persona_data(request.user_id))
        
        if request.include_psychometric_data:
            gather_tasks.append(self._get_psychometric_data(request.user_id))
        
        if request.include_resume_data:
            gather_tasks.append(self._get_resume_data(request.user_id))
        
        if request.include_github_data:
            gather_tasks.append(self._get_github_data(request.user_id))
        
        if request.include_linkedin_data:
            gather_tasks.append(self._get_linkedin_data(request.user_id))
        
        # Execute all data gathering concurrently
        results = await asyncio.gather(*gather_tasks, return_exceptions=True)
        
        # Process results
        data_keys = ['persona', 'psychometric', 'resume', 'github', 'linkedin']
        for i, result in enumerate(results):
            if i < len(data_keys) and not isinstance(result, Exception) and result is not None:
                user_data[data_keys[i]] = result
            elif isinstance(result, Exception):
                logger.warning(f"Failed to gather {data_keys[i] if i < len(data_keys) else 'unknown'} data: {result}")
        
        return user_data


    async def _get_persona_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user persona data"""
        try:
            persona_steps = await self.persona_crud.get_user_persona_steps(user_id)
            if not persona_steps:
                return None
            
            persona_data = {}
            for step in persona_steps:
                persona_data[step.step] = step.data
            
            return persona_data
        except Exception as e:
            logger.error(f"Error fetching persona data for {user_id}: {e}")
            return None


    async def _get_psychometric_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user psychometric data"""
        try:
            psychometric = await self.psychometric_crud.get_user_psychometrics(user_id)
            return psychometric.dict() if psychometric else None
        except Exception as e:
            logger.error(f"Error fetching psychometric data for {user_id}: {e}")
            return None


    async def _get_resume_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user resume data"""
        try:
            resume = await self.resume_crud.get_user_resume(user_id)
            return resume.dict() if resume else None
        except Exception as e:
            logger.error(f"Error fetching resume data for {user_id}: {e}")
            return None


    async def _get_github_data(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get user GitHub repositories data"""
        try:
            repositories = await self.repository_crud.get_user_repositories(user_id)
            return [repo.dict() for repo in repositories] if repositories else None
        except Exception as e:
            logger.error(f"Error fetching GitHub data for {user_id}: {e}")
            return None


    async def _get_linkedin_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user LinkedIn data"""
        try:
            linkedin = await self.linkedin_crud.get_user_linkedin(user_id)
            return linkedin.dict() if linkedin else None
        except Exception as e:
            logger.error(f"Error fetching LinkedIn data for {user_id}: {e}")
            return None


    async def _generate_roadmap_with_ai(self, user_data: Dict[str, Any], request: RoadmapGenerationRequest) -> Roadmap:
        """Generate roadmap using Gemini AI"""
        try:
            # Create comprehensive prompt
            prompt = self._build_roadmap_prompt(user_data, request)
            
            # Call Gemini AI
            ai_response = await self.genai_client.generate_text(prompt)
            
            # Parse AI response into structured roadmap
            roadmap = await self._parse_ai_roadmap_response(ai_response, user_data, request)
            
            return roadmap
            
        except Exception as e:
            logger.error(f"Error generating roadmap with AI: {e}")
            raise


    def _build_roadmap_prompt(self, user_data: Dict[str, Any], request: RoadmapGenerationRequest) -> str:
        """Build comprehensive prompt for Gemini AI"""
        prompt_parts = []
        
        # System instructions
        prompt_parts.append("""
You are an expert career counselor and learning path designer. Create a detailed, personalized career roadmap in JSON format.

CRITICAL: Use only these exact skill levels: "beginner", "intermediate", "advanced", "expert" (all lowercase)

Requirements:
1. Generate a structured roadmap with phases, skills, and learning resources
2. Make it specific to the user's background and target role
3. Include realistic timelines and difficulty progression
4. Provide actionable learning milestones and resources
5. Consider the user's available weekly learning hours
6. Use only lowercase skill levels: beginner, intermediate, advanced, expert

Response format must be valid JSON with this structure:
{
  "title": "Career Roadmap Title",
  "description": "Detailed description",
  "phases": [
    {
      "title": "Phase Title",
      "description": "Phase description",
      "duration_weeks": 8,
      "order": 1,
      "skills": [
        {
          "skill_name": "Skill Name",
          "current_level": "beginner",
          "target_level": "intermediate",
          "priority": 8,
          "estimated_hours": 40,
          "resources": [
            {"title": "Resource Title", "url": "https://example.com", "type": "course"}
          ],
          "milestones": ["Milestone 1", "Milestone 2"],
          "prerequisites": ["Prerequisite skill"]
        }
      ]
    }
  ]
}
        """)
        
        # User profile section
        prompt_parts.append(f"\nUSER PROFILE:")
        prompt_parts.append(f"Target Role: {request.target_role}")
        
        if request.current_role:
            prompt_parts.append(f"Current Role: {request.current_role}")
        
        if request.target_duration_weeks:
            prompt_parts.append(f"Target Duration: {request.target_duration_weeks} weeks")
        
        if request.weekly_learning_hours:
            prompt_parts.append(f"Available Learning Hours: {request.weekly_learning_hours} hours/week")
        
        # Add user data sections
        if user_data.get('persona'):
            prompt_parts.append(f"\nPERSONA DATA:\n{json.dumps(user_data['persona'], indent=2)}")
        
        if user_data.get('resume'):
            resume_data = user_data['resume']
            prompt_parts.append(f"\nRESUME ANALYSIS:")
            prompt_parts.append(f"Skills: {resume_data.get('skills', [])}")
            prompt_parts.append(f"Experience: {len(resume_data.get('experience', []))} positions")
            prompt_parts.append(f"Education: {resume_data.get('education', [])}")
        
        if user_data.get('github'):
            github_data = user_data['github']
            prompt_parts.append(f"\nGITHUB ANALYSIS:")
            prompt_parts.append(f"Repositories: {len(github_data)}")
            languages = set()
            technologies = set()
            for repo in github_data:
                languages.add(repo.get('primary_language', ''))
                technologies.update(repo.get('technologies', []))
            prompt_parts.append(f"Programming Languages: {list(languages)}")
            prompt_parts.append(f"Technologies: {list(technologies)}")
        
        if user_data.get('linkedin'):
            linkedin_data = user_data['linkedin']
            prompt_parts.append(f"\nLINKEDIN PROFILE:")
            prompt_parts.append(f"Current Position: {linkedin_data.get('current_position')}")
            prompt_parts.append(f"Skills: {linkedin_data.get('top_skills', [])}")
            prompt_parts.append(f"Industry: {linkedin_data.get('industry')}")
        
        if user_data.get('psychometric'):
            psychometric = user_data['psychometric']
            prompt_parts.append(f"\nPSYCHOMETRIC PROFILE:")
            if psychometric.get('trait_scores'):
                for trait, score in psychometric['trait_scores'].items():
                    prompt_parts.append(f"{trait.capitalize()}: {score:.1f}/5.0")
        
        # Final instructions
        prompt_parts.append(f"""
        
INSTRUCTIONS:
1. Create a roadmap specifically for transitioning to {request.target_role}
2. Break it into 3-5 logical phases with clear progression
3. Each phase should build on previous ones
4. Include both technical and soft skills
5. Provide real, accessible learning resources
6. Make timelines realistic based on available learning hours
7. Consider the user's existing skills to avoid redundancy
8. Focus on practical, job-relevant skills
9. Include project-based milestones for portfolio building
10. CRITICAL: Use ONLY these skill levels: "beginner", "intermediate", "advanced", "expert" (lowercase)

Return ONLY the JSON roadmap, no additional text.
        """)
        
        return "\n".join(prompt_parts)


    async def _parse_ai_roadmap_response(
        self, 
        ai_response: str, 
        user_data: Dict[str, Any], 
        request: RoadmapGenerationRequest
    ) -> Roadmap:
        """Parse AI response into structured Roadmap model with skill level normalization"""
        try:
            # Extract JSON from response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No valid JSON found in AI response")
            
            json_str = ai_response[json_start:json_end]
            roadmap_data = json.loads(json_str)
            
            # Parse phases
            phases = []
            total_weeks = 0
            
            for phase_data in roadmap_data.get('phases', []):
                # Parse skills for this phase
                skills = []
                for skill_data in phase_data.get('skills', []):
                    # Normalize skill levels using our helper function
                    current_level = self.normalize_skill_level(skill_data.get('current_level', 'beginner'))
                    target_level = self.normalize_skill_level(skill_data.get('target_level', 'intermediate'))
                    
                    try:
                        skill = RoadmapSkill(
                            skill_name=skill_data['skill_name'],
                            current_level=SkillLevel(current_level),
                            target_level=SkillLevel(target_level),
                            priority=skill_data.get('priority', 5),
                            estimated_hours=skill_data.get('estimated_hours', 20),
                            resources=skill_data.get('resources', []),
                            milestones=skill_data.get('milestones', [])
                        )
                        skills.append(skill)
                    except ValueError as e:
                        logger.warning(f"Invalid skill level in AI response, using defaults: {e}")
                        # Create skill with safe defaults
                        skill = RoadmapSkill(
                            skill_name=skill_data.get('skill_name', 'Unknown Skill'),
                            current_level=SkillLevel.BEGINNER,
                            target_level=SkillLevel.INTERMEDIATE,
                            priority=skill_data.get('priority', 5),
                            estimated_hours=skill_data.get('estimated_hours', 20),
                            resources=skill_data.get('resources', []),
                            milestones=skill_data.get('milestones', [])
                        )
                        skills.append(skill)
                
                # Create phase
                phase = RoadmapPhase(
                    title=phase_data['title'],
                    description=phase_data['description'],
                    duration_weeks=phase_data.get('duration_weeks', 4),
                    skills=skills,
                    order=phase_data.get('order', len(phases) + 1)
                )
                phases.append(phase)
                total_weeks += phase.duration_weeks
            
            # Determine difficulty level based on target role
            difficulty_mapping = {
                'junior': SkillLevel.BEGINNER,
                'senior': SkillLevel.ADVANCED,
                'lead': SkillLevel.EXPERT,
                'manager': SkillLevel.EXPERT,
                'principal': SkillLevel.EXPERT,
                'staff': SkillLevel.EXPERT
            }
            
            difficulty = SkillLevel.INTERMEDIATE
            for level, skill_level in difficulty_mapping.items():
                if level in request.target_role.lower():
                    difficulty = skill_level
                    break
            
            # Create roadmap
            roadmap = Roadmap(
                user_id=request.user_id,
                title=roadmap_data.get('title', f"Career Path to {request.target_role}"),
                description=roadmap_data.get('description', f"Personalized roadmap for becoming a {request.target_role}"),
                target_role=request.target_role,
                current_role=request.current_role,
                phases=phases,
                total_duration_weeks=total_weeks,
                difficulty_level=difficulty,
                status=RoadmapStatus.ACTIVE,
                confidence_score=0.85,  # High confidence for AI-generated roadmaps
                based_on_resume=bool(user_data.get('resume')),
                based_on_github=bool(user_data.get('github')),
                based_on_linkedin=bool(user_data.get('linkedin')),
                based_on_psychometrics=bool(user_data.get('psychometric')),
                based_on_persona=bool(user_data.get('persona'))
            )
            
            return roadmap
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"AI Response: {ai_response[:1000]}...")
            # Fallback to creating a basic roadmap
            return await self._create_fallback_roadmap(request)
        except Exception as e:
            logger.error(f"Error parsing AI roadmap response: {e}")
            raise


    async def _create_fallback_roadmap(self, request: RoadmapGenerationRequest) -> Roadmap:
        """Create a basic fallback roadmap if AI generation fails"""
        logger.warning(f"Creating fallback roadmap for {request.target_role}")
        
        # Basic skill template based on target role
        basic_skills = [
            RoadmapSkill(
                skill_name="Foundation Skills",
                current_level=SkillLevel.BEGINNER,
                target_level=SkillLevel.INTERMEDIATE,
                priority=9,
                estimated_hours=40,
                resources=[{"title": "Online Course", "url": "", "type": "course"}],
                milestones=["Complete basics", "Build first project"]
            )
        ]
        
        basic_phase = RoadmapPhase(
            title="Foundation Phase",
            description=f"Build foundational skills for {request.target_role}",
            duration_weeks=8,
            skills=basic_skills,
            order=1
        )
        
        return Roadmap(
            user_id=request.user_id,
            title=f"Basic Path to {request.target_role}",
            description=f"Foundational roadmap for {request.target_role}",
            target_role=request.target_role,
            current_role=request.current_role,
            phases=[basic_phase],
            total_duration_weeks=8,
            difficulty_level=SkillLevel.BEGINNER,
            status=RoadmapStatus.DRAFT,
            confidence_score=0.5,
            based_on_resume=False,
            based_on_github=False,
            based_on_linkedin=False,
            based_on_psychometrics=False,
            based_on_persona=False
        )


    async def _get_cached_roadmap(self, user_data: Dict[str, Any], target_role: str) -> Optional[Roadmap]:
        """Get cached roadmap if available"""
        if not self.redis_client or not settings.cache_llm_responses:
            return None
        
        try:
            # Create cache key based on user data hash
            cache_key = self._create_cache_key(user_data, target_role)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                roadmap_dict = json.loads(cached_data)
                return Roadmap(**roadmap_dict)
            
        except Exception as e:
            logger.warning(f"Error retrieving cached roadmap: {e}")
        
        return None


    async def _cache_roadmap(self, user_data: Dict[str, Any], target_role: str, roadmap: Roadmap):
        """Cache generated roadmap"""
        if not self.redis_client or not settings.cache_llm_responses:
            return
        
        try:
            cache_key = self._create_cache_key(user_data, target_role)
            cache_data = roadmap.json()
            
            # Cache for 7 days
            await self.redis_client.setex(cache_key, 604800, cache_data)
            logger.info(f"Roadmap cached with key: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Error caching roadmap: {e}")


    def _create_cache_key(self, user_data: Dict[str, Any], target_role: str) -> str:
        """Create cache key based on user data"""
        # Create hash of relevant user data
        cache_data = {
            'target_role': target_role,
            'persona_hash': self._hash_data(user_data.get('persona')),
            'resume_skills': user_data.get('resume', {}).get('skills', []),
            'github_languages': [],
            'linkedin_skills': user_data.get('linkedin', {}).get('top_skills', [])
        }
        
        # Add GitHub languages
        if user_data.get('github'):
            languages = set()
            for repo in user_data['github']:
                languages.add(repo.get('primary_language', ''))
            cache_data['github_languages'] = sorted(list(languages))
        
        # Create hash
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        
        return f"roadmap:{cache_hash}"


    def _hash_data(self, data: Any) -> str:
        """Create hash of arbitrary data"""
        if data is None:
            return "none"
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_string.encode()).hexdigest()[:8]


    async def get_user_roadmaps(self, user_id: str) -> List[Roadmap]:
        """Get all roadmaps for a user"""
        return await self.roadmap_crud.get_user_roadmaps(user_id)


    async def get_active_roadmap(self, user_id: str) -> Optional[Roadmap]:
        """Get user's currently active roadmap"""
        return await self.roadmap_crud.get_active_roadmap(user_id)


    async def update_roadmap_status(self, roadmap_id: str, status: RoadmapStatus) -> bool:
        """Update roadmap status"""
        return await self.roadmap_crud.update_roadmap_status(roadmap_id, status.value)



# Global instance
roadmap_builder = RoadmapBuilder()



async def initialize_roadmap_service():
    """Initialize the roadmap service"""
    await roadmap_builder.initialize()
    logger.info("RoadmapBuilder service initialized")



# Export
__all__ = ['RoadmapBuilder', 'roadmap_builder', 'initialize_roadmap_service']
