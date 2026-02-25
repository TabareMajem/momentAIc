"""
Yokaizen Specialized Growth Agent
Strategy: Strategic Growth Architecture: Advanced ASO Optimization & Viral Mechanics
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import structlog

from app.agents.base import BaseAgent
from app.services.agent_memory_service import agent_memory_service

logger = structlog.get_logger()

class YokaizenStrategyResponse(BaseModel):
    """Structured response for Yokaizen strategic advice"""
    tactics: List[str] = Field(description="Specific actionable growth or ASO tactics")
    reasoning: str = Field(description="Strategic reasoning based on the 'Stealth Therapy' context")
    target_audience: str = Field(description="Which market segment this targets (Japan or West)")
    viral_mechanic: Optional[str] = Field(description="Proposed viral loop or physical-digital bridge")

STRATEGY_CONTEXT = """
# Strategic Growth Architecture: Yokaizen

## 1. Executive Strategy
Yokaizen occupies a position at the intersection of "cozy" games and digital companions. 
Core Philosophy: "Stealth Therapy". 
Goal: Address "Global Self-Worth Deficit".
Target: Japan (Satori generation, "Yorisoi") and West ("Optimized Self", "Shadow Work").

## 2. Market Anthropology
- **Japan**: "Archipelago of Silence". Users want "Ibasho" (a place to belong) and "Yorisoi" (snuggling up). Avoid "Mental Health" jargon. Use "Iyashi" (healing).
- **West**: "Optimized Self". Finch success. Users want "Gamified Utility" and "Shadow Work". "Cozy Game" aesthetic.

## 3. ASO Strategy (Japan)
- **Primary Keywords**: Yorisoi (Snuggle), Iyashi (Healing), Ibasho (Safe Place), Honne (True Feelings).
- **Title**: Yokaizen: Kokoro ni Yorisoi AI Yokai to Jiko Koutei Kan Ikusei.
- **Hook**: "Relieve Anxiety & Stress, Learn Heart Self-Care via Manga".

## 4. ASO Strategy (West)
- **Primary Keywords**: Anxiety Relief, CBT, Shadow Work, ADHD Tools, Cozy Game.
- **Title**: Yokaizen: Self-Care RPG & Pet.
- **Hook**: "Turn Your Mental Health Journey into an Epic Anime Adventure."

## 5. Viral Growth Engine
- **Bonded Yokai (Co-Parenting)**: Two users share one Yokai. "Sync Quests" require both users to log data.
- **Mirror Shard Referral**: Users recruit friends to "give" a reward (unlock evolution), not get one. Incentivized Altruism.
- **Inner Yokai Generator**: Personality quiz -> Shareable "Shadow Fox" image -> Install.
"""

class YokaizenAgent(BaseAgent):
    """Expert agent for Yokaizen growth scaling and viral mechanics"""
    
    async def chat(
        self, 
        user_input: str, 
        startup_context: Dict[str, Any] = None,
        user_id: str = None
    ) -> YokaizenStrategyResponse:
        """
        Respond to user queries with a structured strategic action plan based on Yokaizen framework.
        """
        logger.info("YokaizenAgent planning strategy", query=user_input)
        startup_context = startup_context or {}
        
        # Inject Memory
        memory_context = ""
        if startup_context.get("id"):
            memories = await agent_memory_service.get_relevant_memories(
                startup_id=startup_context["id"],
                query=user_input,
                agent_type="yokaizen"
            )
            if memories:
                memory_context = "\n\n=== PAST MEMORIES ===\n" + "\n".join(f"- {m.content}" for m in memories)
                
        prompt = f"""
        You are the Yokaizen Specialized Growth Agent, the Chief Strategy Officer for the Yokaizen app.
        You have deep knowledge of the specific 'Stealth Therapy' strategy, ASO tactics for Japan vs West,
        and Viral Mechanics (Bonded Yokai, NFC Cards).
        
        Your goal is to answer questions and generate tactics solely based on this specific strategic framework.
        
        === STRATEGY CONTEXT ===
        {STRATEGY_CONTEXT}
        {memory_context}
        
        === STARTUP / USER CONTEXT ===
        Name: {startup_context.get('name', 'Unknown')}
        Target Market: {startup_context.get('target_market', 'Global')}
        
        === USER REQUEST ===
        {user_input}
        
        Analyze the request and provide a structured strategic response.
        """
        
        return await self.structured_llm_call(
            prompt=prompt,
            response_model=YokaizenStrategyResponse,
            model_name="gemini-2.5-pro",
            temperature=0.7
        )

# Singleton instance
yokaizen_agent = YokaizenAgent()

