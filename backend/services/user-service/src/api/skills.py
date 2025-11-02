from fastapi import APIRouter, Query
from typing import List
from ..data.skills_catalog import get_all_skills, search_skills, get_skills_by_category, get_categories

router = APIRouter()

@router.get("/skills")
async def list_all_skills() -> List[str]:
    """Get all 545 skills"""
    return get_all_skills()

@router.get("/skills/search")
async def search_skills_endpoint(
    q: str = Query(..., min_length=1, description="Search query")
) -> List[str]:
    """Search skills by keyword"""
    return search_skills(q)

@router.get("/skills/categories")
async def list_categories() -> List[str]:
    """Get all skill categories"""
    return get_categories()

@router.get("/skills/category/{category}")
async def get_skills_in_category(category: str) -> List[str]:
    """Get skills for specific category"""
    return get_skills_by_category(category)

@router.get("/skills/stats")
async def get_skills_stats():
    """Get skills catalog statistics"""
    from ..data.skills_catalog import SKILLS_CATALOG
    return {
        "total_skills": len(get_all_skills()),
        "total_categories": len(SKILLS_CATALOG),
        "breakdown": {cat: len(skills) for cat, skills in SKILLS_CATALOG.items()}
    }
