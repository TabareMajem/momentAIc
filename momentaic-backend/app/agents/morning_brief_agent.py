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


    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for overnight metrics changes, competitor movements, and market shifts.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} overnight metrics changes, competitor movements, and market shifts 2025")
        
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
                                "source": "MorningBriefAgent",
                                "analysis": response.content[:1500],
                                "agent": "morning_brief_agent",
                            }
                        )
                    actions.append({"name": "brief_ready", "industry": industry})
                except Exception as e:
                    logger.error(f"MorningBriefAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Generates actionable morning briefs with prioritized founder tasks.
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
            
            prompt = f"""You are the Daily startup intelligence briefing agent for a {industry} startup.

Based on this context:
- Action requested: {action_type}
- Industry: {industry}
- Research: {str(search_results)[:1500]}

Generate a concrete, actionable deliverable. No fluff. Be specific and executable."""
            
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            # ── DELIVER EMAIL & FLUSH DIGEST QUEUE ──────────────────
            try:
                from app.services.notification_service import notification_service
                from app.integrations.gmail import gmail_integration
                from app.core.config import settings as app_settings
                from app.core.redis_client import redis_client
                import json
                
                founder_email = startup_context.get("founder_email", getattr(app_settings, "GMAIL_USER", ""))
                startup_name = startup_context.get("name", "Your Startup")
                
                # 1. Send the Morning Brief
                await notification_service.dispatch_agent_alert(
                    startup_id=startup_context.get("id"),
                    agent_name="MorningBriefAgent",
                    channel="email",
                    dispatch_func=gmail_integration.execute_action,
                    action="send_email",
                    params={
                        "to": founder_email,
                        "subject": f"☀️ Morning Brief — {startup_name}",
                        "body": response.content[:5000],
                        "priority": "urgent",
                        "agent_name": "Morning Brief Agent"
                    }
                )
                logger.info("Morning Brief emailed to founder")
                
                # 2. Flush the Digest Queue
                queue_key = f"email_digest_queue:{founder_email}"
                digest_items = []
                while await redis_client.llen(queue_key) > 0:
                    item_str = await redis_client.lpop(queue_key)
                    if item_str:
                        digest_items.append(json.loads(item_str))
                
                if digest_items:
                    digest_text = "Here is a roll-up of your low-priority agent updates from the last 24 hours:\n\n"
                    for item in digest_items:
                        digest_text += f"\n### [{item.get('agent_name', 'Agent')}] {item.get('subject', 'Update')}\n"
                        digest_text += f"{item.get('body', '')}\n\n---\n"
                    await notification_service.dispatch_agent_alert(
                        startup_id=startup_context.get("id"),
                        agent_name="NotificationAgent",
                        channel="email",
                        dispatch_func=gmail_integration.execute_action,
                        action="send_email",
                        params={
                            "to": founder_email,
                            "subject": f"📦 Daily Agent Digest ({len(digest_items)} items)",
                            "body": digest_text,
                            "priority": "urgent",
                            "agent_name": "Notification Agent"
                        }
                    )
                    logger.info(f"Morning Digest sent with {len(digest_items)} items")

            except Exception as mail_err:
                logger.warning("Morning Brief email delivery failed", error=str(mail_err))

            # ── DELIVER VIA SLACK ─────────────────────────────────
            try:
                from app.integrations.slack import SlackIntegration
                slack = SlackIntegration()
                
                await notification_service.dispatch_agent_alert(
                    startup_id=startup_context.get("id"),
                    agent_name="MorningBriefAgent",
                    channel="slack",
                    dispatch_func=slack.execute_action,
                    action="send_message",
                    params={
                        "channel": "#general",
                        "text": f"☀️ *Morning Brief — {startup_context.get('name', 'Startup')}*\n{response.content[:500]}",
                    }
                )
                logger.info("Morning Brief posted to Slack")
            except Exception as slack_err:
                logger.warning("Morning Brief Slack delivery failed", error=str(slack_err))

            if hasattr(self, 'publish_to_bus'):
                await self.publish_to_bus(
                    topic="deliverable_generated",
                    data={
                        "type": action_type,
                        "content": response.content[:2000],
                        "agent": "morning_brief_agent",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("MorningBriefAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

morning_brief_agent = MorningBriefAgent()
