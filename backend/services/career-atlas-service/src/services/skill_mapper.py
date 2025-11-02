# skill_mapper.py
from typing import Dict, List
import logging
from datetime import datetime

from ..db.knowledge_crud import KnowledgeCrud
from ..models.knowledge_models import NodeType, RelationshipType

logger = logging.getLogger(__name__)


class SkillMapper:
    """
    Production-ready skill mapping and transferability analysis service
    Handles skill gap analysis, learning path generation, and career transitions
    """

    def __init__(self, knowledge_crud: KnowledgeCrud):
        self.crud = knowledge_crud
        self.skill_similarity_cache = {}
        self.career_skill_cache = {}

    async def analyze_skill_gap(self, current_skills: List[str], target_career: str) -> SkillGap:
        """
        Analyze skill gaps between current skills and target career requirements
        
        Returns detailed gap analysis with priorities and recommendations
        """
        try:
            log_career_operation("analyze_skill_gap", target_career, current_skills_count=len(current_skills))

            # Get target career requirements
            career_skills = await self._get_career_required_skills(target_career)
            if not career_skills:
                logger.warning(f"No skill requirements found for career: {target_career}")
                return SkillGap(
                    analysis_id=f"gap_{target_career}_{datetime.now().timestamp()}",
                    current_skills=current_skills,
                    target_position=target_career,
                    missing_skills=[],
                    skill_priorities={},
                    market_alignment=0.5
                )

            # Normalize skill names for comparison
            current_skills_normalized = set(skill.lower().strip() for skill in current_skills)
            
            # Identify missing skills
            missing_skills = []
            skill_priorities = {}
            
            for skill_data in career_skills:
                skill_name = skill_data['skill_name'].lower().strip()
                
                # Check if skill is missing or needs improvement
                if skill_name not in current_skills_normalized:
                    importance_weight = skill_data.get('weight', 0.5)
                    proficiency_required = skill_data.get('proficiency_level', 'Intermediate')
                    
                    missing_skill = {
                        'skill_name': skill_data['skill_name'],
                        'importance': skill_data.get('importance', 'Medium'),
                        'proficiency_required': proficiency_required,
                        'weight': importance_weight,
                        'skill_category': skill_data.get('skill_category', 'technical'),
                        'learning_resources': await self._get_learning_resources(skill_data['skill_name'])
                    }
                    
                    missing_skills.append(missing_skill)
                    
                    # Calculate priority score (0-100)
                    priority_score = int(importance_weight * 100)
                    if proficiency_required in ['Expert', 'Advanced']:
                        priority_score += 20
                    elif proficiency_required == 'Critical':
                        priority_score += 40
                    
                    skill_priorities[skill_data['skill_name']] = min(priority_score, 100)

            # Calculate market alignment
            market_alignment = await self._calculate_market_alignment(current_skills, career_skills)

            # Generate development recommendations
            development_recommendations = await self._generate_development_recommendations(
                missing_skills, target_career
            )

            analysis_id = f"gap_{target_career}_{int(datetime.now().timestamp())}"

            gap_analysis = SkillGap(
                analysis_id=analysis_id,
                current_skills=current_skills,
                target_position=target_career,
                missing_skills=missing_skills,
                skill_priorities=skill_priorities,
                development_recommendations=development_recommendations,
                market_alignment=market_alignment
            )

            logger.info(f"Skill gap analysis completed: {len(missing_skills)} gaps identified for {target_career}")
            return gap_analysis

        except Exception as e:
            log_error(e, {"operation": "analyze_skill_gap", "target_career": target_career})
            # Return empty analysis on error
            return SkillGap(
                analysis_id=f"gap_error_{int(datetime.now().timestamp())}",
                current_skills=current_skills,
                target_position=target_career,
                missing_skills=[],
                skill_priorities={},
                market_alignment=0.0
            )

    async def _get_career_required_skills(self, career_id: str) -> List[Dict[str, Any]]:
        """Get skills required for a specific career"""
        try:
            # Check cache first
            if career_id in self.career_skill_cache:
                return self.career_skill_cache[career_id]

            relationships = await self.crud.get_outgoing_relationships(
                career_id, RelationshipType.REQUIRES
            )

            skills = []
            for rel in relationships:
                skill_node = await self.crud.get_node(rel.target_node_id)
                if skill_node:
                    skill_data = {
                        'skill_name': skill_node.name,
                        'skill_id': skill_node.node_id,
                        'weight': rel.weight,
                        'importance': rel.properties.get('importance', 'Medium'),
                        'proficiency_level': rel.properties.get('proficiency', 'Intermediate'),
                        'skill_category': getattr(skill_node, 'skill_category', 'technical')
                    }
                    skills.append(skill_data)

            # Cache results
            self.career_skill_cache[career_id] = skills
            return skills

        except Exception as e:
            log_error(e, {"operation": "_get_career_required_skills", "career_id": career_id})
            return []
