#!/usr/bin/env python3
"""
PRODUCTION TEST: Real Vertex AI embeddings with error handling
"""

import requests
import json
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
import os

# Initialize Vertex AI
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser("~/main/backend/configs/keys/Guidora-key.json")
aiplatform.init(project="guidora-main", location="us-central1")

API_URL = "https://guidora-career-746485305795.us-central1.run.app"

def generate_embedding(text: str):
    """Generate 768-dim embedding using Vertex AI"""
    model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    embeddings = model.get_embeddings([text])
    return embeddings[0].values

# Create REAL persona descriptions
personas = {
    "ml_enthusiast": {
        "name": "ML Enthusiast",
        "description": "Expert in Python, TensorFlow, PyTorch, machine learning algorithms, deep learning, neural networks, data science, statistics, mathematics, scikit-learn"
    },
    "frontend_dev": {
        "name": "Frontend Developer",
        "description": "Skilled in React, JavaScript, HTML, CSS, TypeScript, Redux, web development, user interface design, responsive design, frontend frameworks"
    },
    "healthcare_worker": {
        "name": "Healthcare Worker",
        "description": "Experienced in patient care, medical procedures, nursing, healthcare, clinical skills, emergency response, medical charting, IV administration"
    },
    "data_engineer": {
        "name": "Data Engineer",
        "description": "Expert in Python, SQL, Apache Spark, Airflow, Kafka, ETL pipelines, data warehousing, big data, AWS, cloud infrastructure"
    }
}

print("🔍 PRODUCTION TEST: REAL VERTEX AI EMBEDDINGS\n")
print("=" * 70)

for persona_id, persona_data in personas.items():
    print(f"\n👤 PERSONA: {persona_data['name']}")
    print(f"📝 Description: {persona_data['description'][:60]}...")
    print("=" * 70)
    
    # Generate REAL embedding using Vertex AI
    print("⏳ Generating embedding with Vertex AI...")
    embedding = generate_embedding(persona_data['description'])
    print(f"✅ Generated {len(embedding)}-dimensional embedding")
    
    # Get recommendations
    response = requests.post(
        f"{API_URL}/api/careers/recommend",
        json={
            "persona_embedding": embedding,
            "top_k": 5
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        matches = result.get('matches', [])
        
        # Handle both old and new API response formats
        confidence = result.get('recommendation_confidence', 'N/A')
        
        print(f"\n🎯 TOP 5 CAREER MATCHES (Confidence: {confidence}):\n")
        
        for i, match in enumerate(matches, 1):
            print(f"  {i}. {match['title']}")
            
            # Handle different response formats
            if 'fit_score' in match and isinstance(match['fit_score'], (int, float)):
                fit_score = match['fit_score']
                if fit_score < 10:  # Raw similarity score (not percentage)
                    # Convert to percentage: (score + 1) / 2 * 100
                    fit_percentage = ((fit_score + 1) / 2) * 100
                else:  # Already percentage
                    fit_percentage = fit_score
                
                print(f"     ✨ Fit Score: {fit_percentage:.2f}%")
            else:
                print(f"     ✨ Fit Score: {match.get('fit_score', 'N/A')}")
            
            # Salary info
            salary_range = match.get('salary_range', {})
            if isinstance(salary_range, dict):
                print(f"     💼 Salary: ${salary_range.get('min', 0):,} - ${salary_range.get('max', 0):,}")
            
            # Demand and growth
            print(f"     📈 Demand: {match.get('demand_score', 'N/A')}/100 | Growth: {match.get('growth_rate', 'N/A')}%")
            
            # Skills
            skills = match.get('skills', [])
            if skills:
                print(f"     🔧 Skills: {', '.join(skills[:4])}...")
            print()
    else:
        print(f"❌ ERROR {response.status_code}: {response.text}")
    
    print()

print("\n" + "=" * 70)
print("✅ PRODUCTION TEST COMPLETE!")
print("=" * 70)
