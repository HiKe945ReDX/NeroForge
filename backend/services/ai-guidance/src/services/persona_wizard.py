from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class OnboardingStep(Enum):
    BASIC_INFO = 1
    EDUCATION_LEVEL = 2
    UPLOAD_EXPERIENCE = 3
    SKILLS_PICKER = 4
    PSYCHOMETRIC_TEST = 5
    EMPATHY_MAP = 6
    CAREER_PREFERENCES = 7

class PersonaWizard:
    def __init__(self):
        self.steps = list(OnboardingStep)
    
    async def get_step(self, user_id: str, step: OnboardingStep) -> Dict:
        if step == OnboardingStep.BASIC_INFO:
            return {"step": "basic_info", "questions": [{"id": "name", "type": "text"}, {"id": "email", "type": "email"}]}
        elif step == OnboardingStep.EDUCATION_LEVEL:
            return {"step": "education_level", "options": ["High School", "Undergraduate", "Postgraduate", "Professional"]}
        return {"step": step.name}
    
    async def validate_step(self, step: OnboardingStep, data: Dict) -> Tuple[bool, Optional[str]]:
        if step == OnboardingStep.BASIC_INFO:
            required = ["name", "email"]
            if not all(k in data for k in required):
                return False, "Missing required fields"
        return True, None
    
    async def complete_step(self, user_id: str, step: OnboardingStep, data: Dict) -> Dict:
        is_valid, error = await self.validate_step(step, data)
        if not is_valid:
            return {"success": False, "error": error}
        current_index = self.steps.index(step)
        next_step = self.steps[current_index + 1] if current_index < len(self.steps) - 1 else None
        return {"success": True, "next_step": next_step.name if next_step else None}
