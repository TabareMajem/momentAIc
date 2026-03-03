
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


    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for content variations needing evaluation and test results to analyze.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} content variations needing evaluation and test results to analyze 2025")
        
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
                                "source": "JudgementAgent",
                                "analysis": response.content[:1500],
                                "agent": "judgement_agent",
                            }
                        )
                    actions.append({"name": "test_needed", "industry": industry})
                except Exception as e:
                    logger.error(f"JudgementAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Runs A/B evaluations on content variations and provides data-driven recommendations.
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
            
            prompt = f"""You are the A/B testing and content evaluation agent for a {industry} startup.

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
                        "agent": "judgement_agent",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("JudgementAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

judgement_agent = JudgementAgent()
