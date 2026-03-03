"""
Planning Agent
Decomposes complex startup goals into actionable, sequenced tasks.
"""

from typing import Dict, Any, List
import structlog
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent, AgentState, get_agent_config
from app.models.conversation import AgentType

logger = structlog.get_logger()


# --- Structured Output Models ---

class Task(BaseModel):
    id: str = Field(description="Unique task identifier, e.g., TASK-1")
    description: str = Field(description="Detailed description of what needs to be done")
    assigned_agent: str = Field(description="The AgentType best suited to handle this task (e.g., 'sales_hunter', 'content_creator', 'growth_hacker')")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs that must be completed before this one")

class GoalDecomposition(BaseModel):
    goal_summary: str = Field(description="A brief summary of the parsed user goal")
    estimated_complexity: str = Field(description="Complexity level: Low, Medium, High")
    tasks: List[Task] = Field(description="A sequenced list of tasks required to achieve the goal")


class PlanningAgent(BaseAgent):
    """
    Planning Agent - Goal Decomposition and Orchestration
    
    Capabilities:
    - Breaks down complex goals into atomic tasks
    - Assigns tasks to appropriate specialized agents
    - Determines task dependencies for sequenced execution
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.PLANNING_AGENT)

    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a high-level goal and return a structured plan."""
        
        logger.info("PlanningAgent processing goal", user_id=user_id)
        from app.agents.base import web_search
        
        # [KILL SHOT 4] Predictive War Gaming (Live Search Inject)
        search_query = f"{startup_context.get('name', 'Startup')} {startup_context.get('industry', 'Technology')} {message} trends competitors"
        try:
            logger.info("PlanningAgent: Executing Predictive War Gaming search...")
            market_intel = await web_search.ainvoke(search_query)
        except Exception as e:
            logger.warning("Predictive War Gaming search failed", error=str(e))
            market_intel = "Market intelligence currently unavailable due to search failure."
        
        # Build prompt with context + memory + intel
        context_str = ""
        if startup_context:
            context_str = f"""
Startup: {startup_context.get('name', 'Unknown')}
Industry: {startup_context.get('industry', 'Unknown')}
Stage: {startup_context.get('stage', 'Unknown')}
{startup_context.get('agent_memory', '')}

[PREDICTIVE WAR GAMING INTEL - LIVE MARKET DATA]:
{market_intel}
"""
        
        prompt = f"""
Current Context:
{context_str}

User Goal:
{message}

Analyze the user's high-level goal and decompose it into a structured, executable plan.
Identify the specific tasks required, order them by dependencies, and assign each to the most appropriate AI agent from our swarm.

Available Agents: 
- sales_hunter (Lead generation, outreach)
- content_creator (Blogs, social posts, writing)
- growth_hacker (Experiments, viral loops, acquisition)
- tech_lead (Architecture, code, API)
- finance_cfo (Financial models, pricing)
- product_pm (User stories, roadmap)
- marketing_agent (Campaigns, brand)
- legal_counsel (Terms, contracts)
- devops_agent (Deployment, infrastructure)
"""
        try:
            # Leverage BaseAgent structured output + Agent Replay tracing
            structured_plan, chain_of_thought = await self.structured_llm_call(
                prompt=prompt,
                response_model=GoalDecomposition,
                model_name="gemini-pro",
                include_cot=True
            )
            
            # Format the response beautifully for the chat UI
            response_md = f"### 🗺️ Execution Plan: {structured_plan.goal_summary}\n"
            response_md += f"**Complexity Profile:** {structured_plan.estimated_complexity}\n\n"
            
            for task in structured_plan.tasks:
                deps = f"*(Depends on: {', '.join(task.dependencies)})*" if task.dependencies else ""
                response_md += f"- **[{task.id}]** Assign to `{task.assigned_agent}`: {task.description} {deps}\n"
                
                # Publish to A2A Message Bus
                startup_id = startup_context.get('startup_id')
                # Try to get it from general kwargs or state if possible, though currently only startup_context is passed.
                # It's better to verify if startup_id is passed, else we can't publish.
                # In agents endpoints, startup_id is usually tracked in a higher-level state.
                # We'll import MessageBus and publish dynamically.
                try:
                    from app.core.database import AsyncSessionLocal
                    from app.services.message_bus import MessageBus
                    
                    # Assuming we can grab it from a side channel or database if not directly in context,
                    # but the standard `process` param should be `startup_id`.
                    # For now, let's gracefully try to publish if we have the ID.
                    if startup_id:
                        async with AsyncSessionLocal() as db:
                            bus = MessageBus(db)
                            await bus.publish(
                                startup_id=startup_id,
                                from_agent=AgentType.PLANNING_AGENT.value,
                                topic=f"task.{task.assigned_agent}",
                                message_type="ACTION",
                                payload=task.model_dump(),
                                to_agent=task.assigned_agent,
                                priority="high"
                            )
                            await db.commit()
                except Exception as bus_err:
                    logger.warning(f"Failed to publish A2A task for {task.id}", error=str(bus_err))
                
            response_md += "\n*How would you like to proceed? We can execute these sequentially or focus on a specific task first.*"
            
            return {
                "response": response_md,
                "structured_plan": structured_plan.model_dump(),
                "chain_of_thought": chain_of_thought,
                "agent_used": AgentType.PLANNING_AGENT.value
            }
            
        except Exception as e:
            logger.error("PlanningAgent encountered an error", error=str(e))
            return {
                "response": f"I hit a roadblock while trying to plan this out. Error: {str(e)}",
                "agent_used": AgentType.PLANNING_AGENT.value
            }

# Singleton instance

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for incomplete goals, stalled tasks, and priority shifts.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} incomplete goals, stalled tasks, and priority shifts 2025")
        
        if results:
            from app.agents.base import get_llm
            llm = get_llm("gemini-pro", temperature=0.3)
            if llm:
                from langchain_core.messages import HumanMessage
                prompt = f"""Analyze these results for a {industry} startup:
{str(results)[:2000]}

Identify the top 3 actionable insights. Be concise."""
                try:
                    response = await llm.ainvoke([HumanMessage(content=prompt)])
                    from app.agents.base import BaseAgent
                    if hasattr(self, 'publish_to_bus'):
                        await self.publish_to_bus(
                            topic="intelligence_gathered",
                            data={
                                "source": "PlanningAgent",
                                "analysis": response.content[:1500],
                                "agent": "planning_agent",
                            }
                        )
                    actions.append({"name": "plan_stalled", "industry": industry})
                except Exception as e:
                    logger.error(f"PlanningAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Auto-decomposes startup goals into sequenced, agent-assigned task lists.
        """
        action_type = action.get("action", action.get("name", "unknown"))

        try:
            from app.agents.base import get_llm, web_search
            from langchain_core.messages import HumanMessage
            
            industry = startup_context.get("industry", "Technology")
            llm = get_llm("gemini-pro", temperature=0.5)
            
            if not llm:
                return "LLM not available"
            
            search_results = await web_search(f"{industry} {action_type} best practices 2025")
            
            prompt = f"""You are the Goal decomposition and task orchestration agent for a {industry} startup.

Based on this context:
- Action requested: {action_type}
- Industry: {industry}
- Research: {str(search_results)[:1500]}

Generate a concrete, actionable deliverable. No fluff. Be specific and executable."""
            
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            if hasattr(self, 'publish_to_bus'):
                await self.publish_to_bus(
                    topic="deliverable_generated",
                    data={
                        "type": action_type,
                        "content": response.content[:2000],
                        "agent": "planning_agent",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("PlanningAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

planning_agent = PlanningAgent()
