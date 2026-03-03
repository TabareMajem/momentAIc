"""
AI Ambassador Outreach Agent
Automates influencer and ambassador recruitment with personalized messages.
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm

logger = structlog.get_logger()


class AmbassadorOutreachAgent:
    """
    Ambassador Outreach Agent - Specializes in recruiting and managing influencers.
    
    Capabilities:
    - Candidate analysis (fit score)
    - Multi-channel personalized outreach (Twitter, LinkedIn, Email)
    - Value proposition customization for influencers
    - Campaign recruitment
    """
    
    def __init__(self):
        # We will initialize the LLM lazily within the methods to avoid event loop issues
        pass
    
    
    def _get_llm(self):
        # Use GPT-4o for complex reasoning and creative drafting (Gemini had region availability issues)
        return get_llm("gpt-4o", temperature=0.7)
    
    async def analyze_candidate(
        self,
        candidate_profile: Dict[str, Any],
        startup_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze if a candidate is a good fit for the ambassador program"""
        llm = self._get_llm()
        if not llm:
            return {"fit_score": 0, "reasoning": "AI Service Unavailable", "error": True}
        
        prompt = f"""Analyze this potential brand ambassador for the startup:
        
Startup: {startup_context.get('name')}
Description: {startup_context.get('description')}
Industry: {startup_context.get('industry')}

Candidate Profile:
{candidate_profile}

Provide a JSON response with:
1. fit_score (0-100)
2. reasoning (key strengths and concerns)
3. primary_platform (where they are strongest)
4. outreach_angle (best hook to use)"""

        try:
            # Note: In production we use structured output parsing, but here we'll simulate logic
            response = await llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "agent": "ambassador_outreach",
            }
        except Exception as e:
            logger.error("Candidate analysis failed", error=str(e))
            return {"error": str(e), "agent": "ambassador_outreach"}

    async def generate_outreach(
        self,
        candidate_name: str,
        platform: str,
        startup_context: Dict[str, Any],
        program_summary: str,
        custom_instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a personalized outreach message"""
        llm = self._get_llm()
        if not llm:
            return {"message": "AI Service Unavailable", "error": True}
        
        prompt = f"""Generate a recruitment message for a potential brand ambassador.

Target Name: {candidate_name}
Platform: {platform}
Startup: {startup_context.get('name')} ({startup_context.get('tagline')})
Program Details: {program_summary}
Custom Instructions: {custom_instructions or "Keep it professional yet exciting."}

Requirements:
- High personalization
- Clear call to action
- Mention how their specific audience (based on the platform) would benefit
- Avoid corporate jargon"""

        try:
            response = await llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "message": response.content,
                "platform": platform,
                "agent": "ambassador_outreach",
            }
        except Exception as e:
            logger.error("Outreach generation failed", error=str(e))
            return {"error": str(e), "agent": "ambassador_outreach"}

    def _get_system_prompt(self) -> str:
        return """You are the AI Ambassador Outreach Agent. 
Your goal is to recruit high-quality brand ambassadors for early-stage startups.
You are persuasive, authentic, and expert at identifying "fit" between a brand and an influencer.
You specialize in 1:1 personalization—no generic templates.
You understand the nuances of different platforms (Twitter/X vs LinkedIn vs Email)."""

# Singleton

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for influencer activity and outreach timing opportunities.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} influencer activity and outreach timing opportunities 2025")
        
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
                                "source": "AmbassadorOutreachAgent",
                                "analysis": response.content[:1500],
                                "agent": "ambassador_agent",
                            }
                        )
                    actions.append({"name": "outreach_opportunity", "industry": industry})
                except Exception as e:
                    logger.error(f"AmbassadorOutreachAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Drafts hyper-personalized influencer outreach messages across platforms.
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
            
            prompt = f"""You are the Influencer and ambassador personalized outreach agent for a {industry} startup.

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
                        "agent": "ambassador_agent",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("AmbassadorOutreachAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

ambassador_agent = AmbassadorOutreachAgent()
