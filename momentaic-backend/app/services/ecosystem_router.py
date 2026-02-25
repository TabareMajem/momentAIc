"""
Ecosystem Router - Unified AI Platform Integration
Routes tasks to AgentForge, Yokaizen, or local MomentAIc agents
"""

from typing import Dict, Any, Optional
from enum import Enum
import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class Platform(str, Enum):
    """Available AI platforms in the ecosystem"""
    MOMENTAIC = "momentaic"       # Local agents (CFO, Legal, Recruiter)
    AGENTFORGE = "agentforge"     # Complex multi-agent workflows
    YOKAIZEN = "yokaizen"         # Sales, Marketing, Ops automation


class TaskCategory(str, Enum):
    """Task categories that determine routing"""
    SALES = "sales"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    FINANCE = "finance"
    LEGAL = "legal"
    RECRUITING = "recruiting"
    RESEARCH = "research"
    WORKFLOW = "workflow"
    CONTENT = "content"


# Routing rules: which platform handles which categories
ROUTING_MAP: Dict[TaskCategory, Platform] = {
    # Yokaizen handles Sales, Marketing, Ops
    TaskCategory.SALES: Platform.YOKAIZEN,
    TaskCategory.MARKETING: Platform.YOKAIZEN,
    TaskCategory.OPERATIONS: Platform.YOKAIZEN,
    
    # MomentAIc handles startup-specific deliverables
    TaskCategory.FINANCE: Platform.MOMENTAIC,
    TaskCategory.LEGAL: Platform.MOMENTAIC,
    TaskCategory.RECRUITING: Platform.MOMENTAIC,
    TaskCategory.CONTENT: Platform.MOMENTAIC,
    
    # AgentForge handles complex research and workflows
    TaskCategory.RESEARCH: Platform.AGENTFORGE,
    TaskCategory.WORKFLOW: Platform.AGENTFORGE,
}


class EcosystemRouter:
    """
    Routes tasks to the appropriate AI platform in the ecosystem.
    
    Enables seamless integration between:
    - MomentAIc (startup deliverables, Vault)
    - AgentForge (complex multi-agent orchestration)
    - Yokaizen (Sales/Marketing/Ops swarms)
    """
    
    def __init__(self):
        pass
    
    def determine_platform(self, category: TaskCategory) -> Platform:
        """Determine which platform should handle a task"""
        return ROUTING_MAP.get(category, Platform.MOMENTAIC)
    
    async def route(
        self,
        task: str,
        category: TaskCategory,
        context: Dict[str, Any] = None,
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Route a task to the appropriate platform.
        
        Args:
            task: The task description
            category: Task category for routing
            context: Additional context (startup info, etc.)
            user_id: User ID for authentication
            
        Returns:
            Result from the selected platform
        """
        platform = self.determine_platform(category)
        
        logger.info(
            "Routing task",
            category=category.value,
            platform=platform.value,
            task_preview=task[:100]
        )
        
        if platform == Platform.MOMENTAIC:
            return await self._route_to_momentaic(task, category, context)
        elif platform == Platform.AGENTFORGE:
            return await self._route_to_agentforge(task, context, user_id)
        elif platform == Platform.YOKAIZEN:
            return await self._route_to_yokaizen(task, category, context, user_id)
        else:
            return {"error": f"Unknown platform: {platform}"}
    
    async def _route_to_momentaic(
        self,
        task: str,
        category: TaskCategory,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Route to local MomentAIc agents"""
        from app.agents.chain_executor import chain_executor
        
        initial_context = {
            "message": task,
            **(context or {}),
        }
        
        # [KILL SHOT 3] Autonomous Squad Composability (DAGs)
        if context and "dag_config" in context:
            logger.info("Executing composite Agent DAG", dag_nodes=list(context["dag_config"].keys()))
            result = await chain_executor.execute_dag(
                dag=context["dag_config"],
                initial_context=initial_context,
                stop_on_error=False,
            )
        else:
            # Legacy simple tracking
            category_chains = {
                TaskCategory.FINANCE: ["finance_cfo"],
                TaskCategory.LEGAL: ["legal_counsel"],
                TaskCategory.RECRUITING: ["hr_operations"],
                TaskCategory.CONTENT: ["content", "marketing"],
            }
            chain = category_chains.get(category, ["supervisor"])
            
            result = await chain_executor.execute_chain(
                agent_chain=chain,
                initial_context=initial_context,
                stop_on_error=False,
            )
        
        return {
            "success": result.get("status") == "completed",
            "platform": "momentaic",
            "result": result,
        }
    
    async def _route_to_agentforge(
        self,
        task: str,
        context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Route to AgentForge for complex workflows"""
        from app.integrations.agentforge_client import agentforge_client
        
        logger.info("Sending orchestration request to AgentForge API")
        
        result = await agentforge_client.orchestrate(
            task=task,
            context=context,
            user_id=user_id,
        )
        
        if result.get("success"):
            return {
                "success": True,
                "platform": "agentforge",
                "result": result.get("result", {}),
            }
        else:
            logger.warning("AgentForge API call failed", error=result.get("error"))
            # Fallback to local
            return await self._route_to_momentaic(task, TaskCategory.WORKFLOW, context)
    
    async def _route_to_yokaizen(
        self,
        task: str,
        category: TaskCategory,
        context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Route to Yokaizen for Sales/Marketing/Ops"""
        from app.integrations.yokaizen_client import yokaizen_client
        
        logger.info("Sending task execution request to Yokaizen API")
        
        result = await yokaizen_client.execute_task(
            task=task,
            swarm_type=category.value,
            context=context,
            user_id=user_id,
        )
        
        if result.get("success"):
            return {
                "success": True,
                "platform": "yokaizen",
                "result": result.get("result", {}),
            }
        else:
            logger.warning("Yokaizen API call failed", error=result.get("error"))
            # Fallback to local agents
            return await self._fallback_local(task, category, context)
    
    async def _fallback_local(
        self,
        task: str,
        category: TaskCategory,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Fallback to local MomentAIc agents when external platforms fail"""
        from app.agents.chain_executor import chain_executor
        
        # Map Yokaizen categories to local agents
        fallback_chains = {
            TaskCategory.SALES: ["sales", "sdr"],
            TaskCategory.MARKETING: ["marketing", "growth_hacker"],
            TaskCategory.OPERATIONS: ["devops", "product_pm"],
        }
        
        chain = fallback_chains.get(category, ["supervisor"])
        
        result = await chain_executor.execute_chain(
            agent_chain=chain,
            initial_context={"message": task, **(context or {})},
            stop_on_error=False,
        )
        
        return {
            "success": True,
            "platform": "momentaic_fallback",
            "result": result,
        }
    
    async def close(self):
        """Cleanup resources"""
        pass


# Singleton instance
ecosystem_router = EcosystemRouter()
