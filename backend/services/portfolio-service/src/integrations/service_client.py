import httpx
import asyncio
from typing import Dict, Any, Optional, List
from src.core.config import settings
from src.utils.logging import logger

class ServiceClient:
    """Client for integrating with other Guidora services"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        
    async def get_github_data(self, user_id: str, github_username: str) -> Optional[Dict[str, Any]]:
        """Fetch GitHub analysis from AI-Guidance service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{settings.ai_guidance_url}/api/v1/github/analyze",
                    json={
                        "user_id": user_id,
                        "github_username": github_username,
                        "analysis_type": "portfolio"
                    }
                )
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"GitHub data fetch failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching GitHub data: {e}")
            return None
            
    async def get_career_insights(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch career insights from Career Atlas service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{settings.career_atlas_url}/api/v1/insights/{user_id}"
                )
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Career insights fetch failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching career insights: {e}")
            return None
            
    async def get_achievements(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch achievements from Gamification service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{settings.gamification_url}/api/v1/user/{user_id}/achievements"
                )
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Achievements fetch failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching achievements: {e}")
            return None
            
    async def get_all_user_data(self, user_id: str, github_username: Optional[str] = None) -> Dict[str, Any]:
        """Aggregate data from all services"""
        tasks = [
            self.get_career_insights(user_id),
            self.get_achievements(user_id)
        ]
        
        if github_username:
            tasks.append(self.get_github_data(user_id, github_username))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "career_insights": results[0] if len(results) > 0 and not isinstance(results[0], Exception) else None,
            "achievements": results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None,
            "github_data": results[2] if len(results) > 2 and not isinstance(results[2], Exception) else None,
        }
