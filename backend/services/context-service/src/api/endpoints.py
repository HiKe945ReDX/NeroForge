from fastapi import APIRouter, Depends, Body
from typing import Dict, Any
from src.utils.auth import verify_token

router = APIRouter()  # No prefix here - gateway handles /api/context

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "context"}

@router.get("/")
async def get_context(user_id: str = Depends(verify_token)):
    # Your context logic here
    return {"message": "Context endpoint", "user_id": user_id}

@router.post("/")
async def save_context(
    data: Dict[str, Any] = Body(...),
    user_id: str = Depends(verify_token)
):
    # Your save logic here
    return {"message": "Context saved", "user_id": user_id}
