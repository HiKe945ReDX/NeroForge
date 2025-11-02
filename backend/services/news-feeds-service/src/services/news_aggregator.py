"""📰 NEWS AGGREGATOR SERVICE - Multi-Source Career News"""
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

class NewsAggregatorService:
    """📰 Multi-Source News Aggregation Service"""
    
    def __init__(self):
        self.news_sources = {
            "tech_news": {"name": "TechCrunch India", "reliability_score": 90},
            "business_news": {"name": "Economic Times", "reliability_score": 95},
            "career_news": {"name": "Inc42", "reliability_score": 85}
        }
    
    async def fetch_topic_news(self, topic: str, limit: int = 10):
        """📡 Fetch news for specific career topic"""
        return await self._generate_mock_news(topic, limit)
    
    async def aggregate_all_sources(self):
        """🔄 Aggregate news from all configured sources"""
        all_news = []
        for source_id, source_info in self.news_sources.items():
            source_news = await self._fetch_from_source(source_id, source_info)
            all_news.extend(source_news)
        return self._deduplicate_news(all_news)
