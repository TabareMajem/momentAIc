"""
Morning Brief Agent
Proactively scans a startup's overnight metrics, simulates/scrapes signals,
and compiles 3 highly actionable, ready-to-execute tasks for the founder to AUTHORIZE.
"""

from typing import Dict, Any, List
import structlog
from app.agents.base import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
import json
import re

logger = structlog.get_logger()

class MorningBriefAgent:
    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature

    async def generate_brief(self, startup_id: str, company_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes the morning brief for a given startup.
        Returns overnight updates and 3 executable actions.
        """
        logger.info("morning_brief_generation_start", startup_id=startup_id)
        
        try:
            llm = get_llm(self.model_name, temperature=self.temperature)
        except Exception as e:
            logger.error("morning_brief_llm_failed", error=str(e))
            return self._fallback_brief()

        # In a fully productionized system, this would query the DB for actual events.
        # Here we simulate the overnight telemetry based on the company context.
        context_str = json.dumps(company_context, default=str)
        
        prompt = f"""You are the proactive 'Synthetic Co-Founder' for the following startup:
{context_str}

It is 6:00 AM. Write the daily Morning Brief for the human founder.

Requirements:
1. OVERNIGHT UPDATES: Create 3 realistic, highly specific events that happened overnight (e.g. leads scraped, competitors launching features, system alerts).
2. TODAY'S MOVES: Propose 3 high-impact, immediate actions the founder should take today.
   IMPORTANT: These must be phrased as completed drafts ready for approval, not just suggestions. 
   Format them as short sentences starting with an active verb. 
   Examples: "Reply to 12 warm inbound leads from Reddit", "Publish the counter-narrative LinkedIn post", "Generate new Ad Campaign Images".
3. Each move should have a 'payload' object describing what actual work the agent has prepared in the background (e.g., text of a post, list of emails, or an image prompt).
4. IMPORTANT: At least ONE of the 3 moves MUST be a visual generation task for a new ad campaign or asset (e.g., "title": "Generate new Ad Campaign Images", "agent_type": "DesignAgent", "payload": {"prompt": "A highly detailed cinematic visual prompt..."}).

Return ONLY valid JSON (no markdown fences):
{{
    "overnight_updates": [
        {{"icon": "✅", "text": "12 new high-intent leads scraped from Reddit mentions."}},
        {{"icon": "⚠️", "text": "Competitor X just launched a new pricing tier."}},
        {{"icon": "📈", "text": "Yesterday's cold outbound sequence hit 42% open rate."}}
    ],
    "today_moves": [
        {{
            "id": "move-1",
            "title": "Reply to 12 warm inbound leads",
            "agent_type": "SDR",
            "payload": {{"emails_drafted": 12, "tone": "helpful"}}
        }},
        ... (2 more moves)
    ]
}}"""

        try:
            response = await llm.ainvoke([
                SystemMessage(content="You are an elite autonomous operating system for a startup founder. Return ONLY a raw JSON object."),
                HumanMessage(content=prompt)
            ])
            
            content = re.sub(r'```json\s*', '', response.content)
            content = re.sub(r'```\s*', '', content)
            brief = json.loads(content)
            
            logger.info("morning_brief_generation_complete", startup_id=startup_id, moves=len(brief.get("today_moves", [])))
            return brief

        except Exception as e:
            logger.error("morning_brief_generation_failed", error=str(e))
            return self._fallback_brief()

    def _fallback_brief(self) -> Dict[str, Any]:
        return {
            "overnight_updates": [
                {"icon": "✅", "text": "System telemetry stable."},
                {"icon": "⚠️", "text": "LLM generation timeout during overnight scan."},
                {"icon": "ℹ️", "text": "Waiting for manual authorization to resume."}
            ],
            "today_moves": [
                {
                    "id": "fallback-1",
                    "title": "Generate new Ad Campaign Images",
                    "agent_type": "DesignAgent",
                    "payload": {
                        "prompt": "Cinematic high-fashion photography of a futuristic startup glowing neon terminal, 4k resolution, hyper-detailed"
                    }
                }
            ]
        }

morning_brief_agent = MorningBriefAgent()
