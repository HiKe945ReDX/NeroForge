"""
Vertex AI Embedding Service
"""
from vertexai.language_models import TextEmbeddingModel
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        try:
            self.model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            logger.info("Embedding model loaded")
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate 768-dim vector"""
        try:
            embeddings = self.model.get_embeddings([text])
            return embeddings[0].values
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise
    
    def embed_career(self, career: Dict) -> List[float]:
        """Create career embedding"""
        career_text = f"""
        Career: {career.get('title', '')}
        Description: {career.get('description', '')}
        Skills: {', '.join(career.get('skills', []))}
        Category: {career.get('category', '')}
        """
        return self.generate_embedding(career_text.strip())

# Global instance
embedding_service = EmbeddingService()
