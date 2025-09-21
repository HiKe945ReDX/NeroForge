from typing import Dict, Any, List, Optional
from src.models import ProjectHighlight, UserProfile
from src.utils.logging import logger
import json

class ContentGenerator:
    """AI-powered content enhancement for portfolios"""
    
    def __init__(self):
        self.ai_enabled = False  # Will enable when AI keys are provided
        
    async def enhance_project_descriptions(self, projects: List[Dict[str, Any]]) -> List[ProjectHighlight]:
        """Convert raw project data into professional portfolio projects"""
        enhanced_projects = []
        
        for project in projects[:8]:  # Limit to top 8 projects
            try:
                highlight = ProjectHighlight(
                    title=project.get('name', 'Untitled Project'),
                    description=self._generate_description(project),
                    tech_stack=project.get('languages', [])[:5],  # Top 5 technologies
                    github_url=project.get('html_url'),
                    live_url=project.get('homepage'),
                    image_url=None  # Could be enhanced with screenshot service
                )
                enhanced_projects.append(highlight)
            except Exception as e:
                logger.warning(f"Error processing project {project.get('name')}: {e}")
                continue
                
        return enhanced_projects
        
    def _generate_description(self, project: Dict[str, Any]) -> str:
        """Generate professional project description"""
        name = project.get('name', 'Project')
        description = project.get('description', '')
        stars = project.get('stargazers_count', 0)
        forks = project.get('forks_count', 0)
        languages = project.get('languages', [])
        
        # Basic template - can be enhanced with AI
        if description:
            enhanced = f"{description}"
        else:
            enhanced = f"A {' & '.join(languages[:2])} project" if languages else "Software project"
            
        # Add engagement metrics if significant
        if stars > 5:
            enhanced += f" with {stars} GitHub stars"
        if forks > 2:
            enhanced += f" and {forks} forks"
            
        enhanced += "."
        
        return enhanced
        
    async def generate_bio_enhancement(self, profile: UserProfile, service_data: Dict[str, Any]) -> str:
        """Enhance user bio with data from services"""
        bio = profile.bio
        
        # Add achievements if available
        achievements = service_data.get('achievements', {})
        if achievements:
            total_points = achievements.get('total_points', 0)
            if total_points > 1000:
                bio += f" Achieved {total_points} learning points on the platform."
                
        # Add career insights
        career_insights = service_data.get('career_insights', {})
        if career_insights:
            skills = career_insights.get('top_skills', [])[:3]
            if skills:
                bio += f" Specialized in {', '.join(skills)}."
                
        return bio
        
    def create_skills_summary(self, service_data: Dict[str, Any]) -> List[str]:
        """Aggregate skills from all services"""
        all_skills = set()
        
        # From GitHub data
        github_data = service_data.get('github_data', {})
        if github_data:
            languages = github_data.get('languages', {})
            all_skills.update(languages.keys())
            
        # From career insights  
        career_insights = service_data.get('career_insights', {})
        if career_insights:
            skills = career_insights.get('skills', [])
            all_skills.update(skills)
            
        return list(all_skills)[:12]  # Top 12 skills
