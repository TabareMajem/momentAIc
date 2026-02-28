"""
Ghost Mentor Agent
Acts as a ruthless, highly experienced startup mentor (Paul Graham, Elon Musk, etc.)
Delivers daily 'hard truths' to force prioritization and kill feature creep.
"""

from typing import Dict, Any
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

ghost_mentor_agent = GhostMentorAgent()
