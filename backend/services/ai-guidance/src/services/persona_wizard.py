import datetime
from typing import Dict, Any, List
from src.db.client import MongoDBClient
from src.utils.logging import setup_logger
from src.core.genai_client import GenAIClient

logger = setup_logger(__name__)

class PersonaWizardService:
    def __init__(self):
        self.collection = MongoDBClient.get_database().persona_data
        self.genai = GenAIClient()

    async def save_step_data(self, user_id: str, step: str, data: Dict[str, Any]) -> bool:
        try:
            filter_query = {"user_id": user_id, "step": step}
            update = {"$set": {"data": data, "updated_at": datetime.datetime.utcnow()}}
            result = await self.collection.update_one(filter_query, update, upsert=True)
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error saving persona step for user {user_id}, step {step}: {e}")
            raise

    async def get_all_steps(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            cursor = self.collection.find({"user_id": user_id})
            return await cursor.to_list(length=100)
        except Exception as e:
            logger.error(f"Error retrieving persona steps for user {user_id}: {e}")
            raise

    async def aggregate_persona(self, user_id: str) -> Dict[str, Any]:
        try:
            steps = await self.get_all_steps(user_id)
            return {"user_id": user_id, "persona_steps": steps}
        except Exception as e:
            logger.error(f"Error aggregating persona for user {user_id}: {e}")
            raise

    async def generate_career_roadmap(self, user_id: str) -> Dict[str, Any]:
        persona = await self.aggregate_persona(user_id)
        try:
            return await self.genai.generate_roadmap(persona, career_id=persona.get("persona_steps", [])[0].get("data", {}).get("target_career", "general"))
        except Exception as e:
            logger.error(f"GenAI roadmap error for user {user_id}: {e}")
            raise
