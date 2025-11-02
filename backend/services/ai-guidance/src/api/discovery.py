from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import google.generativeai as genai
import os
import json
from typing import Dict

router = APIRouter(prefix="/api/careers", tags=["careers"])

class DiscoveryRequest(BaseModel):
    user_id: str
    responses: Dict[int, str]

@router.post("/discover")
async def discover_careers(req: DiscoveryRequest):
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        prompt = f"""Career discovery: Interests: {req.responses.get(1, '')}, Activities: {req.responses.get(2, '')}, Work: {req.responses.get(3, '')}, Impact: {req.responses.get(4, '')}, Setting: {req.responses.get(5, '')}. Suggest 5 distinct domains. JSON: {{"discovered_domains": ["Domain1", "Domain2", ...], "reasoning": "..."}}"""
        result = client.models.generate_content(prompt)
        data = json.loads(result.text)
        return {"user_id": req.user_id, "discovered_domains": data.get("discovered_domains", []), "completed_at": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

