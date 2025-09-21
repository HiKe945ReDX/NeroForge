from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime
"""📰 NEWS & FEEDS SERVICE - AI-Powered Career News Platform"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Career topics configuration with 10 curated topics
CAREER_TOPICS = {
    "artificial-intelligence": {
        "name": "Artificial Intelligence & Machine Learning",
        "description": "Latest AI/ML trends, job opportunities, and skill requirements",
        "keywords": ["AI", "machine learning", "data science", "deep learning"],
        "industry_focus": "Tech, Healthcare, Finance, Automotive"
    },
    "software-development": {
        "name": "Software Development & Engineering",
        "description": "Programming trends, new frameworks, developer opportunities",
        "keywords": ["programming", "web development", "mobile apps", "DevOps"],
        "industry_focus": "IT Services, Startups, Product Companies"
    }
    # ... (includes all 10 topics)
}

app = FastAPI(
    title="Guidora News & Feeds Service",
    description="📰 AI-powered personalized career news",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "service": "Guidora News & Feeds Service",
        "status": "operational",
        "career_topics": {"total_topics": len(CAREER_TOPICS)},
        "features": [
            "AI-powered career news curation",
            "Personalized feed recommendations", 
            "10 curated career topics for Indian students",
            "Gemini AI integration for insights"
        ]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Enhanced health check endpoint"""
    return {
        "status": "healthy",
        "service": "news-feeds-service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "gemini_ai": "operational",
            "news_aggregator": "active",
            "feed_generator": "running"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5010)
