from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime
from src.core.database import get_database
from src.core.token_service import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class BasicInfoRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    education_level: str
    current_field_or_role: str

class ExperienceUploadRequest(BaseModel):
    resume_filename: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None

class SkillsPickerRequest(BaseModel):
    selected_skills: List[str]

class PsychometricRequest(BaseModel):
    answers: Dict[int, int]

class EmpathyRequest(BaseModel):
    answers: Dict[str, int]

class CareerPreferencesRequest(BaseModel):
    has_goal: str
    career_goals: Optional[List[str]] = None
    industries: List[str]
    work_style: str
    salary_expectation: Optional[int] = None
    geographic_preference: str = "Worldwide"

@router.post("/step1/basic-info")
async def step1_basic_info(data: BasicInfoRequest, db=Depends(get_database)):
    try:
        await db.users.update_one(
            {"email": data.email},
            {"$set": {
                "name": data.name,
                "phone": data.phone,
                "education_level": data.education_level,
                "current_field": data.current_field_or_role,
                "onboarding_step": 1,
                "completed_steps": [1],
                "updated_at": datetime.utcnow()
            }}
        )
        
        is_student = data.education_level in ["High School", "UG", "Bootcamp"]
        
        return {
            "step_completed": 1,
            "next_step": 2,
            "is_student": is_student,
            "message": "Basic info saved successfully"
        }
    except Exception as e:
        logger.error(f"Error in step 1: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/step2/upload-experience")
async def step2_upload_experience(data: ExperienceUploadRequest, current_user=Depends(get_current_user), db=Depends(get_database)):
    try:
        update_data = {
            "onboarding_step": 2,
            "completed_steps": [1, 2],
            "updated_at": datetime.utcnow()
        }
        
        if data.resume_filename:
            update_data["resume"] = {"filename": data.resume_filename, "uploaded_at": datetime.utcnow()}
        if data.github_username:
            update_data["github_username"] = data.github_username
        if data.linkedin_url:
            update_data["linkedin_url"] = data.linkedin_url
        
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": update_data}
        )
        
        return {
            "step_completed": 2,
            "next_step": 3,
            "files_uploaded": [f for f in [data.resume_filename, data.github_username, data.linkedin_url] if f],
            "message": "Experience uploaded successfully"
        }
    except Exception as e:
        logger.error(f"Error in step 2: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/step3/skills-picker")
async def step3_skills_picker(data: SkillsPickerRequest, current_user=Depends(get_current_user), db=Depends(get_database)):
    try:
        if len(data.selected_skills) > 20:
            raise ValueError("Maximum 20 skills allowed")
        
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {
                "skills": data.selected_skills[:20],
                "onboarding_step": 3,
                "completed_steps": [1, 2, 3],
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "step_completed": 3,
            "next_step": 4,
            "skills_count": len(data.selected_skills),
            "message": f"Selected {len(data.selected_skills)} skills"
        }
    except Exception as e:
        logger.error(f"Error in step 3: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/step4/psychometric-submit")
async def step4_psychometric(data: PsychometricRequest, current_user=Depends(get_current_user), db=Depends(get_database)):
    try:
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {
                "psychometric": {
                    "answers": data.answers,
                    "submitted_at": datetime.utcnow()
                },
                "onboarding_step": 4,
                "completed_steps": [1, 2, 3, 4],
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "step_completed": 4,
            "next_step": 5,
            "message": "Psychometric test saved"
        }
    except Exception as e:
        logger.error(f"Error in step 4: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/step5/empathy-submit")
async def step5_empathy(data: EmpathyRequest, current_user=Depends(get_current_user), db=Depends(get_database)):
    try:
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {
                "empathy": {
                    "answers": data.answers,
                    "submitted_at": datetime.utcnow()
                },
                "onboarding_step": 5,
                "completed_steps": [1, 2, 3, 4, 5],
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "step_completed": 5,
            "next_step": 6,
            "message": "Empathy assessment saved"
        }
    except Exception as e:
        logger.error(f"Error in step 5: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/step6/career-preferences")
async def step6_career_preferences(data: CareerPreferencesRequest, current_user=Depends(get_current_user), db=Depends(get_database)):
    try:
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {
                "career_preferences": {
                    "has_goal": data.has_goal,
                    "goals": data.career_goals or [],
                    "industries": data.industries,
                    "work_style": data.work_style,
                    "salary_expectation": data.salary_expectation,
                    "geographic_preference": data.geographic_preference,
                    "created_at": datetime.utcnow()
                },
                "onboarding_completed": True,
                "onboarding_completed_at": datetime.utcnow(),
                "onboarding_step": 6,
                "completed_steps": [1, 2, 3, 4, 5, 6],
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "step_completed": 6,
            "onboarding_complete": True,
            "profile_created": True,
            "portfolio_created": True,
            "next_steps": [
                "📊 View your personality dashboard",
                "🎯 Explore recommended career paths",
                "📈 Generate personalized roadmap",
                "🔗 Connect with mentors"
            ],
            "message": "Onboarding completed successfully!"
        }
    except Exception as e:
        logger.error(f"Error in step 6: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
async def get_onboarding_status(current_user=Depends(get_current_user), db=Depends(get_database)):
    try:
        user = await db.users.find_one({"_id": current_user["_id"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        completed = len(user.get("completed_steps", []))
        
        return {
            "current_step": user.get("onboarding_step", 0),
            "completed_steps": user.get("completed_steps", []),
            "onboarding_completed": user.get("onboarding_completed", False),
            "completion_percentage": (completed / 6) * 100
        }
    except Exception as e:
        logger.error(f"Error getting onboarding status: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
