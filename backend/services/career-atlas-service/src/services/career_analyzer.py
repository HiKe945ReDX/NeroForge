from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import asyncio

from ..models.career_models import Career, CareerDomain, CareerSearchFilters, CareerComparison
from ..db.client import DatabaseManager
from ..core.knowledge_engine import KnowledgeEngine
from ..utils.logging import setup_logging


logger = setup_logging()

class CareerAtlasService:
    """
    Core business logic service for career atlas functionality
    Ported and enhanced from your original monolithic implementation
    """
    
    def __init__(self, db_manager: DatabaseManager, knowledge_engine: KnowledgeEngine):
        self.db_manager = db_manager
        self.knowledge_engine = knowledge_engine
        self.career_domains = {}
        self._initialize_domains()
    
    def _initialize_domains(self):
        """Initialize career domain data"""
        self.career_domains = {
            "technology": CareerDomain(
                domain_id="technology",
                name="Technology",
                description="Careers in software, hardware, and digital innovation",
                icon="💻",
                subcategories=[
                    {"id": "software_development", "name": "Software Development", "career_count": 25},
                    {"id": "data_science", "name": "Data Science & Analytics", "career_count": 15},
                    {"id": "cybersecurity", "name": "Cybersecurity", "career_count": 12},
                    {"id": "product_management", "name": "Product Management", "career_count": 8},
                    {"id": "devops", "name": "DevOps & Infrastructure", "career_count": 10},
                    {"id": "ai_ml", "name": "AI & Machine Learning", "career_count": 18}
                ],
                career_count=88,
                avg_salary="$105,000",
                growth_rate="15%",
                top_skills=["Programming", "Problem Solving", "System Design", "Cloud Computing", "AI/ML"],
                industry_overview="Fast-growing sector driving digital transformation across industries",
                future_outlook="Continued high demand with emerging technologies like AI, blockchain, and quantum computing"
            ),
            "healthcare": CareerDomain(
                domain_id="healthcare",
                name="Healthcare & Life Sciences",
                description="Medical, wellness, research, and healthcare administration careers",
                icon="🏥",
                subcategories=[
                    {"id": "clinical", "name": "Clinical Care", "career_count": 35},
                    {"id": "administration", "name": "Healthcare Administration", "career_count": 18},
                    {"id": "research", "name": "Medical Research", "career_count": 15},
                    {"id": "mental_health", "name": "Mental Health", "career_count": 22},
                    {"id": "health_tech", "name": "Health Technology", "career_count": 12},
                    {"id": "pharmacy", "name": "Pharmacy & Pharma", "career_count": 14}
                ],
                career_count=116,
                avg_salary="$85,000",
                growth_rate="18%",
                top_skills=["Patient Care", "Medical Knowledge", "Communication", "Empathy", "Critical Thinking"],
                industry_overview="Essential sector with aging population and technological advancement driving demand",
                future_outlook="Strong growth with integration of AI, telemedicine, and personalized medicine"
            ),
            # Additional domains...
        }

    async def get_all_domains(self) -> List[CareerDomain]:
        """Get all career domains with current data"""
        logger.info("Retrieving all career domains")
        return list(self.career_domains.values())

    async def get_domain_details(self, domain_id: str) -> CareerDomain:
        """Get detailed information about a specific career domain"""
        logger.info(f"Retrieving domain details for: {domain_id}")
        
        if domain_id not in self.career_domains:
            logger.warning(f"Domain not found: {domain_id}")
            raise ValueError(f"Career domain '{domain_id}' not found")
        
        return self.career_domains[domain_id]

    async def search_careers(self, filters: CareerSearchFilters) -> List[Career]:
        """Advanced career search with comprehensive filtering"""
        logger.info(f"Searching careers with filters: {filters.dict()}")
        
        # Get all careers (in production, this would query the database)
        all_careers = await self._get_comprehensive_career_data()
        
        # Apply filters
        filtered_careers = all_careers
        
        if filters.keywords:
            keywords = filters.keywords.lower()
            filtered_careers = [
                career for career in filtered_careers
                if (keywords in career.title.lower() or 
                    keywords in career.description.lower() or
                    any(keywords in skill.lower() for skill in career.required_skills) or
                    any(keywords in resp.lower() for resp in career.responsibilities))
            ]
        
        # Additional filtering logic...
        
        # Limit results and sort by relevance
        filtered_careers = sorted(
            filtered_careers,
            key=lambda x: (x.demand_score, x.job_satisfaction_score),
            reverse=True
        )[:25]
        
        logger.info(f"Search returned {len(filtered_careers)} careers")
        return filtered_careers

    # Additional methods: get_career_details, compare_careers, get_trending_careers...
    
    async def _get_comprehensive_career_data(self) -> List[Career]:
        """Get comprehensive career data (enhanced version of your original mock data)"""
        return [
            Career(
                career_id="data_scientist",
                title="Data Scientist",
                category="technology",
                subcategory="data_science",
                description="Analyze complex data to help organizations make data-driven decisions",
                # ... complete career data
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            # More careers...
        ]
