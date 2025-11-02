"""
Pinecone Vector Database Integration
"""
import os
from pinecone import Pinecone
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found")
        
        self.pc = Pinecone(api_key=api_key)
        self.index_name = "guidora-careers"
        
        try:
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone: {self.index_name}")
        except Exception as e:
            logger.error(f"Pinecone connection failed: {e}")
            raise
    
    def upsert_career(self, career_id: str, embedding: List[float], metadata: Dict):
        """Store career embedding"""
        try:
            self.index.upsert(vectors=[{
                "id": career_id,
                "values": embedding,
                "metadata": metadata
            }])
            logger.info(f"Upserted: {career_id}")
        except Exception as e:
            logger.error(f"Upsert failed: {e}")
            raise
    
    def search_similar_careers(self, persona_embedding: List[float], top_k: int = 5):
        """Find matching careers"""
        try:
            results = self.index.query(
                vector=persona_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            matches = [
                {
                    "career_id": match.id,
                    "fit_score": round(match.score * 100, 2),
                    "title": match.metadata.get("title"),
                    "skills": match.metadata.get("skills", [])
                }
                for match in results.matches
            ]
            return matches
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

# Global instance
vector_db = VectorDB()
