import networkx as nx
from typing import Dict, List
from datetime import datetime
import logging

from ..db.client import DatabaseManager

logger = logging.getLogger(__name__)

class KnowledgeEngine:
    """
    Decoupled Knowledge Graph Engine — returns plain dicts to avoid model circulars.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.graph = nx.DiGraph()
        self.initialized = False

    async def initialize(self):
        try:
            logger.info("🧠 Initializing Knowledge Graph Engine...")
            # Try DB load; if not available or empty, fall back to basic graph
            try:
                await self._load_from_database()
                if self.graph.number_of_nodes() == 0:
                    await self._create_basic_graph()
            except Exception as e:
                logger.warning(f"DB load failed, using basic graph: {e}")
                await self._create_basic_graph()

            self.initialized = True
            logger.info(
                f"✅ Knowledge Graph ready: {self.graph.number_of_nodes()} nodes, "
                f"{self.graph.number_of_edges()} edges"
            )
        except Exception as e:
            logger.error(f"❌ Knowledge Graph initialization failed: {e}")
            await self._create_minimal_graph()
            self.initialized = True

    async def _load_from_database(self):
        nodes = self.db_manager.get_collection("knowledge_nodes")
        rels = self.db_manager.get_collection("knowledge_relationships")

        # Shallow load with bounds to avoid heavy startup
        count = await nodes.count_documents({})
        if count == 0:
            return

        async for n in nodes.find({}).limit(500):
            node_id = n.get("node_id")
            if not node_id:
                continue
            self.graph.add_node(
                node_id,
                type=n.get("node_type", "unknown"),
                name=n.get("name", node_id),
                properties=n.get("properties", {}),
            )

        async for r in rels.find({}).limit(1000):
            s = r.get("source_id")
            t = r.get("target_id")
            if not s or not t or s not in self.graph.nodes or t not in self.graph.nodes:
                continue
            self.graph.add_edge(
                s,
                t,
                relationship_type=r.get("relationship_type", "relates_to"),
                weight=r.get("weight", 1.0),
                properties=r.get("properties", {}),
            )

    async def _create_basic_graph(self):
        skills = [
            {"id": "python", "name": "Python", "category": "programming"},
            {"id": "javascript", "name": "JavaScript", "category": "programming"},
            {"id": "react", "name": "React", "category": "frontend"},
            {"id": "nodejs", "name": "Node.js", "category": "backend"},
            {"id": "sql", "name": "SQL", "category": "database"},
            {"id": "aws", "name": "AWS", "category": "cloud"},
            {"id": "docker", "name": "Docker", "category": "devops"},
            {"id": "machine_learning", "name": "Machine Learning", "category": "ai"},
        ]
        careers = [
            {"id": "software_engineer", "name": "Software Engineer", "level": "mid"},
            {"id": "frontend_developer", "name": "Frontend Developer", "level": "mid"},
            {"id": "backend_developer", "name": "Backend Developer", "level": "mid"},
            {"id": "fullstack_developer", "name": "Full Stack Developer", "level": "mid"},
            {"id": "data_scientist", "name": "Data Scientist", "level": "mid"},
            {"id": "devops_engineer", "name": "DevOps Engineer", "level": "mid"},
            {"id": "ai_engineer", "name": "AI Engineer", "level": "mid"},
        ]
        rels = [
            ("software_engineer", "python", 0.9),
            ("software_engineer", "javascript", 0.8),
            ("frontend_developer", "javascript", 0.95),
            ("frontend_developer", "react", 0.9),
            ("backend_developer", "python", 0.9),
            ("backend_developer", "nodejs", 0.8),
            ("backend_developer", "sql", 0.85),
            ("fullstack_developer", "javascript", 0.9),
            ("fullstack_developer", "python", 0.8),
            ("data_scientist", "python", 0.95),
            ("data_scientist", "machine_learning", 0.9),
            ("devops_engineer", "aws", 0.9),
            ("devops_engineer", "docker", 0.85),
            ("ai_engineer", "python", 0.95),
            ("ai_engineer", "machine_learning", 0.9),
        ]

        for s in skills:
            self.graph.add_node(s["id"], **s, type="skill")
        for c in careers:
            self.graph.add_node(c["id"], **c, type="career")
        for c_id, s_id, w in rels:
            if c_id in self.graph.nodes and s_id in self.graph.nodes:
                self.graph.add_edge(c_id, s_id, relationship_type="requires", weight=w)

    async def _create_minimal_graph(self):
        self.graph.add_node("software_engineer", name="Software Engineer", type="career")
        self.graph.add_node("python", name="Python", type="skill")
        self.graph.add_edge("software_engineer", "python", relationship_type="requires", weight=0.9)

    async def find_career_paths(self, skills: List[str], experience_level: str = "mid") -> List[Dict]:
        if not self.initialized:
            await self.initialize()

        matches: List[Dict] = []
        for node_id in list(self.graph.nodes):
            node = self.graph.nodes[node_id]
            if node.get("type") != "career":
                continue
            required = []
            for neighbor in self.graph.neighbors(node_id):
                edge = self.graph[node_id][neighbor]
                if edge.get("relationship_type") == "requires":
                    required.append(neighbor)
            if not required:
                continue
            matched = set(skills) & set(required)
            pct = (len(matched) / len(required)) * 100
            if pct >= 20:
                matches.append({
                    "career_id": node_id,
                    "career_name": node.get("name", node_id.replace("_", " ").title()),
                    "match_percentage": round(pct, 1),
                    "matched_skills": sorted(list(matched)),
                    "missing_skills": sorted(list(set(required) - matched)),
                    "required_skills_count": len(required),
                    "experience_level": node.get("level", "mid"),
                })
        matches.sort(key=lambda x: x["match_percentage"], reverse=True)
        return matches[:5]

    async def get_skill_recommendations(self, career_id: str) -> List[Dict]:
        if not self.initialized:
            await self.initialize()

        recs: List[Dict] = []
        if career_id in self.graph.nodes:
            for neighbor in self.graph.neighbors(career_id):
                edge = self.graph[career_id][neighbor]
                if edge.get("relationship_type") == "requires":
                    skill_node = self.graph.nodes[neighbor]
                    recs.append({
                        "skill_id": neighbor,
                        "skill_name": skill_node.get("name", neighbor.replace("_", " ").title()),
                        "importance": edge.get("weight", 1.0),
                        "category": skill_node.get("category", "general"),
                    })
        recs.sort(key=lambda x: x["importance"], reverse=True)
        return recs

    async def analyze_skill_gap(self, user_skills: List[str], target_career: str) -> Dict:
        recs = await self.get_skill_recommendations(target_career)
        required_ids = [r["skill_id"] for r in recs]
        matched = sorted(list(set(user_skills) & set(required_ids)))
        missing = sorted(list(set(required_ids) - set(user_skills)))
        completion = (len(matched) / len(required_ids) * 100) if required_ids else 0.0

        if completion >= 80:
            level = "ready"
        elif completion >= 60:
            level = "nearly_ready"
        elif completion >= 40:
            level = "developing"
        else:
            level = "beginner"

        recommendation = "You are ready!" if not missing else "Focus on: " + ", ".join(missing[:3])

        return {
            "target_career": target_career,
            "completion_percentage": round(completion, 1),
            "readiness_level": level,
            "matched_skills": matched,
            "missing_skills": missing,
            "total_required": len(required_ids),
            "recommendation": recommendation,
        }

_knowledge_engine_instance = None

async def get_knowledge_engine(db_manager: DatabaseManager) -> KnowledgeEngine:
    global _knowledge_engine_instance
    if _knowledge_engine_instance is None:
        _knowledge_engine_instance = KnowledgeEngine(db_manager)
        await _knowledge_engine_instance.initialize()
    return _knowledge_engine_instance
