"""
⚡ DATABASE PERFORMANCE OPTIMIZATION - MongoDB Indices
Instagram-scale database performance with optimized indices
"""
from typing import List, Dict, Any
from datetime import datetime
import asyncio

from ..core.database import get_database
from ..core.config import settings

class DatabaseOptimizer:
    """
    ⚡ Database Performance Optimizer
    Creates and manages MongoDB indices for Instagram-scale performance
    """
    
    def __init__(self, db):
        self.db = db
        
    async def create_all_indices(self):
        """Create all performance-critical indices"""
        
        print("🚀 Creating database indices for Instagram-scale performance...")
        
        # User Activities Collection Indices
        await self.create_user_activities_indices()
        
        # User Sessions Collection Indices
        await self.create_user_sessions_indices()
        
        # Behavior Patterns Collection Indices
        await self.create_behavior_patterns_indices()
        
        # Personalized Insights Collection Indices
        await self.create_personalized_insights_indices()
        
        # Activity Summaries Collection Indices
        await self.create_activity_summaries_indices()
        
        # Users Collection Indices
        await self.create_users_indices()
        
        print("✅ All database indices created successfully!")

    async def create_user_activities_indices(self):
        """Create indices for user_activities collection"""
        
        print("📊 Creating user_activities indices...")
        
        indices = [
            # Primary query patterns
            [("user_id", 1), ("timestamp", -1)],  # User timeline queries
            [("session_id", 1), ("timestamp", 1)],  # Session-based queries
            [("user_id", 1), ("activity_type", 1), ("timestamp", -1)],  # Activity type filtering
            [("user_id", 1), ("feature_name", 1), ("timestamp", -1)],  # Feature usage analysis
            
            # Analytics queries
            [("timestamp", -1)],  # Time-based aggregations
            [("user_id", 1), ("timestamp", -1), ("duration_seconds", 1)],  # Performance analytics
            [("activity_type", 1), ("timestamp", -1)],  # Global activity analysis
            [("feature_name", 1), ("timestamp", -1)],  # Feature popularity analysis
        ]
        
        for index_fields in indices:
            await self.db.user_activities.create_index(index_fields)
            
        # Text index for search functionality
        await self.db.user_activities.create_index([
            ("page_title", "text"),
            ("feature_name", "text"),
            ("metadata", "text")
        ])
        
        print("✅ user_activities indices created")

# Optimization functions
async def initialize_database_optimization():
    """Initialize database optimization on startup"""
    
    try:
        db = await get_database()
        optimizer = DatabaseOptimizer(db)
        
        # Create all indices
        await optimizer.create_all_indices()
        
        print("🚀 Database optimization completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database optimization failed: {e}")
        return False
