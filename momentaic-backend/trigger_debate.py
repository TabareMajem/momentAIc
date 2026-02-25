import asyncio
import sys
import uuid
import structlog
from app.core.database import AsyncSessionLocal
from app.services.message_bus import MessageBus
from app.models.agent_message import A2AMessageType, MessagePriority

logger = structlog.get_logger(__name__)

async def trigger_war_room(startup_id: str):
    logger.info("Triggering War Room escalation manually for testing...")
    
    async with AsyncSessionLocal() as db:
        bus = MessageBus(db)
        # Emit the escalation!
        await bus.publish(
            startup_id=startup_id,
            from_agent="heartbeat_engine",
            topic="heartbeat.escalation",
            message_type=A2AMessageType.ALERT.value,
            payload={
                "trigger": "Stagnant Growth Detected",
                "details": "0 user interviews logged this week. MRR is flat.",
                "urgency": "critical"
            },
            priority=MessagePriority.CRITICAL.value
        )
        await db.commit()
    
    logger.info("Escalation published. The YC Advisor should now intercept and summon Elon Musk.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trigger_debate.py <startup_uuid>")
        sys.exit(1)
        
    asyncio.run(trigger_war_room(sys.argv[1]))
