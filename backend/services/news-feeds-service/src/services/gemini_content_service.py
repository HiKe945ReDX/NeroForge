"""
🤖 GEMINI CONTENT SERVICE - AI-Powered News Curation
Uses Gemini AI to generate, curate, and personalize career news content
"""
import google.generativeai as genai
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

class GeminiContentService:
    """AI-Powered Content Generation using Gemini"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_career_news(self, topic: str, user_preferences: Dict = None) -> List[Dict]:
        """📰 Generate AI-curated career news for specific topic"""
        prompt = f"""
        Generate 5 relevant career news items about {topic} for Indian students.
        Include: job trends, skill requirements, company updates, salary insights.
        Format as JSON with: title, summary, career_insights, skills, relevance_score
        """
        
        response = await self._call_gemini_async(prompt)
        return self._parse_news_response(response, topic)
    
    async def personalize_feed(self, feeds: List[Dict], user_profile: Dict) -> List[Dict]:
        """🎯 Personalize feeds based on user interests and career stage"""
        # AI-powered personalization logic
        return feeds
    
    async def generate_career_insights(self, content: str) -> Dict[str, Any]:
        """💡 Extract actionable career insights from news content"""
        prompt = f"""
        Analyze this career content and provide:
        1. Key career insights (3-5 points)
        2. Skills mentioned (list) 
        3. Actionable steps (3 points)
        4. Relevance score (0-100)
        
        Content: {content[:2000]}
        """
        
        response = await self._call_gemini_async(prompt)
        return self._parse_insights_response(response)
