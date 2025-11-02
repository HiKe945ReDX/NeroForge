"""Persona API Endpoints - Production Grade"""
from fastapi import APIRouter, HTTPException
from typing import Dict
from datetime import datetime
import logging

# CORRECT IMPORT PATH
from ..db.client import DatabaseClient

router = APIRouter(prefix="/api/persona", tags=["persona"])
logger = logging.getLogger(__name__)

@router.post("/create")
async def create_persona(data: Dict):
    """Create complete user persona"""
    try:
        from ..services.persona_aggregator import PersonaAggregator
        
        aggregator = PersonaAggregator()
        persona = await aggregator.create_complete_persona(data)
        
        # Save to MongoDB
        await DatabaseClient.database.personas.update_one(
            {"user_id": data.get("user_id")},
            {"$set": persona},
            upsert=True
        )
        
        return {"persona": persona, "status": "created"}
        
    except Exception as e:
        logger.error(f"Persona creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_persona(user_id: str):
    """Retrieve user persona"""
    persona = await DatabaseClient.database.personas.find_one({"user_id": user_id})
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    persona.pop("_id", None)
    return persona

@router.post("/{user_id}/preferences")
async def save_preferences(user_id: str, preferences: Dict):
    """Save career preferences"""
    careers = preferences.get("careers", [])
    
    if not careers or len(careers) > 3:
        raise HTTPException(status_code=400, detail="Select 1-3 careers")
    
    await DatabaseClient.database.personas.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "career_preferences": {
                    "careers": careers,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        },
        upsert=True
    )
    
    return {"user_id": user_id, "preferences": careers, "status": "saved"}

@router.get("/{user_id}/preferences")
async def get_preferences(user_id: str):
    """Get career preferences"""
    persona = await DatabaseClient.database.personas.find_one({"user_id": user_id})
    
    if not persona or "career_preferences" not in persona:
        raise HTTPException(status_code=404, detail="No preferences found")
    
    return persona["career_preferences"]
