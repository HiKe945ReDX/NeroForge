import datetime
from typing import Dict, List, Optional

from src.db.client import MongoDBClient
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

class PsychometricService:
    def __init__(self):
        self.collection = MongoDBClient.get_database().psychometrics

    def validate_answers(self, answers: Dict[str, List[int]]) -> bool:
        """
        Validate the structure and content of the psychometric answers.
        Ensures required traits exist and values are integers 1-5.
        """
        required_traits = {
            "openness", "conscientiousness",
            "extraversion", "agreeableness",
            "neuroticism", "grit"
        }
        if not required_traits.issubset(set(answers.keys())):
            logger.debug("Missing required traits in answers.")
            return False

        for trait, values in answers.items():
            if not all(isinstance(v, int) and 1 <= v <= 5 for v in values):
                logger.debug(f"Invalid values for trait '{trait}': {values}")
                return False

        return True

    def compute_scores(self, answers: Dict[str, List[int]]) -> Dict[str, float]:
        """
        Compute average scores (rounded to 2 decimals) for each trait.
        """
        scores = {}
        for trait, vals in answers.items():
            scores[trait] = round(sum(vals) / len(vals), 2) if vals else 0.0
        return scores

    async def save_scores(self, user_id: str, scores: Dict[str, float]) -> bool:
        """
        Save or update user's psychometric scores in MongoDB.
        """
        doc = {
            "user_id": user_id,
            "scores": scores,
            "updated_at": datetime.datetime.utcnow(),
        }
        try:
            result = await self.collection.replace_one({"user_id": user_id}, doc, upsert=True)
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error saving psychometric scores for user '{user_id}': {e}")
            raise

    async def get_scores(self, user_id: str) -> Optional[Dict[str, float]]:
        """
        Retrieve previously stored scores for user, if any.
        """
        try:
            doc = await self.collection.find_one({"user_id": user_id})
            return doc.get("scores") if doc else None
        except Exception as e:
            logger.error(f"Error retrieving scores for user '{user_id}': {e}")
            raise

    async def process_submission(self, user_id: str, answers: Dict[str, List[int]]) -> Dict[str, float]:
        """
        Full workflow: validate, compute, save, and return scores for psychometric submission.
        Raises ValueError on invalid input.
        """
        if not self.validate_answers(answers):
            logger.warning(f"Invalid psychometric answers received for user '{user_id}'.")
            raise ValueError("Invalid psychometric answers submitted.")

        scores = self.compute_scores(answers)
        await self.save_scores(user_id, scores)
        return scores
