"""
Ghost Mentor Agent
Acts as a ruthless, highly experienced startup mentor (Paul Graham, Elon Musk, etc.)
Delivers daily 'hard truths' to force prioritization and kill feature creep.
"""

from typing import List,  Dict, Any
import structlog
from app.agents.base import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
import json

logger = structlog.get_logger()

class GhostMentorAgent:
    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.9):
        # High temperature for more creative/aggressive mentor personalities
        self.model_name = model_name
        self.temperature = temperature

    async def get_daily_hard_truth(self, company_context: Dict[str, Any], mentor_persona: str = "pg") -> str:
        """
        Generates a 2-3 sentence 'hard truth' based on the startup's context.
        mentor_persona: 'pg' (Paul Graham style), 'musk' (Elon style), or 'jobs' (Steve Jobs style).
        """
        logger.info("ghost_mentor_generation_start", persona=mentor_persona)
        
        try:
            llm = get_llm(self.model_name, temperature=self.temperature)
        except Exception as e:
            logger.error("ghost_mentor_llm_failed", error=str(e))
            return "You are building features nobody asked for. Talk to 5 customers today. Not 3. Five."

        context_str = json.dumps(company_context, default=str)
        
        personas = {
            "pg": "You are Paul Graham. Your advice is concise, mildly condescending but deeply true, focusing intensely on talking to users and not building fake startups format. Focus on product-market fit.",
            "musk": "You are Elon Musk. Your advice is intense, physics-based, and focused on extreme speed, deleting unnecessary parts, and sleeping on the factory floor. Be blunt.",
            "jobs": "You are Steve Jobs. Your advice focuses on extreme focus, taste, and cutting 100 good ideas to find the 1 great idea. Say NO."
        }
        
        system_prompt = personas.get(mentor_persona, personas["pg"])
        
        prompt = f"""Read this startup's context:
{context_str}

Deliver your daily 'hard truth' to the solo founder. 
Do not greet them. Do not use hashtags. 
Write exactly 2-3 sentences. Identify the most likely trap they are falling into right now (e.g. optimizing prematurely, ignoring sales, building features instead of selling) and give them a harsh directive to fix it today."""

        try:
            response = await llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ])
            
            note = response.content.strip().replace('"', '')
            logger.info("ghost_mentor_generation_complete", note_length=len(note))
            return note

        except Exception as e:
            logger.error("ghost_mentor_generation_failed", error=str(e))
            return "Stop optimizing code. No one is using your product yet. Go sell."


    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for founder focus drift, feature creep, and priority misalignment.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} founder focus drift, feature creep, and priority misalignment 2025")
        
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
                                "source": "GhostMentorAgent",
                                "analysis": response.content[:1500],
                                "agent": "ghost_mentor_agent",
                            }
                        )
                    actions.append({"name": "priority_drift_detected", "industry": industry})
                except Exception as e:
                    logger.error(f"GhostMentorAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Generates hard-truth founder nudges and priority enforcement advice.
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
            
            prompt = f"""You are the Ruthless startup mentorship and priority enforcement agent for a {industry} startup.

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
                        "agent": "ghost_mentor_agent",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("GhostMentorAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

ghost_mentor_agent = GhostMentorAgent()
