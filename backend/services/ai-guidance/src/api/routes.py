from fastapi import APIRouter
from src.api.endpoints.psychometric import router as psychometric_router
from src.api.endpoints.discovery import router as discovery_router
from src.api.endpoints.work_style import router as work_style_router
from src.api.endpoints.empathy import router as empathy_router
from src.api.endpoints.skills_endpoints import router as skills_router
from src.api.endpoints.endpoints import router as general_router

router = APIRouter()

router.include_router(psychometric_router, prefix="/psychometric", tags=["psychometric"])
router.include_router(discovery_router, prefix="/discovery", tags=["discovery"])
router.include_router(work_style_router, prefix="/work-style", tags=["work-style"])
router.include_router(empathy_router, prefix="/empathy", tags=["empathy"])
router.include_router(skills_router, prefix="/skills", tags=["skills"])
router.include_router(general_router, tags=["general"])

__all__ = ["router"]
