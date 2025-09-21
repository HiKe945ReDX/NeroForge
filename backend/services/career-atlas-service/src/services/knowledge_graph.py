from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class NodeType(str, Enum):
    """Types of nodes in the knowledge graph"""
    CAREER = "career"
    SKILL = "skill"
    DOMAIN = "domain"
    INDUSTRY = "industry"
    COMPANY = "company"
    EDUCATION = "education"
    CERTIFICATION = "certification"

class RelationshipType(str, Enum):
    """Types of relationships in the knowledge graph"""
    REQUIRES = "requires"
    PREFERS = "prefers"
    RELATES_TO = "relates_to"
    TRANSFERS_TO = "transfers_to"
    BELONGS_TO = "belongs_to"
    LEADS_TO = "leads_to"
    OFFERS = "offers"
    ISSUES = "issues"

class KnowledgeNode(BaseModel):
    """Base model for knowledge graph nodes"""
    node_id: str = Field(..., description="Unique identifier for the node")
    node_type: NodeType = Field(..., description="Type of the node")
    name: str = Field(..., description="Display name of the node")
    description: Optional[str] = Field(None, description="Detailed description")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional node properties")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True

class SkillNode(KnowledgeNode):
    """Skill node in the knowledge graph"""
    node_type: NodeType = NodeType.SKILL
    skill_category: str = Field(..., description="Category of the skill (technical, soft, domain)")
    proficiency_levels: List[str] = Field(default=["Beginner", "Intermediate", "Advanced", "Expert"])
    learning_resources: List[Dict[str, str]] = Field(default_factory=list)
    market_demand: float = Field(0.0, ge=0.0, le=1.0, description="Market demand score 0-1")
    average_salary_impact: int = Field(0, description="Average salary impact in USD")

class CareerNode(KnowledgeNode):
    """Career node in the knowledge graph"""
    node_type: NodeType = NodeType.CAREER
    domain: str = Field(..., description="Career domain")
    level: str = Field(..., description="Career level (entry, mid, senior)")
    median_salary: int = Field(0, description="Median salary in USD")
    growth_rate: float = Field(0.0, description="Job growth rate percentage")
    demand_score: float = Field(0.0, ge=0.0, le=1.0)
    remote_friendly: bool = Field(False)

class KnowledgeRelationship(BaseModel):
    """Relationship between nodes in the knowledge graph"""
    relationship_id: str = Field(..., description="Unique identifier for the relationship")
    source_node_id: str = Field(..., description="Source node identifier")
    target_node_id: str = Field(..., description="Target node identifier")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    weight: float = Field(1.0, ge=0.0, le=1.0, description="Relationship strength/importance")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional relationship properties")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True

class LearningPath(BaseModel):
    """Learning path recommendation model"""
    path_id: str = Field(..., description="Unique identifier for the path")
    source_skills: List[str] = Field(..., description="Starting skills")
    target_career: str = Field(..., description="Target career")
    required_skills: List[Dict[str, Any]] = Field(..., description="Skills needed to acquire")
    estimated_timeline: Dict[str, str] = Field(..., description="Estimated learning timeline")
    difficulty_level: str = Field(..., description="Overall difficulty assessment")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Confidence in recommendation")
    alternative_paths: List[Dict[str, Any]] = Field(default_factory=list)

class SkillGap(BaseModel):
    """Skill gap analysis model"""
    analysis_id: str = Field(..., description="Unique identifier for the analysis")
    current_skills: List[str] = Field(..., description="Current skill set")
    target_position: str = Field(..., description="Target position/career")
    missing_skills: List[Dict[str, Any]] = Field(..., description="Skills that need to be developed")
    skill_priorities: Dict[str, int] = Field(..., description="Priority ranking of skills")
    development_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    market_alignment: float = Field(0.0, ge=0.0, le=1.0, description="How well skills align with market demand")

class CareerTransitionPath(BaseModel):
    """Career transition path model"""
    transition_id: str = Field(..., description="Unique identifier for the transition")
    from_career: str = Field(..., description="Current career")
    to_career: str = Field(..., description="Target career")
    transition_difficulty: str = Field(..., description="Difficulty level (Easy, Medium, Hard)")
    transferable_skills: List[str] = Field(..., description="Skills that transfer directly")
    skills_to_develop: List[Dict[str, Any]] = Field(..., description="New skills to develop")
    potential_bridges: List[str] = Field(default_factory=list, description="Intermediate career steps")
    success_factors: List[str] = Field(default_factory=list)
    estimated_timeline: str = Field(..., description="Estimated transition timeline")
    salary_impact: Dict[str, Any] = Field(default_factory=dict, description="Expected salary changes")

class KnowledgeGraphStats(BaseModel):
    """Statistics about the knowledge graph"""
    total_nodes: int = Field(0, description="Total number of nodes")
    total_relationships: int = Field(0, description="Total number of relationships")
    node_type_counts: Dict[str, int] = Field(default_factory=dict)
    relationship_type_counts: Dict[str, int] = Field(default_factory=dict)
    graph_density: float = Field(0.0, description="Graph density metric")
    average_node_degree: float = Field(0.0, description="Average connections per node")
    last_updated: datetime = Field(default_factory=datetime.now)
    data_quality_score: float = Field(0.0, ge=0.0, le=1.0)

# Additional models for career matching, validation, etc...
