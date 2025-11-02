import networkx as nx
from typing import Dict, List, Optional, Any, Tuple
import json
import asyncio
from datetime import datetime
import logging

# Fixed imports with relative paths
from ..db.client import DatabaseManager
from ..models.knowledge_models import (
    KnowledgeNode, KnowledgeRelationship, NodeType, RelationshipType, 
    SkillNode, CareerNode, KnowledgeGraphStats
)
from .config import get_settings

logger = logging.getLogger(__name__)

class KnowledgeEngine:
    """
    Production-ready NetworkX knowledge graph engine for career intelligence
    Handles relationships between careers, skills, domains, and companies
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.settings = get_settings()
        self.graph = nx.DiGraph()  # Directed graph for hierarchical relationships
        self.initialized = False
        self.node_cache = {}
        self.relationship_cache = {}
    
    async def initialize(self):
        """Initialize knowledge graph with seed data"""
        try:
            logger.info("🧠 Initializing Knowledge Graph Engine...")
            
            # Create collections if they don't exist
            await self._ensure_collections()
            
            # Load graph from database
            await self._load_graph()
            
            # Add seed data if graph is empty
            if self.graph.number_of_nodes() == 0:
                await self._seed_initial_data()
            
            self.initialized = True
            logger.info(f"✅ Knowledge Graph initialized with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} relationships")
            
        except Exception as e:
            logger.error(f"❌ Knowledge Graph initialization failed: {e}")
            raise
    
    async def _ensure_collections(self):
        """Create collections if they don't exist"""
        collections = ["knowledge_nodes", "knowledge_relationships", "career_paths", "skill_clusters"]
        for collection_name in collections:
            try:
                collection = self.db_manager.get_collection(collection_name)
                # Create indexes for better performance
                if collection_name == "knowledge_nodes":
                    await collection.create_index([("node_id", 1)], unique=True)
                    await collection.create_index([("node_type", 1)])
                elif collection_name == "knowledge_relationships":
                    await collection.create_index([("source_id", 1), ("target_id", 1)])
                    await collection.create_index([("relationship_type", 1)])
                    
                logger.info(f"📚 Collection '{collection_name}' ready")
            except Exception as e:
                logger.warning(f"Collection setup warning for {collection_name}: {e}")
    
    async def _load_graph(self):
        """Load existing graph from database"""
        try:
            # Load nodes
            nodes_collection = self.db_manager.get_collection("knowledge_nodes")
            async for node_doc in nodes_collection.find({}):
                node_data = {
                    "id": node_doc["node_id"],
                    "type": node_doc["node_type"],
                    "name": node_doc.get("name", ""),
                    "description": node_doc.get("description", ""),
                    "properties": node_doc.get("properties", {}),
                    "weight": node_doc.get("weight", 1.0)
                }
                self.graph.add_node(node_doc["node_id"], **node_data)
            
            # Load relationships
            relationships_collection = self.db_manager.get_collection("knowledge_relationships")
            async for rel_doc in relationships_collection.find({}):
                self.graph.add_edge(
                    rel_doc["source_id"],
                    rel_doc["target_id"],
                    relationship_type=rel_doc["relationship_type"],
                    weight=rel_doc.get("weight", 1.0),
                    properties=rel_doc.get("properties", {})
                )
            
            logger.info(f"📊 Loaded {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} relationships")
            
        except Exception as e:
            logger.warning(f"Graph loading warning: {e}")
    
    async def _seed_initial_data(self):
        """Seed initial knowledge graph data"""
        try:
            logger.info("🌱 Seeding initial knowledge graph data...")
            
            # Core technology skills
            tech_skills = [
                {"id": "python", "name": "Python", "type": "skill", "category": "programming"},
                {"id": "javascript", "name": "JavaScript", "type": "skill", "category": "programming"},
                {"id": "react", "name": "React", "type": "skill", "category": "frontend"},
                {"id": "nodejs", "name": "Node.js", "type": "skill", "category": "backend"},
                {"id": "mongodb", "name": "MongoDB", "type": "skill", "category": "database"},
                {"id": "aws", "name": "AWS", "type": "skill", "category": "cloud"},
                {"id": "docker", "name": "Docker", "type": "skill", "category": "devops"},
                {"id": "machine_learning", "name": "Machine Learning", "type": "skill", "category": "ai"}
            ]
            
            # Core career paths
            career_paths = [
                {"id": "software_engineer", "name": "Software Engineer", "type": "career", "level": "mid"},
                {"id": "frontend_developer", "name": "Frontend Developer", "type": "career", "level": "mid"},
                {"id": "backend_developer", "name": "Backend Developer", "type": "career", "level": "mid"},
                {"id": "fullstack_developer", "name": "Full Stack Developer", "type": "career", "level": "mid"},
                {"id": "data_scientist", "name": "Data Scientist", "type": "career", "level": "mid"},
                {"id": "devops_engineer", "name": "DevOps Engineer", "type": "career", "level": "mid"},
                {"id": "ai_engineer", "name": "AI Engineer", "type": "career", "level": "mid"}
            ]
            
            # Add nodes to graph
            for skill in tech_skills:
                await self._add_node(skill["id"], NodeType.SKILL, skill["name"], properties=skill)
            
            for career in career_paths:
                await self._add_node(career["id"], NodeType.CAREER, career["name"], properties=career)
            
            # Add relationships (career requires skills)
            relationships = [
                ("software_engineer", "python", "requires"),
                ("software_engineer", "javascript", "requires"),
                ("frontend_developer", "javascript", "requires"),
                ("frontend_developer", "react", "requires"),
                ("backend_developer", "python", "requires"),
                ("backend_developer", "nodejs", "requires"),
                ("fullstack_developer", "javascript", "requires"),
                ("fullstack_developer", "python", "requires"),
                ("fullstack_developer", "react", "requires"),
                ("data_scientist", "python", "requires"),
                ("data_scientist", "machine_learning", "requires"),
                ("devops_engineer", "aws", "requires"),
                ("devops_engineer", "docker", "requires"),
                ("ai_engineer", "python", "requires"),
                ("ai_engineer", "machine_learning", "requires")
            ]
            
            for career_id, skill_id, rel_type in relationships:
                await self._add_relationship(career_id, skill_id, RelationshipType.REQUIRES, weight=0.8)
            
            logger.info("✅ Seeded initial knowledge graph data")
            
        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}")
            raise
    
    async def _add_node(self, node_id: str, node_type: NodeType, name: str, description: str = "", properties: dict = None):
        """Add node to graph and database"""
        try:
            # Add to graph
            self.graph.add_node(
                node_id,
                id=node_id,
                type=node_type.value,
                name=name,
                description=description,
                properties=properties or {}
            )
            
            # Save to database
            nodes_collection = self.db_manager.get_collection("knowledge_nodes")
            node_doc = {
                "node_id": node_id,
                "node_type": node_type.value,
                "name": name,
                "description": description,
                "properties": properties or {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await nodes_collection.update_one(
                {"node_id": node_id},
                {"$set": node_doc},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Failed to add node {node_id}: {e}")
            raise
    
    async def _add_relationship(self, source_id: str, target_id: str, rel_type: RelationshipType, weight: float = 1.0, properties: dict = None):
        """Add relationship to graph and database"""
        try:
            # Add to graph
            self.graph.add_edge(
                source_id,
                target_id,
                relationship_type=rel_type.value,
                weight=weight,
                properties=properties or {}
            )
            
            # Save to database
            relationships_collection = self.db_manager.get_collection("knowledge_relationships")
            rel_doc = {
                "source_id": source_id,
                "target_id": target_id,
                "relationship_type": rel_type.value,
                "weight": weight,
                "properties": properties or {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await relationships_collection.update_one(
                {"source_id": source_id, "target_id": target_id, "relationship_type": rel_type.value},
                {"$set": rel_doc},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Failed to add relationship {source_id} -> {target_id}: {e}")
            raise
    
    async def find_career_paths(self, skills: List[str], experience_level: str = "mid") -> List[Dict]:
        """Find career paths based on user skills"""
        if not self.initialized:
            await self.initialize()
        
        try:
            matching_careers = []
            
            # Find careers that match user skills
            for node_id in self.graph.nodes():
                node = self.graph.nodes[node_id]
                if node.get("type") == "career":
                    
                    # Get required skills for this career
                    required_skills = []
                    for neighbor in self.graph.neighbors(node_id):
                        edge_data = self.graph[node_id][neighbor]
                        if edge_data.get("relationship_type") == "requires":
                            required_skills.append(neighbor)
                    
                    # Calculate skill match percentage
                    if required_skills:
                        matched_skills = set(skills).intersection(set(required_skills))
                        match_percentage = len(matched_skills) / len(required_skills)
                        
                        if match_percentage > 0.3:  # At least 30% match
                            career_info = {
                                "career_id": node_id,
                                "career_name": node.get("name", node_id),
                                "match_percentage": round(match_percentage * 100, 1),
                                "matched_skills": list(matched_skills),
                                "missing_skills": list(set(required_skills) - set(skills)),
                                "total_required_skills": len(required_skills)
                            }
                            matching_careers.append(career_info)
            
            # Sort by match percentage
            matching_careers.sort(key=lambda x: x["match_percentage"], reverse=True)
            
            return matching_careers[:10]  # Return top 10 matches
            
        except Exception as e:
            logger.error(f"Career path finding failed: {e}")
            return []
    
    async def get_skill_recommendations(self, career_id: str) -> List[str]:
        """Get skill recommendations for a specific career"""
        if not self.initialized:
            await self.initialize()
        
        try:
            recommended_skills = []
            
            if career_id in self.graph.nodes():
                # Get direct skill requirements
                for neighbor in self.graph.neighbors(career_id):
                    edge_data = self.graph[career_id][neighbor]
                    if edge_data.get("relationship_type") == "requires":
                        skill_node = self.graph.nodes[neighbor]
                        recommended_skills.append({
                            "skill_id": neighbor,
                            "skill_name": skill_node.get("name", neighbor),
                            "importance": edge_data.get("weight", 1.0),
                            "category": skill_node.get("properties", {}).get("category", "general")
                        })
            
            # Sort by importance
            recommended_skills.sort(key=lambda x: x["importance"], reverse=True)
            
            return recommended_skills
            
        except Exception as e:
            logger.error(f"Skill recommendation failed: {e}")
            return []
    
    async def analyze_skill_gap(self, user_skills: List[str], target_career: str) -> Dict:
        """Analyze skill gap for a target career"""
        if not self.initialized:
            await self.initialize()
        
        try:
            required_skills = await self.get_skill_recommendations(target_career)
            required_skill_ids = [skill["skill_id"] for skill in required_skills]
            
            user_skill_set = set(user_skills)
            required_skill_set = set(required_skill_ids)
            
            matched_skills = user_skill_set.intersection(required_skill_set)
            missing_skills = required_skill_set - user_skill_set
            
            analysis = {
                "target_career": target_career,
                "total_required_skills": len(required_skill_set),
                "matched_skills": list(matched_skills),
                "missing_skills": list(missing_skills),
                "completion_percentage": round(len(matched_skills) / len(required_skill_set) * 100, 1) if required_skill_set else 0,
                "readiness_level": self._calculate_readiness_level(len(matched_skills), len(required_skill_set))
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {e}")
            return {}
    
    def _calculate_readiness_level(self, matched_count: int, total_count: int) -> str:
        """Calculate readiness level based on skill match"""
        if total_count == 0:
            return "unknown"
        
        percentage = matched_count / total_count
        
        if percentage >= 0.8:
            return "ready"
        elif percentage >= 0.6:
            return "nearly_ready"
        elif percentage >= 0.4:
            return "developing"
        else:
            return "beginner"
    
    async def get_graph_stats(self) -> KnowledgeGraphStats:
        """Get knowledge graph statistics"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Count nodes by type
            node_types = {}
            for node_id in self.graph.nodes():
                node_type = self.graph.nodes[node_id].get("type", "unknown")
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            # Count relationships by type
            relationship_types = {}
            for source, target in self.graph.edges():
                rel_type = self.graph[source][target].get("relationship_type", "unknown")
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
            
            stats = KnowledgeGraphStats(
                total_nodes=self.graph.number_of_nodes(),
                total_relationships=self.graph.number_of_edges(),
                node_types=node_types,
                relationship_types=relationship_types,
                last_updated=datetime.utcnow()
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Stats calculation failed: {e}")
            return KnowledgeGraphStats()

# Global instance
_knowledge_engine_instance = None

async def get_knowledge_engine(db_manager: DatabaseManager) -> KnowledgeEngine:
    """Get or create knowledge engine instance"""
    global _knowledge_engine_instance
    
    if _knowledge_engine_instance is None:
        _knowledge_engine_instance = KnowledgeEngine(db_manager)
        await _knowledge_engine_instance.initialize()
    
    return _knowledge_engine_instance
