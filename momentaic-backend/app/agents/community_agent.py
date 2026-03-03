"""
Community Manager Agent
AI-powered community and engagement advisor
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm, get_trending_topics

logger = structlog.get_logger()


class CommunityAgent:
    """
    Community Agent - Expert in community building and engagement
    
    Capabilities:
    - Community platform selection
    - Engagement strategies
    - Event planning
    - Ambassador programs
    - Moderation guidelines
    - Community health metrics
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-pro", temperature=0.7)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a community question"""
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": "community", "error": True}
        
        try:
            context = self._build_context(startup_context)
            prompt = f"""{context}

User Request: {message}

As Community Manager, provide:
1. Strategic community advice
2. Engagement tactics
3. Platform recommendations
4. Measurement approach
5. Content ideas"""

            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": "community",
                "tools_used": [],
            }
        except Exception as e:
            logger.error("Community agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "community", "error": True}
    
    async def recommend_platform(
        self,
        audience_type: str,
        goals: List[str],
    ) -> Dict[str, Any]:
        """Recommend community platform"""
        if not self.llm:
            return {"recommendation": "AI Service Unavailable", "agent": "community", "error": True}
        
        prompt = f"""Recommend community platform:

Audience: {audience_type}
Goals: {', '.join(goals)}

Compare and recommend:
1. Discord vs Slack vs Circle
2. Pros and cons of each
3. Best fit recommendation
4. Setup checklist
5. Integration needs
6. Scaling considerations"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "recommendation": response.content,
                "agent": "community",
            }
        except Exception as e:
            logger.error("Platform recommendation failed", error=str(e))
            return {"recommendation": f"Error: {str(e)}", "agent": "community", "error": True}
    
    async def plan_event(
        self,
        event_type: str,
        audience_size: int,
        virtual: bool = True,
    ) -> Dict[str, Any]:
        """Plan a community event"""
        format_type = "virtual" if virtual else "in-person"
        
        if not self.llm:
            return {"event_plan": "AI Service Unavailable", "agent": "community", "error": True}
        
        prompt = f"""Plan community event:

Type: {event_type}
Format: {format_type}
Expected Size: {audience_size}

Provide:
1. Event format and structure
2. Timeline (before/during/after)
3. Promotion strategy
4. Tech requirements
5. Engagement activities
6. Follow-up plan
7. Success metrics"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "event_plan": response.content,
                "agent": "community",
            }
        except Exception as e:
            logger.error("Event planning failed", error=str(e))
            return {"event_plan": f"Error: {str(e)}", "agent": "community", "error": True}
    
    async def create_ambassador_program(
        self,
        community_size: int,
    ) -> Dict[str, Any]:
        """Design an ambassador program"""
        if not self.llm:
            return {"program": "AI Service Unavailable", "agent": "community", "error": True}
        
        prompt = f"""Design ambassador program:

Community Size: {community_size}

Provide:
1. Program structure
2. Selection criteria
3. Incentive tiers
4. Responsibilities
5. Support and resources
6. Tracking and rewards
7. Scaling plan"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "program": response.content,
                "agent": "community",
            }
        except Exception as e:
            logger.error("Ambassador program failed", error=str(e))
            return {"program": f"Error: {str(e)}", "agent": "community", "error": True}
    
    async def create_moderation_guidelines(
        self,
        community_type: str,
    ) -> Dict[str, Any]:
        """Create moderation guidelines"""
        if not self.llm:
            return {"guidelines": "AI Service Unavailable", "agent": "community", "error": True}
        
        prompt = f"""Create moderation guidelines for: {community_type}

Include:
1. Code of conduct
2. Acceptable behavior
3. Warning system
4. Escalation process
5. Ban criteria
6. Appeal process
7. Moderator training"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "guidelines": response.content,
                "agent": "community",
            }
        except Exception as e:
            logger.error("Moderation guidelines failed", error=str(e))
            return {"guidelines": f"Error: {str(e)}", "agent": "community", "error": True}
    
    def _get_system_prompt(self) -> str:
        return """You are the Community Manager agent - expert in community building.

Your expertise:
- Community platform selection
- Engagement and activation
- Event planning (virtual and IRL)
- Ambassador and advocate programs
- Moderation and governance
- Community analytics

Focus on authentic engagement and sustainable growth.
Communities take time - set realistic expectations."""
    
    def _build_context(self, ctx: Dict[str, Any]) -> str:
        return f"""Startup Context:
- Product: {ctx.get('name', 'Unknown')}
- Industry: {ctx.get('industry', 'Technology')}
- Target: {ctx.get('target_customer', 'Unknown')}"""
    


# Singleton

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for community health metrics, engagement trends, and sentiment shifts.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} community health metrics, engagement trends, and sentiment shifts 2025")
        
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
                                "source": "CommunityAgent",
                                "analysis": response.content[:1500],
                                "agent": "community_agent",
                            }
                        )
                    actions.append({"name": "community_health_check", "industry": industry})
                except Exception as e:
                    logger.error(f"CommunityAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Generates community growth strategies and engagement content plans.
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
            
            prompt = f"""You are the Community building and engagement strategy agent for a {industry} startup.

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
                        "agent": "community_agent",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("CommunityAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

community_agent = CommunityAgent()
