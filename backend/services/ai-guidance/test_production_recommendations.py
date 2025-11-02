import requests
import json
import numpy as np

API_URL = "https://guidora-career-746485305795.us-central1.run.app"

# Simulate different user personas
personas = {
    "ml_enthusiast": {
        "name": "ML Enthusiast (Python, TensorFlow, Math)",
        "embedding": [0.8] * 200 + [0.1] * 568  # High ML skills
    },
    "frontend_dev": {
        "name": "Frontend Developer (React, JavaScript, UI)",
        "embedding": [0.1] * 400 + [0.9] * 200 + [0.1] * 168
    },
    "healthcare_worker": {
        "name": "Healthcare Worker (Medical, Patient Care)",
        "embedding": [0.1] * 600 + [0.8] * 168
    },
    "business_analyst": {
        "name": "Business Analyst (SQL, Excel, Strategy)",
        "embedding": [0.5] * 300 + [0.3] * 468
    }
}

print("🔍 TESTING PRODUCTION CAREER RECOMMENDATIONS\n")

for persona_id, persona_data in personas.items():
    print(f"{'='*60}")
    print(f"👤 PERSONA: {persona_data['name']}")
    print(f"{'='*60}")
    
    response = requests.post(
        f"{API_URL}/api/careers/recommend",
        json={
            "persona_embedding": persona_data['embedding'],
            "top_k": 5
        }
    )
    
    if response.status_code == 200:
        matches = response.json()['matches']
        print(f"\n🎯 TOP 5 CAREER MATCHES:\n")
        for i, match in enumerate(matches, 1):
            print(f"  {i}. {match['title']}")
            print(f"     Fit Score: {match['fit_score']:.2f}")
            print(f"     Skills: {', '.join(match['skills'][:3])}...")
            print()
    else:
        print(f"❌ ERROR: {response.status_code}")
    
    print()

print("\n✅ PRODUCTION TEST COMPLETE!")
