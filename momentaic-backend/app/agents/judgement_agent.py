
from typing import Dict, Any, List, Optional
import structlog
from langchain.schema import SystemMessage, HumanMessage
import json
import re

from app.agents.base import get_llm, get_agent_config
from app.models.conversation import AgentType
from app.core.events import publish_event
import datetime

logger = structlog.get_logger()

class JudgementAgent:
    """
    Judgement Agent - The Critic & Optimizer
    Role: A/B Tests content, critiques drafts, and predicts viral potential.
    """
    
    def __init__(self):
        self._llm = None
        
    @property
    def llm(self):
        if self._llm is None:
            try:
                # Using 2.0 Flash for speed + analytical reasoning
                self._llm = get_llm("gemini-2.0-flash", temperature=0.2)
            except Exception as e:
                logger.error("JudgementAgent: LLM initialization failed", error=str(e))
        return self._llm

    async def evaluate_content(
        self, 
        goal: str, 
        target_audience: str, 
        variations: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate multiple content variations and pick a winner.
        """
        if not self.llm:
            return {"error": "Judgement Agent not initialized"}

        # Publish event
        await publish_event("agent_activity", {
            "agent": "JudgementAgent",
            "action": "evaluating_variations",
            "count": len(variations),
            "timestamp": str(datetime.datetime.utcnow())
        })

        variations_text = "\n\n".join([f"=== VARIATION {i+1} ===\n{v}" for i, v in enumerate(variations)])

        prompt = f"""
        You are the JUDGEMENT AGENT. Your job is to scientifically critique content for viral potential.
        
        GOAL: {goal}
        AUDIENCE: {target_audience}
        
        {variations_text}
        
        Analyze these variations based on:
        1. HOOK (First 2 seconds/lines)
        2. VALUE (Clarity of insight)
        3. CALL TO ACTION (Compelling trigger)
        
        Return a JSON object with:
        - "scores": [list of 0-100 scores for each variation]
        - "winner_index": (1-based index of the best variation)
        - "reasoning": "Short explanation of why it won"
        - "critique": ["Specific improvement for V1", "Specific improvement for V2"...]
        """

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a strict, data-driven content critic."),
                HumanMessage(content=prompt)
            ])
            
            # Parse JSON
            content = response.content
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                
                # Add original text to result for convenience
                winner_idx = result.get("winner_index", 1) - 1
                if 0 <= winner_idx < len(variations):
                    result["winner_text"] = variations[winner_idx]
                
                return result
            else:
                return {"error": "Failed to parse judgement", "raw": content}
                
        except Exception as e:
            logger.error("JudgementAgent: Evaluation failed", error=str(e))
            return {"error": str(e)}

    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        General chat interface for Judgement Agent
        """
        return {
            "response": "I am the Judgement Agent. Please use my specialized tools (like A/B testing) to evaluate content.",
            "agent": AgentType.JUDGEMENT.value 
        }

judgement_agent = JudgementAgent()
