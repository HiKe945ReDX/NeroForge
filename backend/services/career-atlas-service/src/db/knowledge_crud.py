
from typing import Dict, Any, List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING
import logging
from datetime import datetime

from ..models.knowledge_models import (
    KnowledgeNode, KnowledgeRelationship, NodeType, RelationshipType,
    SkillNode, CareerNode, KnowledgeGraphStats
)
from ..db.client import DatabaseManager
from ..utils.logging import setup_logging

logger = logging.getLogger(__name__)

class NodeType(str, Enum):
    CAREER = "career"
    SKILL = "skill"
    DOMAIN = "domain"
    INDUSTRY = "industry"
    COMPANY = "company"
    EDUCATION = "education"
    CERTIFICATION = "certification"

class RelationshipType(str, Enum):
    REQUIRES = "requires"
    PREFERS = "prefers"
    RELATES_TO = "relates_to"
    TRANSFERS_TO = "transfers_to"
    BELONGS_TO = "belongs_to"
    LEADS_TO = "leads_to"
    OFFERS = "offers"
    ISSUES = "issues"

class KnowledgeNode(BaseModel):
    node_id: str = Field(..., description="Unique identifier")
    node_type: NodeType = Field(..., description="Type of the node")
    name: str = Field(..., description="Display name")
    description: Optional[str] = Field(None, description="Detailed description")
    properties: Dict[str, any] = Field(default_factory=dict, description="Additional attributes")
    weight: float = Field(default=1.0, ge=0, description="Node importance")

class KnowledgeRelationship(BaseModel):
    source_id: str = Field(..., description="Source node id")
    target_id: str = Field(..., description="Target node id")
    relationship_type: RelationshipType = Field(..., description="Relationship type")
    weight: float = Field(default=1.0, ge=0, description="Connection strength")
    properties: Dict[str, any] = Field(default_factory=dict, description="Additional attributes")

class SkillNode(KnowledgeNode):
    node_type: NodeType = Field(default=NodeType.SKILL)

class CareerNode(KnowledgeNode):
    node_type: NodeType = Field(default=NodeType.CAREER)

class KnowledgeGraphStats(BaseModel):
    total_nodes: int = 0
    total_relationships: int = 0
    node_types: Dict[str, int] = Field(default_factory=dict)
    relationship_types: Dict[str, int] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
