import json
import structlog
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage
from app.agents.base import get_llm

logger = structlog.get_logger()

class NLTriggerService:
    """
    Parses Natural Language Triggers (e.g., 'Every Monday, research my competitors')
    into structured database TriggerRules (cron expressions + agent actions).
    """

    async def parse_trigger(self, nl_command: str) -> Optional[Dict[str, Any]]:
        """
        Takes a natural language string and uses an LLM to extract the cron schedule
        and the intended agent action.
        """
        prompt = f"""You are a Natural Language to Cron Job Parser.
Your job is to convert the user's plain text command into a scheduled automation.

User Command: "{nl_command}"

You need to extract:
1. The execution schedule, converted to a standard CRON expression (e.g., '0 9 * * 1' for Every Monday at 9AM). Default time to 9AM (0 9) if unspecified.
2. The agent best suited for the task. Available agents: 'sales_hunter', 'content_creator', 'finance_cfo', 'growth_hacker', 'competitor_intel', 'tech_lead', 'product_pm', 'general'.
3. The specific task instruction for the agent.

Return ONLY a valid JSON object matching this structure:
{{
    "cron_expression": "* * * * *",
    "agent": "agent_name",
    "task_instruction": "Specific instructions..."
}}

If the command doesn't seem like a scheduled task, return {{"error": "Not a valid trigger command."}}
"""
        try:
            llm = get_llm("gemini-2.0-flash", temperature=0.1)
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            result_text = response.content.strip()

            if result_text.startswith("```"):
                result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            
            parsed = json.loads(result_text)
            if "error" in parsed:
                logger.warning("NLTrigger failed parsing", user_command=nl_command, info=parsed["error"])
                return None
                
            return {
                "cron": parsed["cron_expression"],
                "agent": parsed["agent"],
                "task": parsed["task_instruction"]
            }
        except Exception as e:
            logger.error("NLTrigger LLM evaluation failed", error=str(e))
            return None

    async def create_trigger_rule_from_nl(
        self, db, startup_id: str, user_id: str, nl_command: str
    ):
        """Creates a TriggerRule database entry directly from natural language."""
        parsed = await self.parse_trigger(nl_command)
        if not parsed:
            raise ValueError("Could not parse schedule or action from the command.")
            
        from app.models.trigger import TriggerRule, TriggerType
        import uuid
        
        rule = TriggerRule(
            startup_id=uuid.UUID(startup_id),
            user_id=uuid.UUID(user_id),
            name=f"Auto-Trigger: {nl_command[:50]}",
            description=f"Generated from NL: {nl_command}",
            trigger_type=TriggerType.TIME,
            condition={"cron": parsed["cron"], "timezone": "UTC"},
            action={
                "agent": parsed["agent"],
                "task": parsed["task"],
                "requires_approval": False,
                "type": "agent_task",
                "data": {"prompt": parsed["task"]}
            },
            is_active=True
        )
        
        db.add(rule)
        await db.flush()
        return rule

nl_trigger_service = NLTriggerService()
