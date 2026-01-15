"""
Goal Tracker - Persistent Goal and Progress Tracking
Tracks startup goals, milestones, and progress across the journey
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4
import structlog

logger = structlog.get_logger()


class GoalStatus(str, Enum):
    """Status of a goal"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class GoalPriority(str, Enum):
    """Goal priority levels"""
    CRITICAL = "critical"  # Must do today
    HIGH = "high"          # This week
    MEDIUM = "medium"      # This month
    LOW = "low"            # Someday


@dataclass
class Goal:
    """A startup goal"""
    id: str
    name: str
    description: str
    target_metric: str
    target_value: float
    current_value: float = 0
    status: GoalStatus = GoalStatus.PENDING
    priority: GoalPriority = GoalPriority.MEDIUM
    phase: str = "idea"
    assigned_agent_chain: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    notes: List[str] = field(default_factory=list)
    
    @property
    def progress(self) -> float:
        """Calculate progress percentage"""
        if self.target_value == 0:
            return 100 if self.current_value > 0 else 0
        return min(100, (self.current_value / self.target_value) * 100)
    
    @property
    def is_complete(self) -> bool:
        return self.current_value >= self.target_value or self.status == GoalStatus.COMPLETED
    
    @property
    def is_overdue(self) -> bool:
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline and not self.is_complete
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_metric": self.target_metric,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "progress": self.progress,
            "status": self.status.value,
            "priority": self.priority.value,
            "phase": self.phase,
            "assigned_agent_chain": self.assigned_agent_chain,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_complete": self.is_complete,
            "is_overdue": self.is_overdue,
            "notes": self.notes
        }


@dataclass
class Milestone:
    """A significant achievement or milestone"""
    id: str
    name: str
    description: str
    achieved_at: datetime
    phase: str
    related_goal_id: Optional[str] = None
    celebration_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "achieved_at": self.achieved_at.isoformat(),
            "phase": self.phase,
            "related_goal_id": self.related_goal_id,
            "celebration_message": self.celebration_message
        }


@dataclass
class DailyProgress:
    """Daily progress snapshot"""
    date: str
    phase: str
    goals_completed: int
    goals_in_progress: int
    actions_executed: int
    key_achievements: List[str]
    blockers: List[str]
    agent_activities: Dict[str, int]  # agent_id -> action_count


class GoalTracker:
    """
    Persistent Goal and Progress Tracking
    
    Tracks:
    - Active goals with progress
    - Completed milestones
    - Daily/weekly summaries
    - Agent activity history
    """
    
    def __init__(self):
        # In-memory storage (in production, use database)
        self._goals: Dict[str, Dict[str, Goal]] = {}  # startup_id -> {goal_id -> Goal}
        self._milestones: Dict[str, List[Milestone]] = {}  # startup_id -> [Milestone]
        self._daily_progress: Dict[str, List[DailyProgress]] = {}  # startup_id -> [DailyProgress]
        self._metrics: Dict[str, Dict[str, float]] = {}  # startup_id -> {metric_name -> value}
        logger.info("Goal Tracker initialized")
    
    # ==================
    # Goal Management
    # ==================
    
    async def create_goal(
        self,
        startup_id: str,
        name: str,
        description: str,
        target_metric: str,
        target_value: float,
        priority: GoalPriority = GoalPriority.MEDIUM,
        phase: str = "idea",
        agent_chain: List[str] = None,
        deadline: Optional[datetime] = None
    ) -> Goal:
        """Create a new goal"""
        if startup_id not in self._goals:
            self._goals[startup_id] = {}
        
        goal = Goal(
            id=str(uuid4()),
            name=name,
            description=description,
            target_metric=target_metric,
            target_value=target_value,
            priority=priority,
            phase=phase,
            assigned_agent_chain=agent_chain or [],
            deadline=deadline
        )
        
        self._goals[startup_id][goal.id] = goal
        logger.info("Goal created", startup_id=startup_id, goal_id=goal.id, name=name)
        return goal
    
    async def update_goal_progress(
        self,
        startup_id: str,
        goal_id: str,
        current_value: float,
        note: Optional[str] = None
    ) -> Optional[Goal]:
        """Update goal progress"""
        if startup_id not in self._goals or goal_id not in self._goals[startup_id]:
            return None
        
        goal = self._goals[startup_id][goal_id]
        goal.current_value = current_value
        goal.updated_at = datetime.utcnow()
        
        if note:
            goal.notes.append(f"[{datetime.utcnow().isoformat()}] {note}")
        
        # Check if completed
        if goal.is_complete and goal.status != GoalStatus.COMPLETED:
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.utcnow()
            logger.info("Goal completed!", startup_id=startup_id, goal_id=goal_id, name=goal.name)
            
            # Auto-create milestone
            await self.record_milestone(
                startup_id=startup_id,
                name=f"Completed: {goal.name}",
                description=f"Achieved {goal.target_value} {goal.target_metric}",
                phase=goal.phase,
                related_goal_id=goal_id
            )
        
        return goal
    
    async def set_goal_status(
        self,
        startup_id: str,
        goal_id: str,
        status: GoalStatus
    ) -> Optional[Goal]:
        """Update goal status"""
        if startup_id not in self._goals or goal_id not in self._goals[startup_id]:
            return None
        
        goal = self._goals[startup_id][goal_id]
        goal.status = status
        goal.updated_at = datetime.utcnow()
        
        if status == GoalStatus.COMPLETED:
            goal.completed_at = datetime.utcnow()
        
        return goal
    
    async def get_goal(self, startup_id: str, goal_id: str) -> Optional[Goal]:
        """Get a specific goal"""
        if startup_id not in self._goals:
            return None
        return self._goals[startup_id].get(goal_id)
    
    async def get_active_goals(
        self, 
        startup_id: str,
        phase: Optional[str] = None
    ) -> List[Goal]:
        """Get all active (non-completed) goals"""
        if startup_id not in self._goals:
            return []
        
        goals = [
            g for g in self._goals[startup_id].values()
            if g.status not in [GoalStatus.COMPLETED, GoalStatus.CANCELLED]
        ]
        
        if phase:
            goals = [g for g in goals if g.phase == phase]
        
        # Sort by priority
        priority_order = {GoalPriority.CRITICAL: 0, GoalPriority.HIGH: 1, GoalPriority.MEDIUM: 2, GoalPriority.LOW: 3}
        return sorted(goals, key=lambda g: priority_order.get(g.priority, 99))
    
    async def get_overdue_goals(self, startup_id: str) -> List[Goal]:
        """Get all overdue goals"""
        active = await self.get_active_goals(startup_id)
        return [g for g in active if g.is_overdue]
    
    # ==================
    # Milestone Tracking
    # ==================
    
    async def record_milestone(
        self,
        startup_id: str,
        name: str,
        description: str,
        phase: str,
        related_goal_id: Optional[str] = None
    ) -> Milestone:
        """Record a new milestone"""
        if startup_id not in self._milestones:
            self._milestones[startup_id] = []
        
        # Generate celebration message
        celebrations = [
            "🎉 Incredible achievement!",
            "🚀 You're on fire!",
            "⭐ Another milestone crushed!",
            "💪 The momentum is building!",
            "🏆 Champions move forward!"
        ]
        import random
        celebration = random.choice(celebrations)
        
        milestone = Milestone(
            id=str(uuid4()),
            name=name,
            description=description,
            achieved_at=datetime.utcnow(),
            phase=phase,
            related_goal_id=related_goal_id,
            celebration_message=celebration
        )
        
        self._milestones[startup_id].append(milestone)
        logger.info("Milestone recorded", startup_id=startup_id, name=name, celebration=celebration)
        return milestone
    
    async def get_milestones(
        self, 
        startup_id: str,
        limit: int = 20
    ) -> List[Milestone]:
        """Get recent milestones"""
        if startup_id not in self._milestones:
            return []
        
        milestones = sorted(
            self._milestones[startup_id],
            key=lambda m: m.achieved_at,
            reverse=True
        )
        return milestones[:limit]
    
    # ==================
    # Metrics Tracking
    # ==================
    
    async def update_metric(
        self,
        startup_id: str,
        metric_name: str,
        value: float
    ) -> None:
        """Update a startup metric"""
        if startup_id not in self._metrics:
            self._metrics[startup_id] = {}
        
        self._metrics[startup_id][metric_name] = value
        logger.debug("Metric updated", startup_id=startup_id, metric=metric_name, value=value)
        
        # Auto-update goals tracking this metric
        if startup_id in self._goals:
            for goal in self._goals[startup_id].values():
                if goal.target_metric == metric_name:
                    await self.update_goal_progress(startup_id, goal.id, value)
    
    async def get_metrics(self, startup_id: str) -> Dict[str, float]:
        """Get all metrics for a startup"""
        return self._metrics.get(startup_id, {})
    
    async def get_metric(self, startup_id: str, metric_name: str) -> Optional[float]:
        """Get a specific metric"""
        if startup_id not in self._metrics:
            return None
        return self._metrics[startup_id].get(metric_name)
    
    # ==================
    # Progress Summary
    # ==================
    
    async def get_progress_summary(self, startup_id: str) -> Dict[str, Any]:
        """Get comprehensive progress summary"""
        active_goals = await self.get_active_goals(startup_id)
        overdue_goals = await self.get_overdue_goals(startup_id)
        milestones = await self.get_milestones(startup_id, limit=5)
        metrics = await self.get_metrics(startup_id)
        
        # Calculate overall health score
        total_goals = len(active_goals) + len([g for g in self._goals.get(startup_id, {}).values() if g.status == GoalStatus.COMPLETED])
        completed_goals = len([g for g in self._goals.get(startup_id, {}).values() if g.status == GoalStatus.COMPLETED])
        
        completion_rate = (completed_goals / max(total_goals, 1)) * 100
        overdue_penalty = len(overdue_goals) * 10
        health_score = max(0, min(100, completion_rate - overdue_penalty))
        
        return {
            "startup_id": startup_id,
            "health_score": health_score,
            "active_goals": [g.to_dict() for g in active_goals],
            "overdue_goals": [g.to_dict() for g in overdue_goals],
            "recent_milestones": [m.to_dict() for m in milestones],
            "metrics": metrics,
            "stats": {
                "total_goals": total_goals,
                "completed_goals": completed_goals,
                "active_goals": len(active_goals),
                "overdue_goals": len(overdue_goals),
                "completion_rate": completion_rate,
                "milestone_count": len(self._milestones.get(startup_id, []))
            }
        }
    
    async def generate_daily_summary(self, startup_id: str) -> str:
        """Generate a human-readable daily summary"""
        summary = await self.get_progress_summary(startup_id)
        
        lines = [
            f"📊 **Daily Progress Report**",
            f"",
            f"**Health Score:** {summary['health_score']:.0f}/100",
            f"**Goals:** {summary['stats']['active_goals']} active, {summary['stats']['completed_goals']} completed",
            f""
        ]
        
        if summary['overdue_goals']:
            lines.append("⚠️ **Overdue Goals:**")
            for g in summary['overdue_goals'][:3]:
                lines.append(f"  - {g['name']} ({g['progress']:.0f}%)")
            lines.append("")
        
        if summary['recent_milestones']:
            lines.append("🎉 **Recent Wins:**")
            for m in summary['recent_milestones'][:3]:
                lines.append(f"  - {m['name']}")
            lines.append("")
        
        # Top priorities
        active = [g for g in summary['active_goals'] if g['priority'] in ['critical', 'high']]
        if active:
            lines.append("🎯 **Focus Today:**")
            for g in active[:3]:
                lines.append(f"  - {g['name']} ({g['progress']:.0f}%)")
        
        return "\n".join(lines)


# Singleton instance
goal_tracker = GoalTracker()
