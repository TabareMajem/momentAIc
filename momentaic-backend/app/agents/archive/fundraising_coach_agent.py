"""
Fundraising Coach Agent
Helps founders prepare for and execute fundraising campaigns
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm, web_search
from app.models.conversation import AgentType

logger = structlog.get_logger()

class FundraisingCoachAgent:
    """
    Fundraising Coach - Expert guidance for raising capital
    
    Capabilities:
    - Pitch deck review and feedback
    - Investor matching and research
    - Due diligence preparation
    - Valuation estimation
    - Term sheet explanation
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-2.0-flash", temperature=0.6)
    
    async def review_pitch_deck(self, content: str) -> Dict[str, Any]:
        """
        Review pitch deck content/structure
        """
        if not self.llm:
            return {"error": "LLM not available"}
            
        prompt = f"""Review this pitch deck content and provide critical feedback.
        
        Content:
        {content}
        
        Evaluate against the standard Sequoia/YC slides:
        1. Problem
        2. Solution
        3. Market Size (TAM/SAM/SOM)
        4. Product
        5. Traction
        6. Team
        7. Competition
        8. Financials
        9. Ask
        
        Provide specific, harsh but constructive feedback. What is missing? What is unclear?
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a top-tier VC associate reviewing a pitch deck."),
                HumanMessage(content=prompt)
            ])
            
            return {
                "feedback": response.content,
                "agent": "fundraising_coach"
            }
        except Exception as e:
            logger.error("Pitch review failed", error=str(e))
            return {"error": str(e)}

    async def identify_investors(self, startup_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find potential investors based on industry and stage.
        """
        industry = startup_context.get("industry", "Technology")
        stage = startup_context.get("stage", "Seed")
        
        # Use web search fallback (Real-ification)
        search_query = f"top VC firms {industry} {stage} stage active 2024 2025"
        
        try:
            search_results = web_search(search_query)
            
            prompt = f"""Identify 5-10 potential investors for a {stage} stage {industry} startup.
            
            Use these search results:
            {search_results}
            
            For each, explain WHY they are a good fit.
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a fundraising advisor."),
                HumanMessage(content=prompt)
            ])
             
            return {
                "investors": response.content,
                "agent": "fundraising_coach"
            }
        except Exception as e:
            return {"error": str(e)}

    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process fundraising requests
        """
        message_lower = message.lower()
        
        if "deck" in message_lower or "pitch" in message_lower:
            # Assume the message contains deck content or user wants review
            return await self.review_pitch_deck(message)
            
        if "investor" in message_lower or "vc" in message_lower or "angel" in message_lower:
            return await self.identify_investors(startup_context)
            
        # Default advice
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert fundraising coach. Answer the user's question about fundraising."),
                HumanMessage(content=message)
            ])
            return {
                "response": response.content,
                "agent": "fundraising_coach"
            }
        except Exception as e:
            return {"error": str(e)}

# Singleton
fundraising_coach_agent = FundraisingCoachAgent()
