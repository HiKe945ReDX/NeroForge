"""Career Discovery Processor - Match users to careers"""
import json
from typing import List, Dict

class DiscoveryProcessor:
    def __init__(self):
        self.skills_db = {}
        self.careers_db = {}
    
    def process_discovery_answers(self, answers: Dict) -> List[Dict]:
        """
        Process 5 discovery questions and return top 5 career matches
        answers: {
            'subjects': str,
            'activities': str,
            'workstyle': str,
            'impact': str,
            'environment': str
        }
        """
        # Simplified matching algorithm
        career_scores = self._calculate_matches(answers)
        top_careers = sorted(career_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:5]
        return [{"career": k, **v} for k, v in top_careers]
    
    def _calculate_matches(self, answers: Dict) -> Dict:
        """Internal: Calculate career match scores"""
        # Default career mapping (expand with real data)
        careers = {
            "Software Engineer": {"score": 85, "reason": "Matches technical skills"},
            "Data Scientist": {"score": 78, "reason": "Strong analytical foundation"},
            "Product Manager": {"score": 72, "reason": "Good leadership potential"},
            "UX Designer": {"score": 65, "reason": "Creative thinking detected"},
            "DevOps Engineer": {"score": 70, "reason": "Systems thinking strength"}
        }
        return careers

processor = DiscoveryProcessor()
