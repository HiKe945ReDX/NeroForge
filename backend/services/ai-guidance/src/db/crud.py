from typing import Any, Dict, List, Optional, Union, Type
from datetime import datetime, timezone
from src.db.client import MongoDBClient
from src.utils.logging import setup_logger
from src.models.models import (
    PersonaStepData, PsychometricAnswers, ResumeParseResponse, AIInsightResponse,
    Repository, LinkedInProfile, Roadmap, RoadmapProgress, TimestampedModel
)
from pydantic import BaseModel
import pymongo
from pymongo import ReturnDocument

logger = setup_logger(__name__)


class MongoCRUD:
    """Enhanced CRUD operations with Pydantic model support"""
    
    def __init__(self, collection_name: str):
        self.collection = MongoDBClient.get_database()[collection_name]
        self.collection_name = collection_name

    # Base CRUD Operations
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        try:
            result = await self.collection.find_one(query)
            return result
        except Exception as e:
            logger.error(f"Error in find_one for {self.collection_name}: {e}")
            raise

    async def find_many(
        self, 
        query: Dict[str, Any] = None, 
        limit: int = 100, 
        skip: int = 0,
        sort: List[tuple] = None
    ) -> List[Dict[str, Any]]:
        """Find multiple documents with pagination and sorting"""
        try:
            query = query or {}
            cursor = self.collection.find(query)
            
            if sort:
                cursor = cursor.sort(sort)
            if skip > 0:
                cursor = cursor.skip(skip)
            
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Error in find_many for {self.collection_name}: {e}")
            raise

    async def insert_one(self, document: Dict[str, Any]) -> Optional[str]:
        """Insert a single document and return the inserted ID"""
        try:
            # Add timestamp if document is timestamped
            if isinstance(document, dict) and 'created_at' not in document:
                document['created_at'] = datetime.now(timezone.utc)
                document['updated_at'] = datetime.now(timezone.utc)
            
            result = await self.collection.insert_one(document)
            return str(result.inserted_id) if result.acknowledged else None
        except Exception as e:
            logger.error(f"Error in insert_one for {self.collection_name}: {e}")
            raise

    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents and return inserted IDs"""
        try:
            # Add timestamps
            now = datetime.now(timezone.utc)
            for doc in documents:
                if 'created_at' not in doc:
                    doc['created_at'] = now
                    doc['updated_at'] = now
            
            result = await self.collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids] if result.acknowledged else []
        except Exception as e:
            logger.error(f"Error in insert_many for {self.collection_name}: {e}")
            raise

    async def replace_one(
        self, 
        query: Dict[str, Any], 
        document: Dict[str, Any], 
        upsert: bool = True
    ) -> bool:
        """Replace a single document"""
        try:
            # Update timestamp
            document['updated_at'] = datetime.now(timezone.utc)
            if upsert and 'created_at' not in document:
                document['created_at'] = datetime.now(timezone.utc)
            
            result = await self.collection.replace_one(query, document, upsert=upsert)
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error in replace_one for {self.collection_name}: {e}")
            raise

    async def update_one(
        self, 
        query: Dict[str, Any], 
        update: Dict[str, Any], 
        upsert: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Update a single document and return the updated document"""
        try:
            # Ensure proper update operators
            if not any(key.startswith('$') for key in update.keys()):
                update = {"$set": update}
            
            # Add updated timestamp
            if '$set' not in update:
                update['$set'] = {}
            update['$set']['updated_at'] = datetime.now(timezone.utc)
            
            result = await self.collection.find_one_and_update(
                query, 
                update, 
                upsert=upsert,
                return_document=ReturnDocument.AFTER
            )
            return result
        except Exception as e:
            logger.error(f"Error in update_one for {self.collection_name}: {e}")
            raise

    async def update_many(
        self, 
        query: Dict[str, Any], 
        update: Dict[str, Any]
    ) -> int:
        """Update multiple documents and return count of modified documents"""
        try:
            # Ensure proper update operators
            if not any(key.startswith('$') for key in update.keys()):
                update = {"$set": update}
            
            # Add updated timestamp
            if '$set' not in update:
                update['$set'] = {}
            update['$set']['updated_at'] = datetime.now(timezone.utc)
            
            result = await self.collection.update_many(query, update)
            return result.modified_count
        except Exception as e:
            logger.error(f"Error in update_many for {self.collection_name}: {e}")
            raise

    async def delete_one(self, query: Dict[str, Any]) -> bool:
        """Delete a single document"""
        try:
            result = await self.collection.delete_one(query)
            return result.acknowledged and result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error in delete_one for {self.collection_name}: {e}")
            raise

    async def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete multiple documents and return count of deleted documents"""
        try:
            result = await self.collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error in delete_many for {self.collection_name}: {e}")
            raise

    async def count_documents(self, query: Dict[str, Any] = None) -> int:
        """Count documents matching query"""
        try:
            query = query or {}
            return await self.collection.count_documents(query)
        except Exception as e:
            logger.error(f"Error in count_documents for {self.collection_name}: {e}")
            raise

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline"""
        try:
            cursor = self.collection.aggregate(pipeline)
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error in aggregate for {self.collection_name}: {e}")
            raise

    async def create_index(
        self, 
        keys: Union[str, List[tuple]], 
        unique: bool = False,
        sparse: bool = False
    ) -> str:
        """Create index on collection"""
        try:
            return await self.collection.create_index(
                keys, 
                unique=unique, 
                sparse=sparse
            )
        except Exception as e:
            logger.error(f"Error creating index for {self.collection_name}: {e}")
            raise

    # Pydantic Model Integration Methods
    async def insert_model(self, model: BaseModel) -> Optional[str]:
        """Insert a Pydantic model instance"""
        try:
            document = model.dict()
            return await self.insert_one(document)
        except Exception as e:
            logger.error(f"Error in insert_model for {self.collection_name}: {e}")
            raise

    async def find_model(
        self, 
        model_class: Type[BaseModel], 
        query: Dict[str, Any]
    ) -> Optional[BaseModel]:
        """Find and return a Pydantic model instance"""
        try:
            result = await self.find_one(query)
            return model_class(**result) if result else None
        except Exception as e:
            logger.error(f"Error in find_model for {self.collection_name}: {e}")
            raise

    async def find_models(
        self, 
        model_class: Type[BaseModel], 
        query: Dict[str, Any] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[BaseModel]:
        """Find and return multiple Pydantic model instances"""
        try:
            results = await self.find_many(query, limit=limit, skip=skip)
            return [model_class(**result) for result in results]
        except Exception as e:
            logger.error(f"Error in find_models for {self.collection_name}: {e}")
            raise

    async def update_model(
        self, 
        query: Dict[str, Any], 
        model: BaseModel, 
        upsert: bool = False
    ) -> Optional[BaseModel]:
        """Update with a Pydantic model and return updated model"""
        try:
            update_data = model.dict(exclude_unset=True)
            result = await self.update_one(query, update_data, upsert=upsert)
            return type(model)(**result) if result else None
        except Exception as e:
            logger.error(f"Error in update_model for {self.collection_name}: {e}")
            raise


# Specialized CRUD Classes for each model type
class PersonaCRUD(MongoCRUD):
    """CRUD operations for persona data"""
    
    def __init__(self):
        super().__init__("persona_steps")

    async def get_user_persona_steps(self, user_id: str) -> List[PersonaStepData]:
        """Get all persona steps for a user"""
        query = {"user_id": user_id}
        return await self.find_models(PersonaStepData, query)

    async def get_user_step(self, user_id: str, step: str) -> Optional[PersonaStepData]:
        """Get specific step for a user"""
        query = {"user_id": user_id, "step": step}
        return await self.find_model(PersonaStepData, query)

    async def save_step(self, step_data: PersonaStepData) -> Optional[str]:
        """Save or update a persona step"""
        query = {"user_id": step_data.user_id, "step": step_data.step}
        existing = await self.find_one(query)
        
        if existing:
            return await self.update_one(query, step_data.dict(exclude_unset=True))
        else:
            return await self.insert_model(step_data)


class PsychometricCRUD(MongoCRUD):
    """CRUD operations for psychometric data"""
    
    def __init__(self):
        super().__init__("psychometric_answers")

    async def get_user_psychometrics(self, user_id: str) -> Optional[PsychometricAnswers]:
        """Get psychometric data for user"""
        query = {"user_id": user_id}
        return await self.find_model(PsychometricAnswers, query)

    async def save_psychometrics(self, psychometric_data: PsychometricAnswers) -> Optional[str]:
        """Save psychometric data"""
        return await self.insert_model(psychometric_data)


class ResumeCRUD(MongoCRUD):
    """CRUD operations for resume data"""
    
    def __init__(self):
        super().__init__("resume_data")

    async def get_user_resume(self, user_id: str) -> Optional[ResumeParseResponse]:
        """Get latest resume for user"""
        query = {"user_id": user_id}
        sort = [("parsed_at", pymongo.DESCENDING)]
        results = await self.find_many(query, limit=1, sort=sort)
        return ResumeParseResponse(**results[0]) if results else None

    async def save_resume(self, resume_data: ResumeParseResponse) -> Optional[str]:
        """Save resume data"""
        return await self.insert_model(resume_data)


class RepositoryCRUD(MongoCRUD):
    """CRUD operations for GitHub repositories"""
    
    def __init__(self):
        super().__init__("repositories")
        
    async def get_user_repositories(self, user_id: str) -> List[Repository]:
        """Get all repositories for a user"""
        query = {"user_id": user_id}
        return await self.find_models(Repository, query)

    async def save_repository(self, repo_data: Repository) -> Optional[str]:
        """Save repository analysis"""
        return await self.insert_model(repo_data)

    async def get_repository_by_url(self, user_id: str, repo_url: str) -> Optional[Repository]:
        """Get specific repository by URL"""
        query = {"user_id": user_id, "repo_url": repo_url}
        return await self.find_model(Repository, query)


class LinkedInCRUD(MongoCRUD):
    """CRUD operations for LinkedIn profiles"""
    
    def __init__(self):
        super().__init__("linkedin_profiles")

    async def get_user_linkedin(self, user_id: str) -> Optional[LinkedInProfile]:
        """Get latest LinkedIn profile for user"""
        query = {"user_id": user_id}
        sort = [("scraped_at", pymongo.DESCENDING)]
        results = await self.find_many(query, limit=1, sort=sort)
        return LinkedInProfile(**results[0]) if results else None

    async def save_linkedin_profile(self, linkedin_data: LinkedInProfile) -> Optional[str]:
        """Save LinkedIn profile data"""
        return await self.insert_model(linkedin_data)


class RoadmapCRUD(MongoCRUD):
    """CRUD operations for roadmaps"""
    
    def __init__(self):
        super().__init__("roadmaps")

    async def get_user_roadmaps(self, user_id: str) -> List[Roadmap]:
        """Get all roadmaps for a user"""
        query = {"user_id": user_id}
        sort = [("created_at", pymongo.DESCENDING)]
        return await self.find_models(Roadmap, query)

    async def get_active_roadmap(self, user_id: str) -> Optional[Roadmap]:
        """Get user's active roadmap"""
        query = {"user_id": user_id, "status": "active"}
        return await self.find_model(Roadmap, query)

    async def save_roadmap(self, roadmap_data: Roadmap) -> Optional[str]:
        """Save roadmap"""
        return await self.insert_model(roadmap_data)

    async def update_roadmap_status(self, roadmap_id: str, status: str) -> bool:
        """Update roadmap status"""
        query = {"roadmap_id": roadmap_id}
        update = {"status": status}
        result = await self.update_one(query, update)
        return result is not None


class ProgressCRUD(MongoCRUD):
    """CRUD operations for roadmap progress"""
    
    def __init__(self):
        super().__init__("roadmap_progress")

    async def get_user_progress(self, user_id: str, roadmap_id: str) -> Optional[RoadmapProgress]:
        """Get progress for specific roadmap"""
        query = {"user_id": user_id, "roadmap_id": roadmap_id}
        return await self.find_model(RoadmapProgress, query)

    async def save_progress(self, progress_data: RoadmapProgress) -> Optional[str]:
        """Save progress data"""
        return await self.insert_model(progress_data)

    async def update_progress(
        self, 
        user_id: str, 
        roadmap_id: str, 
        progress_update: Dict[str, Any]
    ) -> Optional[RoadmapProgress]:
        """Update progress for a roadmap"""
        query = {"user_id": user_id, "roadmap_id": roadmap_id}
        result = await self.update_one(query, progress_update, upsert=True)
        return RoadmapProgress(**result) if result else None


class AIInsightCRUD(MongoCRUD):
    """CRUD operations for AI insights"""
    
    def __init__(self):
        super().__init__("ai_insights")

    async def get_user_latest_insight(self, user_id: str) -> Optional[AIInsightResponse]:
        """Get latest AI insight for user"""
        query = {"user_id": user_id}
        sort = [("generated_at", pymongo.DESCENDING)]
        results = await self.find_many(query, limit=1, sort=sort)
        return AIInsightResponse(**results[0]) if results else None

    async def save_insight(self, insight_data: AIInsightResponse) -> Optional[str]:
        """Save AI insight"""
        return await self.insert_model(insight_data)


# Database Initialization and Index Creation
async def initialize_database():
    """Create indexes for optimal query performance"""
    try:
        # Persona indexes
        persona_crud = PersonaCRUD()
        await persona_crud.create_index([("user_id", 1), ("step", 1)], unique=True)
        await persona_crud.create_index("updated_at")

        # Psychometric indexes
        psycho_crud = PsychometricCRUD()
        await psycho_crud.create_index("user_id", unique=True)

        # Resume indexes
        resume_crud = ResumeCRUD()
        await resume_crud.create_index("user_id")
        await resume_crud.create_index("parsed_at")

        # Repository indexes
        repo_crud = RepositoryCRUD()
        await repo_crud.create_index([("user_id", 1), ("repo_url", 1)], unique=True)
        await repo_crud.create_index("updated_at")

        # LinkedIn indexes
        linkedin_crud = LinkedInCRUD()
        await linkedin_crud.create_index("user_id")
        await linkedin_crud.create_index("scraped_at")

        # Roadmap indexes
        roadmap_crud = RoadmapCRUD()
        await roadmap_crud.create_index("user_id")
        await roadmap_crud.create_index("roadmap_id", unique=True)
        await roadmap_crud.create_index([("user_id", 1), ("status", 1)])

        # Progress indexes
        progress_crud = ProgressCRUD()
        await progress_crud.create_index([("user_id", 1), ("roadmap_id", 1)], unique=True)
        await progress_crud.create_index("last_activity_date")

        # AI Insight indexes
        insight_crud = AIInsightCRUD()
        await insight_crud.create_index("user_id")
        await insight_crud.create_index("generated_at")

        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error initializing database indexes: {e}")
        raise


# Export all CRUD classes
__all__ = [
    'MongoCRUD',
    'PersonaCRUD', 
    'PsychometricCRUD',
    'ResumeCRUD',
    'RepositoryCRUD', 
    'LinkedInCRUD',
    'RoadmapCRUD',
    'ProgressCRUD',
    'AIInsightCRUD',
    'initialize_database'
]
