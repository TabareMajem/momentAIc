from typing import Any, Dict
import structlog
from app.services.war_room import WarRoomEngine
from app.services.message_bus import MessageBus
from app.models.agent_message import A2AMessageType, MessagePriority

logger = structlog.get_logger(__name__)

class YCAdvisorAgent:
    """
    "Harsh but Fair" Office Hours Agent.
    Subscribes to heartbeat.escalation and initiates a War Room debate.
    """
    def __init__(self, db_session=None):
        self.name = "YC Advisor"
        self.role = "Startup Mentor"
        self.description = "Forces the entrepreneur to talk to users, focus on ICP, and cut features."
        self.db_session = db_session
        self.war_room = WarRoomEngine()

    async def handle_message(self, message: Any):
        """
        Triggered when MessageBus sends a heartbeat.escalation.
        """
        logger.info("YC Advisor: Intercepted an escalation! Summoning War Room...", topic=message.topic)
        
        # In a real scenario, context would be pulled from the message payload / DB stats
        context = {
            "Trigger": message.topic,
            "Recent Heartbeats": "0 user interviews logged this week.",
            "Growth": "Flat week over week."
        }
        
        # Start the debate
        conclusion = await self.war_room.trigger_debate(
            escalation_topic="Stagnant Growth & Lack of User Context",
            context=context
        )
        
        logger.info("War Room Output Generated. Ready to distribute to founder.")
        
        # Publish the final verdict back to the bus so the frontend/founders can see it
        mbus = MessageBus(self.db_session)
        await mbus.publish(
            startup_id=str(message.startup_id),
            from_agent="yc_advisor_agent",
            topic="war_room.verdict",
            message_type=A2AMessageType.INSIGHT.value,
            payload={
                "yc_stance": conclusion.yc_stance,
                "musk_stance": conclusion.musk_stance,
                "unified_recommendation": conclusion.unified_recommendation
            },
            priority=MessagePriority.HIGH.value
        )
