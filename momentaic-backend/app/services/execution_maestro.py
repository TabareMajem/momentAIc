
from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime
import uuid
from pydantic import BaseModel
from enum import Enum

from app.models.conversation import AgentType
from app.agents.swarm_router import swarm_router

logger = structlog.get_logger()

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ExecutionTask(BaseModel):
    id: str
    agent_type: str
    action: str
    params: Dict[str, Any]
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.now()

class ExecutionPlan(BaseModel):
    id: str
    startup_id: str
    source_context: Dict[str, Any]
    tasks: List[ExecutionTask]
    created_at: datetime = datetime.now()

class ExecutionMaestro:
    """
    The 'God Mode' Executor.
    Orchestrates the transition from Strategy -> Action.
    """
    
    async def generate_plan_from_strategy(self, startup_id: str, strategy: Dict[str, Any], context: Dict[str, Any]) -> ExecutionPlan:
        """
        Converts a high-level Strategy (from GrowthHacker) into executable Tasks.
        """
        tasks = []
        
        # 1. Sales Task (Hunt Leads)
        if "target_audience" in strategy:
            tasks.append(ExecutionTask(
                id=str(uuid.uuid4()),
                agent_type=AgentType.SALES.value,
                action="hunt_leads",
                params={
                    "target_audience": strategy["target_audience"],
                    "count": 10,  # Default batch
                    "platform": "linkedin" # Yokaizen integration point
                },
                priority=10
            ))
            
        # 2. Marketing Task (Viral Post)
        if "viral_post_hook" in strategy:
            tasks.append(ExecutionTask(
                id=str(uuid.uuid4()),
                agent_type=AgentType.MARKETING.value,
                action="generate_content",
                params={
                    "topic": strategy["viral_post_hook"],
                    "platform": "twitter",
                    "goal": "viral_awareness"
                },
                priority=8
            ))
            
        # 3. Development Task (GitHub Import / Product Polish)
        if context.get("source") == "github":
            tasks.append(ExecutionTask(
                id=str(uuid.uuid4()),
                agent_type="developer", # We implement this agent later if needed, or use OnboardingCoach
                action="analyze_codebase", 
                params={
                    "repo_url": context.get("import_details", {}).get("metadata", {}).get("url")
                },
                priority=5
            ))
            
        return ExecutionPlan(
            id=str(uuid.uuid4()),
            startup_id=startup_id,
            source_context=context,
            tasks=tasks
        )

    async def execute_plan(self, plan: ExecutionPlan):
        """
        Dispatches tasks to the Swarm.
        Real execution happens here.
        """
        logger.info("Maestro: Executing Plan", plan_id=plan.id, task_count=len(plan.tasks))
        
        results = {}
        
        for task in plan.tasks:
            try:
                logger.info("Maestro: Dispatching Task", task_id=task.id, agent=task.agent_type, action=task.action)
                task.status = TaskStatus.IN_PROGRESS
                
                # [INTEGRATION] Yokaizen / AgentForge Logic
                # For Phase 5 MVP, we delegate to SwarmRouter or Mock
                result = await self._dispatch_to_swarm(task, plan.startup_id)
                
                task.result = result
                task.status = TaskStatus.COMPLETED
                results[task.id] = result
                
            except Exception as e:
                logger.error("Task Execution Failed", task_id=task.id, error=str(e))
                task.status = TaskStatus.FAILED
                task.result = {"error": str(e)}
                
        return results

    async def _dispatch_to_swarm(self, task: ExecutionTask, startup_id: str) -> Dict[str, Any]:
        """
        Route to specific Agent capability.
        """
        if task.agent_type == AgentType.SALES.value:
            # Call Sales Agent
            # For now, we simulate the Yokaizen integration
            return {
                "status": "success", 
                "leads_found": 10, 
                "platform": "yokaizen.com (simulated)",
                "note": "Connected to Yokaizen Lead Database"
            }
            
        elif task.agent_type == AgentType.MARKETING.value:
            # Call Marketing Agent / Social Scheduler
            from app.services.social_scheduler import social_scheduler
            from datetime import datetime
            
            content = f"Draft post about {task.params.get('topic')} #MomentAIc"
            # In a real scenario, we'd use the MarketingAgent to write the content first
            # But the user wants Execution *Now*.
            
            # 1. Generate Content (Simulated for speed, or call LLM)
            # content = await marketing_agent.generate_viral_thread(task.params.get('topic'))[0]
            
            # 2. Schedule
            post = await social_scheduler.schedule_post(
                startup_id=startup_id,
                content=content,
                platforms=["twitter", "linkedin"],
                scheduled_at=datetime.utcnow()
            )
            
            return {
                "status": "scheduled",
                "post_id": str(post.id),
                "scheduled_at": str(post.scheduled_at),
                "platform": "Native Scheduler (Buffer Killer)"
            }
            
        return {"status": "skipped", "reason": "No agent handler"}

execution_maestro = ExecutionMaestro()
