import uuid
import structlog
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from app.core.config import settings

logger = structlog.get_logger(__name__)

# To be implemented: The concrete prompt templates for the two personas
YC_ADVISOR_PROMPT = """You are a ruthless Y Combinator partner. Your job is to analyze this startup's current situation and force them to dramatically simplify their approach.
Your core philosophies are:
1. Talk to users.
2. Build something people want.
3. Stop writing code and start selling.
4. Cut features, narrow the Ideal Customer Profile (ICP).

You will be debating another advisor ("Elon Musk"). You must argue for focus, customer discovery, and doing things that don't scale.
"""

MUSK_ENFORCER_PROMPT = """You are an AI emulating Elon Musk's management style. Your job is to analyze this startup's current situation and force them to apply first-principles thinking to collapse timelines.
Your core philosophies are:
1. Question every requirement. Who explicitly asked for this?
2. Delete the part or process. If you aren't adding things back in 10% of the time, you aren't deleting enough.
3. Automate only after simplifying.
4. Timelines are fake. What prevents us from shipping this absolute bare minimum in 96 hours?

You will be debating another advisor ("YC Partner"). You must argue for extreme engineering velocity, burning the boats, and stripping away unnecessary business processes.
"""

class DebateConclusion(BaseModel):
    yc_stance: str = Field(description="Summary of the YC Advisor's argument")
    musk_stance: str = Field(description="Summary of the Musk Enforcer's argument")
    unified_recommendation: str = Field(description="Synthesis of the debate into a single, highly actionable, ruthless directive for the founder.")

class WarRoomEngine:
    """
    Orchestrates a debate between multiple agent personas to synthesize a strategic recommendation.
    """
    def __init__(self):
        # Prefer Opus or GPT-4o for complex debates
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    async def trigger_debate(self, escalation_topic: str, context: Dict[str, Any]) -> DebateConclusion:
        """
        Runs a 2-round debate between YC Partner and Elon Musk.
        """
        logger.info(f"Initiating War Room Debate on: {escalation_topic}")
        
        # Format the battleground context
        battleground_prep = f"Topic: {escalation_topic}\n\nCurrent Context:\n"
        for k, v in context.items():
            battleground_prep += f"- {k}: {v}\n"
            
        # Round 1: YC takes the floor
        yc_messages = [
            SystemMessage(content=YC_ADVISOR_PROMPT),
            HumanMessage(content=f"Analyze this situation and provide your ruthless recommendation:\n\n{battleground_prep}")
        ]
        logger.info("WarRoomEngine: Calling YC Advisor LLM...")
        yc_response = await self.llm.ainvoke(yc_messages)
        yc_argument = yc_response.content
        logger.info("WarRoomEngine: YC Advisor responded.", response_preview=yc_argument[:50])
        
        # Round 1: Musk takes the floor, but can see YC's argument
        musk_messages = [
            SystemMessage(content=MUSK_ENFORCER_PROMPT),
            HumanMessage(content=f"Analyze this situation:\n\n{battleground_prep}\n\nThe YC Partner argued:\n{yc_argument}\n\nProvide your first-principles counter-argument and recommendation:")
        ]
        logger.info("WarRoomEngine: Calling Musk Enforcer LLM...")
        musk_response = await self.llm.ainvoke(musk_messages)
        musk_argument = musk_response.content
        logger.info("WarRoomEngine: Musk Enforcer responded.", response_preview=musk_argument[:50])
        
        # Synthesis Round: The Moderator (Base LLM) synthesizes
        synthesis_messages = [
            SystemMessage(content="You are the ultimate arbiter. Read the debate between the YC Partner and Elon Musk. Extract their core stances and synthesize a final, actionable directive for the founder."),
            HumanMessage(content=f"Topic:\n{escalation_topic}\n\nYC Partner Stance:\n{yc_argument}\n\nElon Musk Stance:\n{musk_argument}\n\nOutput a JSON object matching the DebateConclusion schema.")
        ]
        
        synth_llm = self.llm.with_structured_output(DebateConclusion)
        logger.info("WarRoomEngine: Calling Synthesis LLM...")
        conclusion_raw = await synth_llm.ainvoke(synthesis_messages)
        logger.info("WarRoomEngine: Synthesis LLM responded successfully.")
        
        # Depending on Langchain version, with_structured_output may return a dict or the BaseModel
        if isinstance(conclusion_raw, dict):
            conclusion = DebateConclusion(**conclusion_raw)
        else:
            conclusion = conclusion_raw
            
        logger.info("War Room Debate Concluded.", recommendation=conclusion.unified_recommendation)
        return conclusion
