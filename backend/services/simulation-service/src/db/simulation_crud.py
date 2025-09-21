from typing import List, Optional
from ..models.simulation_models import SimulationOutput, SimulationRequest
from .client import db_client
import uuid
from datetime import datetime

class SimulationCRUD:
    def __init__(self):
        self.collection_name = "simulations"
    
    async def create_simulation(self, request: SimulationRequest) -> str:
        simulation_id = str(uuid.uuid4())
        
        simulation_doc = {
            "simulation_id": simulation_id,
            "user_id": request.user_id,
            "simulation_type": request.simulation_type,
            "name": request.name,
            "status": "pending",
            "parameters": {
                "current_role": request.current_role.dict(),
                "target_role": request.target_role.dict(),
                "timeline_years": request.timeline_years,
                **request.parameters
            },
            "results": [],
            "summary": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if db_client.db:
            await db_client.db[self.collection_name].insert_one(simulation_doc)
        
        return simulation_id
    
    async def get_simulation(self, simulation_id: str) -> Optional[dict]:
        if not db_client.db:
            return None
        doc = await db_client.db[self.collection_name].find_one(
            {"simulation_id": simulation_id}
        )
        return doc
    
    async def update_simulation(self, simulation_id: str, update_data: dict):
        if not db_client.db:
            return
        update_data["updated_at"] = datetime.utcnow()
        await db_client.db[self.collection_name].update_one(
            {"simulation_id": simulation_id},
            {"$set": update_data}
        )
    
    async def list_simulations(self, user_id: str = None) -> List[dict]:
        if not db_client.db:
            return []
        query = {}
        if user_id:
            query["user_id"] = user_id
        cursor = db_client.db[self.collection_name].find(query).sort("created_at", -1)
        return await cursor.to_list(length=100)

simulation_crud = SimulationCRUD()
