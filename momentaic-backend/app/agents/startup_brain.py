"""
Startup Brain - The Central Intelligence for Startup Success
Orchestrates all agents, tracks progress, generates action plans
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import uuid4
import structlog
import asyncio

from app.agents.success_protocol import success_protocol, StartupPhase, PhaseAction
from app.services.goal_tracker import goal_tracker, Goal, GoalPriority, GoalStatus

logger = structlog.get_logger()


@dataclass
class AgentTask:
    """A task to be executed by an agent chain"""
    id: str
    action_id: str
    name: str
    description: str
    agent_chain: List[str]
    priority: int
    estimated_hours: float
    requires_approval: bool = False
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_id": self.action_id,
            "name": self.name,
            "description": self.description,
            "agent_chain": self.agent_chain,
            "priority": self.priority,
            "estimated_hours": self.estimated_hours,
            "requires_approval": self.requires_approval,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error
        }


@dataclass
class ActionPlan:
    """Daily action plan for a startup"""
    id: str
    startup_id: str
    date: str
    phase: str
    tasks: List[AgentTask]
    total_estimated_hours: float
    automated_count: int
    approval_required_count: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    completion_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            "date": self.date,
            "phase": self.phase,
            "tasks": [t.to_dict() for t in self.tasks],
            "total_estimated_hours": self.total_estimated_hours,
            "automated_count": self.automated_count,
            "approval_required_count": self.approval_required_count,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "completion_rate": self.completion_rate
        }


@dataclass 
class StartupState:
    """Current state of a startup"""
    startup_id: str
    name: str
    description: str
    current_phase: StartupPhase
    phase_progress: Dict[str, Any]
    active_goals: List[Dict[str, Any]]
    overdue_goals: List[Dict[str, Any]]
    recent_milestones: List[Dict[str, Any]]
    metrics: Dict[str, float]
    health_score: float
    next_actions: List[Dict[str, Any]]
    blockers: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "startup_id": self.startup_id,
            "name": self.name,
            "description": self.description,
            "current_phase": self.current_phase.value,
            "phase_progress": self.phase_progress,
            "active_goals": self.active_goals,
            "overdue_goals": self.overdue_goals,
            "recent_milestones": self.recent_milestones,
            "metrics": self.metrics,
            "health_score": self.health_score,
            "next_actions": self.next_actions,
            "blockers": self.blockers
        }


class StartupBrain:
    """
    The Central Nervous System for Startup Success
    
    Responsibilities:
    1. Track startup phase and progress
    2. Generate daily action plans
    3. Orchestrate agent execution
    4. Monitor and report on progress
    5. Identify blockers and suggest solutions
    """
    
    def __init__(self):
        self._action_plans: Dict[str, List[ActionPlan]] = {}  # startup_id -> [plans]
        self._completed_actions: Dict[str, set] = {}  # startup_id -> {action_ids}
        self._startup_contexts: Dict[str, Dict[str, Any]] = {}  # startup_id -> context
        logger.info("Startup Brain initialized")
    
    # ==================
    # State Analysis
    # ==================
    
    async def analyze_current_state(
        self,
        startup_id: str,
        startup_context: Optional[Dict[str, Any]] = None
    ) -> StartupState:
        """
        Pull all data, assess phase, identify blockers
        """
        # Cache context
        if startup_context:
            self._startup_contexts[startup_id] = startup_context
        context = self._startup_contexts.get(startup_id, {})
        
        # Get metrics from goal tracker
        metrics = await goal_tracker.get_metrics(startup_id)
        
        # Detect current phase based on metrics
        current_phase = success_protocol.detect_phase(metrics)
        
        # Get phase progress
        phase_progress = success_protocol.get_phase_progress(current_phase, metrics)
        
        # Get goals
        progress_summary = await goal_tracker.get_progress_summary(startup_id)
        
        # Get completed actions
        completed = list(self._completed_actions.get(startup_id, set()))
        
        # Get next actions from protocol
        next_actions = success_protocol.get_required_actions(current_phase, completed)
        
        # Identify blockers
        blockers = []
        if progress_summary['overdue_goals']:
            blockers.append(f"{len(progress_summary['overdue_goals'])} overdue goals")
        if phase_progress.get('overall_progress', 0) < 20:
            blockers.append("Low phase progress - need to execute more actions")
        
        state = StartupState(
            startup_id=startup_id,
            name=context.get('name', 'Unnamed Startup'),
            description=context.get('description', ''),
            current_phase=current_phase,
            phase_progress=phase_progress,
            active_goals=progress_summary['active_goals'],
            overdue_goals=progress_summary['overdue_goals'],
            recent_milestones=progress_summary['recent_milestones'],
            metrics=metrics,
            health_score=progress_summary['health_score'],
            next_actions=[a.to_dict() for a in next_actions[:5]],
            blockers=blockers
        )
        
        logger.info(
            "State analyzed",
            startup_id=startup_id,
            phase=current_phase.value,
            health_score=state.health_score
        )
        
        return state
    
    # ==================
    # Action Plan Generation
    # ==================
    
    async def generate_daily_action_plan(
        self,
        startup_id: str,
        max_hours: float = 8.0,
        include_non_automated: bool = False
    ) -> ActionPlan:
        """
        Generate today's action plan based on current state and protocol
        """
        # Analyze current state
        state = await self.analyze_current_state(startup_id)
        
        # Get completed actions
        completed = list(self._completed_actions.get(startup_id, set()))
        
        # Get required actions from protocol
        if include_non_automated:
            actions = success_protocol.get_required_actions(state.current_phase, completed)
        else:
            actions = success_protocol.get_automated_actions(state.current_phase, completed)
        
        # Convert to tasks and fit within time budget
        tasks = []
        total_hours = 0
        automated_count = 0
        approval_count = 0
        
        for action in actions:
            if total_hours + action.estimated_hours <= max_hours:
                task = AgentTask(
                    id=str(uuid4()),
                    action_id=action.id,
                    name=action.name,
                    description=action.description,
                    agent_chain=action.agent_chain,
                    priority=action.priority,
                    estimated_hours=action.estimated_hours,
                    requires_approval=not action.automated
                )
                tasks.append(task)
                total_hours += action.estimated_hours
                
                if action.automated:
                    automated_count += 1
                else:
                    approval_count += 1
        
        plan = ActionPlan(
            id=str(uuid4()),
            startup_id=startup_id,
            date=datetime.utcnow().strftime("%Y-%m-%d"),
            phase=state.current_phase.value,
            tasks=tasks,
            total_estimated_hours=total_hours,
            automated_count=automated_count,
            approval_required_count=approval_count
        )
        
        # Store plan
        if startup_id not in self._action_plans:
            self._action_plans[startup_id] = []
        self._action_plans[startup_id].append(plan)
        
        logger.info(
            "Action plan generated",
            startup_id=startup_id,
            tasks=len(tasks),
            estimated_hours=total_hours
        )
        
        return plan
    
    # ==================
    # Action Execution
    # ==================
    
    async def execute_action_plan(
        self,
        plan: ActionPlan,
        startup_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute all tasks in the action plan
        Returns execution report
        """
        from app.agents.chain_executor import chain_executor
        
        plan.executed_at = datetime.utcnow()
        results = []
        completed = 0
        failed = 0
        
        for task in plan.tasks:
            if task.requires_approval:
                # Skip tasks needing approval - they go to a queue
                task.status = "pending_approval"
                continue
            
            try:
                task.status = "running"
                task.started_at = datetime.utcnow()
                
                logger.info(
                    "Executing task",
                    task_id=task.id,
                    name=task.name,
                    agents=task.agent_chain
                )
                
                # Execute through chain executor
                result = await chain_executor.execute_chain(
                    agent_chain=task.agent_chain,
                    initial_context={
                        **startup_context,
                        "task_name": task.name,
                        "task_description": task.description
                    }
                )
                
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                task.result = result
                completed += 1
                
                # Mark action as completed
                if plan.startup_id not in self._completed_actions:
                    self._completed_actions[plan.startup_id] = set()
                self._completed_actions[plan.startup_id].add(task.action_id)
                
            except Exception as e:
                task.status = "failed"
                task.error = str(e)
                failed += 1
                logger.error("Task failed", task_id=task.id, error=str(e))
            
            results.append(task.to_dict())
        
        # Calculate completion rate
        total_executed = completed + failed
        plan.completion_rate = (completed / max(total_executed, 1)) * 100
        
        report = {
            "plan_id": plan.id,
            "startup_id": plan.startup_id,
            "executed_at": plan.executed_at.isoformat(),
            "tasks_completed": completed,
            "tasks_failed": failed,
            "tasks_pending_approval": len([t for t in plan.tasks if t.status == "pending_approval"]),
            "completion_rate": plan.completion_rate,
            "results": results
        }
        
        logger.info(
            "Action plan executed",
            plan_id=plan.id,
            completed=completed,
            failed=failed,
            completion_rate=plan.completion_rate
        )
        
        return report
    
    async def execute_single_action(
        self,
        startup_id: str,
        action_id: str,
        startup_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single specific action"""
        from app.agents.chain_executor import chain_executor
        
        state = await self.analyze_current_state(startup_id, startup_context)
        agent_chain = success_protocol.get_agent_chain(action_id, state.current_phase)
        
        if not agent_chain:
            return {"success": False, "error": f"Unknown action: {action_id}"}
        
        try:
            result = await chain_executor.execute_chain(
                agent_chain=agent_chain,
                initial_context={
                    **startup_context,
                    "action_id": action_id
                }
            )
            
            # Mark as completed
            if startup_id not in self._completed_actions:
                self._completed_actions[startup_id] = set()
            self._completed_actions[startup_id].add(action_id)
            
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error("Action execution failed", action_id=action_id, error=str(e))
            return {"success": False, "error": str(e)}
    
    # ==================
    # Progress Evaluation
    # ==================
    
    async def evaluate_progress(self, startup_id: str) -> Dict[str, Any]:
        """
        Comprehensive progress evaluation
        """
        state = await self.analyze_current_state(startup_id)
        
        # Calculate progress score (0-100)
        phase_weight = 0.4
        goals_weight = 0.3
        actions_weight = 0.3
        
        phase_score = state.phase_progress.get('overall_progress', 0) * phase_weight
        goals_score = state.health_score * goals_weight
        
        # Action completion score
        completed_count = len(self._completed_actions.get(startup_id, set()))
        phase_actions = success_protocol.get_phase(state.current_phase)
        total_actions = len(phase_actions.required_actions) if phase_actions else 1
        actions_score = (completed_count / max(total_actions, 1)) * 100 * actions_weight
        
        progress_score = phase_score + goals_score + actions_score
        
        # Generate recommendations
        recommendations = []
        if state.overdue_goals:
            recommendations.append("Focus on overdue goals to improve momentum")
        if state.phase_progress.get('overall_progress', 0) < 50:
            recommendations.append(f"Continue executing {state.current_phase.value} phase actions")
        if completed_count < total_actions:
            next_action = success_protocol.get_next_action(
                state.current_phase, 
                list(self._completed_actions.get(startup_id, set()))
            )
            if next_action:
                recommendations.append(f"Next priority: {next_action.name}")
        
        return {
            "startup_id": startup_id,
            "current_phase": state.current_phase.value,
            "progress_score": progress_score,
            "phase_progress": state.phase_progress.get('overall_progress', 0),
            "health_score": state.health_score,
            "actions_completed": completed_count,
            "actions_total": total_actions,
            "ready_to_advance": state.phase_progress.get('ready_to_advance', False),
            "recommendations": recommendations,
            "blockers": state.blockers
        }
    
    # ==================
    # Morning Briefing
    # ==================
    
    async def generate_morning_briefing(
        self,
        startup_id: str,
        startup_context: Dict[str, Any]
    ) -> str:
        """
        Generate a morning briefing for the founder
        """
        state = await self.analyze_current_state(startup_id, startup_context)
        plan = await self.generate_daily_action_plan(startup_id)
        
        lines = [
            f"☀️ **Good Morning, {startup_context.get('founder_name', 'Founder')}!**",
            f"",
            f"**{state.name}** | Phase: **{state.current_phase.value.title()}**",
            f"Health Score: **{state.health_score:.0f}/100**",
            f"",
        ]
        
        # Phase progress
        progress = state.phase_progress.get('overall_progress', 0)
        lines.append(f"📈 **Phase Progress:** {progress:.0f}%")
        if state.phase_progress.get('ready_to_advance'):
            lines.append("🎉 Ready to advance to next phase!")
        lines.append("")
        
        # Today's plan
        lines.append(f"📋 **Today's Action Plan** ({plan.total_estimated_hours:.1f}h estimated)")
        for task in plan.tasks[:5]:
            icon = "🤖" if not task.requires_approval else "👤"
            lines.append(f"  {icon} {task.name}")
        if len(plan.tasks) > 5:
            lines.append(f"  ... and {len(plan.tasks) - 5} more")
        lines.append("")
        
        # Alerts
        if state.blockers:
            lines.append("⚠️ **Attention Needed:**")
            for blocker in state.blockers:
                lines.append(f"  - {blocker}")
            lines.append("")
        
        # Recent wins
        if state.recent_milestones:
            lines.append("🏆 **Recent Wins:**")
            for m in state.recent_milestones[:3]:
                lines.append(f"  - {m['name']}")
        
        return "\n".join(lines)


# Singleton instance
startup_brain = StartupBrain()
