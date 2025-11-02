import google.generativeai as genai
from typing import Dict, List
import logging
import os
import json

logger = logging.getLogger(__name__)

class ResumeParserGemini:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")
    
    async def parse(self, file_path: str) -> Dict:
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            prompt = """Extract resume data as JSON with: name, email, phone, location, summary, skills, experience, education, certifications."""
            
            response = self.model.generate_content([prompt, {"mime_type": "application/pdf", "data": file_content}])
            result = json.loads(response.text)
            logger.info(f"Resume parsed for {result.get('name', 'Unknown')}")
            return result
        except Exception as e:
            logger.error(f"Resume parsing error: {e}")
            raise
    
    async def extract_skills(self, resume_data: Dict) -> List[str]:
        return [s.lower().strip() for s in resume_data.get("skills", [])]
    
    async def calculate_experience_level(self, resume_data: Dict) -> str:
        total_months = sum(int(job.get("duration", "0").split()[0]) for job in resume_data.get("experience", []) if job.get("duration"))
        years = total_months / 12
        if years < 2: return "Entry Level"
        elif years < 5: return "Junior"
        elif years < 10: return "Mid-Level"
        else: return "Senior"
