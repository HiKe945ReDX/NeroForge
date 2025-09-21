
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum

from ..services.analytics import PersonalizationEngine, generate_user_analytics
from ..core.database import get_database
from ..core.config import settings

logger = logging.getLogger(__name__)

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BackgroundJob:
    """Background job definition"""
    id: str
    name: str
    function: Callable
    args: tuple
    kwargs: dict
    priority: str
    scheduled_at: datetime
    max_retries: int = 3
    retry_count: int = 0
    status: JobStatus = JobStatus.PENDING

class AnalyticsJobScheduler:
    """
    ⏰ Advanced Background Job Scheduler
    Processes Instagram-style analytics in the background
    """
    
    def __init__(self):
        self.jobs: Dict[str, BackgroundJob] = {}
        self.running = False
        self.worker_tasks: List[asyncio.Task] = []
        self.max_workers = 3
        
    async def start(self):
        """Start the job scheduler"""
        
        if self.running:
            return
            
        self.running = True
        logger.info("🚀 Analytics Job Scheduler starting...")
        
        # Start worker tasks
        for i in range(self.max_workers):
            task = asyncio.create_task(self._worker(f"worker-{i}"))
            self.worker_tasks.append(task)
            
        logger.info(f"✅ Job scheduler started with {self.max_workers} workers")

    async def schedule_job(
        self, 
        name: str, 
        function: Callable, 
        args: tuple = (), 
        kwargs: dict = None,
        priority: str = "medium",
        delay_seconds: int = 0,
        max_retries: int = 3
    ) -> str:
        """Schedule a background job"""
        
        import uuid
        
        job_id = str(uuid.uuid4())
        scheduled_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        
        job = BackgroundJob(
            id=job_id,
            name=name,
            function=function,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            scheduled_at=scheduled_at,
            max_retries=max_retries
        )
        
        self.jobs[job_id] = job
        
        logger.info(f"📝 Job scheduled: {name} (ID: {job_id[:8]}) - Priority: {priority}")
        
        return job_id

    async def _generate_hourly_insights(self):
        """Generate personalized insights for active users"""
        
        db = await get_database()
        engine = PersonalizationEngine(db)
        
        # Get users active in last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        active_users = await db.user_activities.distinct(
            "user_id",
            {"timestamp": {"$gte": one_hour_ago}}
        )
        
        insights_generated = 0
        
        for user_id in active_users:
            try:
                insights = await engine.generate_personalized_insights(user_id)
                insights_generated += len(insights)
            except Exception as e:
                logger.error(f"Insight generation failed for user {user_id}: {e}")
                
        logger.info(f"✅ Generated {insights_generated} insights for {len(active_users)} users")

# Global scheduler instance
scheduler = AnalyticsJobScheduler()

# Scheduler management functions
async def start_background_scheduler():
    """Start the background job scheduler"""
    await scheduler.start()

async def schedule_analytics_job(name: str, function: Callable, **kwargs) -> str:
    """Schedule an analytics background job"""
    return await scheduler.schedule_job(name, function, **kwargs)
