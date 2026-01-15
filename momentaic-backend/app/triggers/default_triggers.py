"""
Default Triggers - Auto-created for new startups
Part of SuperOS: The Proactive Heartbeat
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import structlog

from app.models.trigger import TriggerRule, TriggerType
from app.models.conversation import AgentType

logger = structlog.get_logger()


DEFAULT_TRIGGERS = [
    {
        "name": "Weekly Content Ideas",
        "description": "Generate fresh content ideas every Sunday",
        "trigger_type": TriggerType.TIME,
        "condition": {
            "cron": "0 18 * * 0"  # Sunday 6PM
        },
        "action": {
            "agent": "content",
            "task": "Generate 5 engaging social media post ideas for this week based on my startup's mission and recent trends.",
            "requires_approval": False
        },
        "cooldown_minutes": 1440,  # 1 day
        "max_triggers_per_day": 1,
    },
    {
        "name": "Daily Lead Pulse",
        "description": "Check for new leads and opportunities every morning",
        "trigger_type": TriggerType.TIME,
        "condition": {
            "cron": "0 9 * * 1-5"  # Mon-Fri 9AM
        },
        "action": {
            "agent": "sdr",
            "task": "Review my pipeline and draft outreach for the top 3 priority leads.",
            "requires_approval": True  # User approves before sending
        },
        "cooldown_minutes": 1440,
        "max_triggers_per_day": 1,
    },
    {
        "name": "Monthly Growth Report",
        "description": "Analyze growth metrics and suggest improvements",
        "trigger_type": TriggerType.TIME,
        "condition": {
            "cron": "0 10 1 * *"  # 1st of month, 10AM
        },
        "action": {
            "agent": "growth_hacker",
            "task": "Generate a monthly growth report with key metrics, trends, and 3 actionable recommendations.",
            "requires_approval": False
        },
        "cooldown_minutes": 43200,  # 30 days
        "max_triggers_per_day": 1,
    },
]


async def create_default_triggers(
    db: AsyncSession,
    startup_id: UUID,
    user_id: UUID,
) -> int:
    """
    Create default triggers for a new startup.
    Called during startup creation.
    
    Returns: Number of triggers created
    """
    created_count = 0
    
    for trigger_config in DEFAULT_TRIGGERS:
        trigger = TriggerRule(
            startup_id=startup_id,
            user_id=user_id,
            name=trigger_config["name"],
            description=trigger_config["description"],
            trigger_type=trigger_config["trigger_type"],
            condition=trigger_config["condition"],
            action=trigger_config["action"],
            cooldown_minutes=trigger_config["cooldown_minutes"],
            max_triggers_per_day=trigger_config["max_triggers_per_day"],
            is_active=True,
            is_paused=False,
        )
        db.add(trigger)
        created_count += 1
    
    await db.flush()
    
    logger.info(
        "Default triggers created",
        startup_id=str(startup_id),
        count=created_count
    )
    
    return created_count
