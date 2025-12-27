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
        return get_llm("gemini-2.5-pro", temperature=0.7)
    
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
ambassador_agent = AmbassadorOutreachAgent()
