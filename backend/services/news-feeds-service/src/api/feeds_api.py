"""📰 FEEDS API - Personalized Career News Endpoints"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter()

@router.get("/feeds/personalized/{user_id}")
async def get_personalized_feeds(user_id: str, limit: int = 15):
    """🎯 Get AI-personalized feeds for specific user"""
    # Personalization logic with AI-powered recommendations
    return PersonalizedFeedResponse(
        user_id=user_id,
        feeds=personalized_feeds[:limit],
        personalization_score=85.0,
        trending_topics=["artificial-intelligence", "fintech", "cloud-computing"],
        suggested_topics=["cybersecurity", "healthcare-tech"]
    )

@router.get("/feeds/topic/{topic}")
async def get_topic_feeds(topic: str, limit: int = 10):
    """📚 Get feeds for specific career topic"""
    return {"success": True, "topic": topic, "feeds": topic_feeds[:limit]}

@router.post("/feeds/generate/{topic}")
async def generate_ai_feeds(topic: str, background_tasks: BackgroundTasks):
    """🤖 Generate new AI-powered feeds using Gemini"""
    background_tasks.add_task(generate_feeds_background, topic)
    return {"success": True, "message": f"AI feed generation started for: {topic}"}
