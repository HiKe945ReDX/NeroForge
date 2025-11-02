from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
import json
import os

router = APIRouter(prefix="/api/skills", tags=["skills"])

# Load skills database
skills_db_path = os.path.join(os.path.dirname(__file__), "../data/skills_database.json")
with open(skills_db_path) as f:
    SKILLS_DB = json.load(f)

@router.get("/categories")
async def get_skill_categories():
    """Return all skill categories"""
    return {
        "categories": list(SKILLS_DB.keys()),
        "total_skills": sum(len(skills) for skills in SKILLS_DB.values())
    }

@router.get("/category/{category_name}")
async def get_skills_by_category(category_name: str):
    """Get all skills in a specific category"""
    if category_name not in SKILLS_DB:
        raise HTTPException(status_code=404, detail=f"Category '{category_name}' not found")
    
    return {
        "category": category_name,
        "skills": SKILLS_DB[category_name],
        "count": len(SKILLS_DB[category_name])
    }

@router.get("/search")
async def search_skills(
    query: str = Query(..., min_length=2),
    limit: int = Query(50, le=200)
):
    """Search skills by keyword (case-insensitive)"""
    results = []
    query_lower = query.lower()
    
    for category, skills in SKILLS_DB.items():
        matching = [
            {
                "skill": skill,
                "category": category,
                "category_display": category.replace("_", " ").title()
            }
            for skill in skills 
            if query_lower in skill.lower()
        ]
        results.extend(matching)
    
    # Sort by relevance (exact matches first, then starts-with, then contains)
    results.sort(key=lambda x: (
        x["skill"].lower() != query_lower,
        not x["skill"].lower().startswith(query_lower),
        x["skill"].lower()
    ))
    
    return {
        "query": query,
        "results": results[:limit],
        "total_found": len(results)
    }

@router.post("/validate")
async def validate_skills(skills: List[str]):
    """Validate selected skills (max 15)"""
    if len(skills) > 15:
        raise HTTPException(status_code=400, detail="Maximum 15 skills allowed")
    
    validated = []
    invalid = []
    
    for skill in skills:
        found = False
        for category, skill_list in SKILLS_DB.items():
            if skill in skill_list:
                validated.append({
                    "skill": skill,
                    "category": category,
                    "category_display": category.replace("_", " ").title()
                })
                found = True
                break
        
        if not found:
            invalid.append(skill)
    
    return {
        "validated_skills": validated,
        "invalid_skills": invalid,
        "total_validated": len(validated)
    }

@router.get("/recommend")
async def recommend_skills(
    current_skills: List[str] = Query(...),
    target_career: Optional[str] = None
):
    """Recommend complementary skills based on current skills"""
    # Simple recommendation: suggest skills from same categories
    user_categories = set()
    
    for skill in current_skills:
        for category, skills in SKILLS_DB.items():
            if skill in skills:
                user_categories.add(category)
    
    recommendations = []
    for category in user_categories:
        category_skills = [
            s for s in SKILLS_DB[category] 
            if s not in current_skills
        ]
        recommendations.extend([
            {
                "skill": skill,
                "category": category,
                "reason": f"Complements your {category.replace('_', ' ')} skills"
            }
            for skill in category_skills[:5]  # Top 5 per category
        ])
    
    return {
        "current_skills": current_skills,
        "recommendations": recommendations[:15],  # Max 15 suggestions
        "total_available": len(recommendations)
    }

@router.get("/stats")
async def get_stats():
    """Get statistics about skills database"""
    return {
        "total_categories": len(SKILLS_DB),
        "total_skills": sum(len(skills) for skills in SKILLS_DB.values()),
        "breakdown": {
            category: len(skills) 
            for category, skills in SKILLS_DB.items()
        }
    }

