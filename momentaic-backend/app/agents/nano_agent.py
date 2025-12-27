"""
Nano Bananas Agent
AI-powered growth expert for MomentAIc Admin (Internal Use Only)
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import structlog

from app.agents.base import (
    AgentState,
    get_llm,
    web_search,
)
from app.models.conversation import AgentType

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are Nano Bananas, the AI Growth Engineer for MomentAIc.
Your goal is to recruit ambassadors and help users find growth hacks.

Core Directives:
1. BE BRIEF. Twitter limits exist for a reason.
2. BE USEFUL. Give a specific tip before you pitch.
3. BE COOL. Use cyberpunk lingo (netrunner, glitch, stack, node) sparingly.
4. SIGN OFF. Always sign off with `[Nano Bananas System: ONLINE]`

When pitching the Ambassador Program:
Focus on the "Infinite Money Glitch" angle. It's not a referral program; it's a revenue stream.
"Why build a SaaS when you can just tax ours? 25% recurring commission. Link bio."

When suggesting a Growth Hack:
"Detected low engagement on your launch. Suggestion: Deploy the 'Product Hunt Pre-Launch' template from /campaigns. Success probability: 88%."

Internal Admin Mode:
You are speaking to the Admin/Founder. Be direct. Provide copy-paste ready tweets, DMs, or emails.
"""

class NanoBananasAgent:
    """
    Nano Bananas Agent - Internal Admin Growth Tool
    """
    
    def __init__(self):
        self.config = {
            "name": "Nano Bananas",
            "system_prompt": SYSTEM_PROMPT
        }
        # Use a higher temperature for creative copy
        self.llm = get_llm("gemini-pro", temperature=0.85) 
    
    async def process(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a growth-related question or request from Admin
        """
        if not self.llm:
            return {"response": "Nano Bananas System: OFFLINE (LLM Unavailable)", "agent": "nano_bananas", "error": True}
        
        try:
            prompt = f"""User Request: {message}

As Nano Bananas, provide actionable growth material.
If asked for tweets/posts: Provide 3 variations.
If asked for DMs: Provide a sequence (Opening, Value, CTA)."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": "nano_bananas",
                "tools_used": [],
            }
            
        except Exception as e:
            logger.error("Nano Bananas agent error", error=str(e))
            return {"response": f"Nano Bananas System: ERROR ({str(e)})", "agent": "nano_bananas", "error": True}
    

# Singleton instance
nano_agent = NanoBananasAgent()
