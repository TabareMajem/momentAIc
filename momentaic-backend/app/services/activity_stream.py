"""
Agent Activity Stream
Broadcasts agent activities in real-time for Command Center UI
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import uuid
import structlog

logger = structlog.get_logger()


class ActivityStatus(str, Enum):
    """Agent activity status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"
    PAUSED = "paused"


@dataclass
class AgentActivity:
    """Single agent activity record"""
    id: str
    agent_name: str
    task: str
    status: ActivityStatus
    progress: int = 0  # 0-100
    message: str = ""
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    startup_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent": self.agent_name,
            "task": self.task,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class AgentActivityStream:
    """
    Central hub for agent activity broadcasting.
    
    Agents call report_* methods, and the stream broadcasts to:
    - WebSocket connections (Command Center UI)
    - Activity log (database)
    """
    
    def __init__(self):
        self._activities: Dict[str, AgentActivity] = {}
        self._subscribers: List[Callable] = []
        self._startup_activities: Dict[str, List[str]] = {}  # startup_id -> activity_ids
    
    def subscribe(self, callback: Callable):
        """Subscribe to activity updates"""
        self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from activity updates"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    async def _broadcast(self, activity: AgentActivity):
        """Broadcast activity to all subscribers"""
        for subscriber in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(activity.to_dict())
                else:
                    subscriber(activity.to_dict())
            except Exception as e:
                logger.error("Failed to broadcast activity", error=str(e))
    
    async def report_start(
        self,
        agent_name: str,
        task: str,
        startup_id: str = None,
    ) -> str:
        """Report agent starting a task"""
        activity_id = str(uuid.uuid4())
        
        activity = AgentActivity(
            id=activity_id,
            agent_name=agent_name,
            task=task,
            status=ActivityStatus.RUNNING,
            progress=0,
            message="Starting...",
            startup_id=startup_id,
        )
        
        self._activities[activity_id] = activity
        
        if startup_id:
            if startup_id not in self._startup_activities:
                self._startup_activities[startup_id] = []
            self._startup_activities[startup_id].append(activity_id)
        
        logger.info(
            "🚀 Agent started",
            agent=agent_name,
            task=task,
            activity_id=activity_id
        )
        
        await self._broadcast(activity)
        return activity_id
    
    async def report_progress(
        self,
        activity_id: str,
        message: str,
        progress: int = None,
    ):
        """Report progress on a task"""
        if activity_id not in self._activities:
            return
        
        activity = self._activities[activity_id]
        activity.message = message
        if progress is not None:
            activity.progress = min(100, max(0, progress))
        
        logger.info(
            "⏳ Agent progress",
            agent=activity.agent_name,
            message=message,
            progress=activity.progress
        )
        
        await self._broadcast(activity)
    
    async def report_complete(
        self,
        activity_id: str,
        result: Dict[str, Any] = None,
    ):
        """Report task completion"""
        if activity_id not in self._activities:
            return
        
        activity = self._activities[activity_id]
        activity.status = ActivityStatus.COMPLETE
        activity.progress = 100
        activity.message = "Complete"
        activity.result = result
        activity.completed_at = datetime.utcnow()
        
        logger.info(
            "✅ Agent completed",
            agent=activity.agent_name,
            task=activity.task,
            duration_s=(activity.completed_at - activity.started_at).total_seconds()
        )
        
        await self._broadcast(activity)
    
    async def report_error(
        self,
        activity_id: str,
        error: str,
    ):
        """Report task error"""
        if activity_id not in self._activities:
            return
        
        activity = self._activities[activity_id]
        activity.status = ActivityStatus.ERROR
        activity.error = error
        activity.completed_at = datetime.utcnow()
        
        logger.error(
            "❌ Agent error",
            agent=activity.agent_name,
            task=activity.task,
            error=error
        )
        
        await self._broadcast(activity)
    
    def get_activities(self, startup_id: str = None, limit: int = 50) -> List[Dict]:
        """Get recent activities"""
        activities = list(self._activities.values())
        
        if startup_id:
            activities = [a for a in activities if a.startup_id == startup_id]
        
        # Sort by most recent first
        activities.sort(key=lambda a: a.started_at, reverse=True)
        
        return [a.to_dict() for a in activities[:limit]]
    
    def get_active(self, startup_id: str = None) -> List[Dict]:
        """Get currently running activities"""
        activities = [
            a for a in self._activities.values()
            if a.status == ActivityStatus.RUNNING
        ]
        
        if startup_id:
            activities = [a for a in activities if a.startup_id == startup_id]
        
        return [a.to_dict() for a in activities]
    
    def get_pending(self, startup_id: str = None) -> List[Dict]:
        """Get pending activities"""
        activities = [
            a for a in self._activities.values()
            if a.status == ActivityStatus.PENDING
        ]
        
        if startup_id:
            activities = [a for a in activities if a.startup_id == startup_id]
        
        return [a.to_dict() for a in activities]


# Singleton instance
activity_stream = AgentActivityStream()
