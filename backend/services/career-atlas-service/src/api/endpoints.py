from fastapi import APIRouter, HTTPException
from pinecone import Pinecone
import numpy as np
import os
from typing import List, Dict
from datetime import datetime

router = APIRouter()

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "pcsk_5o9b9T_TjBMQ8MYhxGahQbEfAU21dQ5RprNEVB8Pty14NA2rZNE9kWmVLFbM6s9kABrSZE")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("guidora-careers")

def normalize_fit_score(raw_score: float) -> Dict:
    """
    Convert Pinecone cosine similarity to percentage fit score
    
    Pinecone similarity ranges from -1 to 1:
    - 1.0 = perfect match (identical vectors)
    - 0.0 = no similarity
    - -1.0 = opposite
    
    We convert this to 0-100% where:
    - 90-100% = Excellent Match
    - 70-89% = Strong Match  
    - 50-69% = Moderate Match
    - <50% = Weak Match
    """
    # Convert -1 to 1 range into 0-100%
    # Formula: (similarity + 1) / 2 * 100
    fit_percentage = ((raw_score + 1) / 2) * 100
    
    # Clamp to 0-100 range
    fit_percentage = max(0, min(100, fit_percentage))
    
    # Quality classification
    if fit_percentage >= 85:
        quality = "Excellent Match"
        confidence = "Very High"
    elif fit_percentage >= 70:
        quality = "Strong Match"
        confidence = "High"
    elif fit_percentage >= 50:
        quality = "Moderate Match"
        confidence = "Moderate"
    else:
        quality = "Weak Match"
        confidence = "Low"
    
    return {
        "fit_score": round(fit_percentage, 2),
        "match_quality": quality,
        "confidence": confidence,
        "raw_similarity": round(raw_score, 4)
    }

@router.get("/")
async def root():
    return {
        "status": "Career Atlas Service Running",
        "version": "1.0.0",
        "features": ["Vector Search", "Career Recommendations", "Fit Scoring"]
    }

@router.get("/api/careers/stats")
async def get_stats():
    """Get Pinecone index statistics"""
    try:
        stats = index.describe_index_stats()
        return {
            "total_careers": stats.total_vector_count,
            "dimension": stats.dimension,
            "index_fullness": stats.index_fullness
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/api/careers/recommend")
async def recommend_careers(request: Dict):
    """
    PRODUCTION-LEVEL career recommendations with normalized fit scores
    
    Request body:
    {
        "persona_embedding": [0.1, 0.2, ...],  # 768-dim vector
        "top_k": 5  # Number of recommendations
    }
    """
    try:
        persona_embedding = request.get("persona_embedding")
        top_k = request.get("top_k", 5)
        
        if not persona_embedding:
            raise HTTPException(status_code=400, detail="persona_embedding is required")
        
        if len(persona_embedding) != 768:
            raise HTTPException(
                status_code=400,
                detail=f"persona_embedding must be 768-dimensional, got {len(persona_embedding)}"
            )
        
        # Query Pinecone for similar careers
        results = index.query(
            vector=persona_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # CRITICAL FIX: Results are already sorted by Pinecone (highest similarity first)
        # DO NOT re-sort them!
        matches = []
        for match in results['matches']:
            # Normalize the score
            score_data = normalize_fit_score(match['score'])
            
            # Extract metadata
            metadata = match.get('metadata', {})
            
            matches.append({
                "career_id": match['id'],
                "fit_score": score_data['fit_score'],
                "match_quality": score_data['match_quality'],
                "confidence": score_data['confidence'],
                "raw_similarity": score_data['raw_similarity'],
                "title": metadata.get('title', 'Unknown'),
                "category": metadata.get('category', 'Unknown'),
                "skills": metadata.get('skills', []),
                "salary_range": {
                    "min": metadata.get('salary_min', 0),
                    "max": metadata.get('salary_max', 0),
                    "currency": "USD"
                },
                "demand_score": metadata.get('demand_score', 0),
                "growth_rate": metadata.get('growth_rate', 0)
            })
        
        # Calculate overall confidence
        if matches:
            top_score = matches[0]['fit_score']
            if top_score >= 85:
                overall_confidence = "Very High"
            elif top_score >= 70:
                overall_confidence = "High"
            elif top_score >= 50:
                overall_confidence = "Moderate"
            else:
                overall_confidence = "Low"
        else:
            overall_confidence = "No matches"
        
        return {
            "matches": matches,
            "recommendation_confidence": overall_confidence,
            "total_analyzed": len(matches),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")



from src.services.discovery_processor import DiscoveryProcessor
import logging

logger = logging.getLogger(__name__)
processor = DiscoveryProcessor()

@router.post("/api/careers/from-discovery")
async def recommend_from_discovery(responses: dict):
    """Process discovery responses and recommend matching careers"""
    try:
        from datetime import datetime
        
        user_id = responses.get("user_id")
        if not user_id:
            return {
                "success": False,
                "error": "user_id is required",
                "status": 400
            }
        
        matches = await processor.process_responses(responses)
        
        return {
            "success": True,
            "careers": [m.dict() for m in matches],
            "count": len(matches),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in recommend_from_discovery: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "status": 500
        }
