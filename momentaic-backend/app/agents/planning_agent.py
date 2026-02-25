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
        
        # Build prompt with context + memory
        context_str = ""
        if startup_context:
            context_str = f"""
Startup: {startup_context.get('name', 'Unknown')}
Industry: {startup_context.get('industry', 'Unknown')}
Stage: {startup_context.get('stage', 'Unknown')}
{startup_context.get('agent_memory', '')}
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
            # Leverage BaseAgent structured output
            structured_plan: GoalDecomposition = await self.structured_llm_call(
                prompt=prompt,
                response_model=GoalDecomposition,
                model_name="gemini-pro"
            )
            
            # Format the response beautifully for the chat UI
            response_md = f"### 🗺️ Execution Plan: {structured_plan.goal_summary}\n"
            response_md += f"**Complexity Profile:** {structured_plan.estimated_complexity}\n\n"
            
            for task in structured_plan.tasks:
                deps = f"*(Depends on: {', '.join(task.dependencies)})*" if task.dependencies else ""
                response_md += f"- **[{task.id}]** Assign to `{task.assigned_agent}`: {task.description} {deps}\n"
                
            response_md += "\n*How would you like to proceed? We can execute these sequentially or focus on a specific task first.*"
            
            return {
                "response": response_md,
                "structured_plan": structured_plan.model_dump(),
                "agent_used": AgentType.PLANNING_AGENT.value
            }
            
        except Exception as e:
            logger.error("PlanningAgent encountered an error", error=str(e))
            return {
                "response": f"I hit a roadblock while trying to plan this out. Error: {str(e)}",
                "agent_used": AgentType.PLANNING_AGENT.value
            }

# Singleton instance
planning_agent = PlanningAgent()
