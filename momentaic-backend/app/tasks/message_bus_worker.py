import structlog
import asyncio
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.message_bus import MessageBus
from app.models.agent_message import MessageStatus
from sqlalchemy import select

logger = structlog.get_logger(__name__)

# Registry mapping from agent IDs to their class initializers
def get_agent_instance(agent_id: str):
    if agent_id == "yc_advisor_agent":
        from app.agents.yc_advisor_agent import YCAdvisorAgent
        return YCAdvisorAgent()
    elif agent_id == "musk_enforcer_agent":
        from app.agents.musk_enforcer_agent import MuskEnforcerAgent
        return MuskEnforcerAgent()
    # Add other core agents here as needed
    return None

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

async def process_a2a_messages_async():
    """
    Sweeps the database for unread PENDING messages and dispatches them 
    to the correct Agent handler.
    """
    logger.info("Message Bus Sweep: Checking for PENDING A2A messages...")
    
    # Create fresh engine and session maker per loop execution
    # to avoid async pg connection pool issues across Celery process forks
    engine = create_async_engine(settings.database_url, echo=False)
    local_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    
    async with local_session_maker() as db:
        # Get pending messages from the bus
        from app.models.agent_message import AgentMessage
        query = select(AgentMessage).where(AgentMessage.status == MessageStatus.PENDING.value).order_by(AgentMessage.created_at.asc()).limit(50)
        result = await db.execute(query)
        messages = result.scalars().all()
        
        if not messages:
            return 0
            
        processed_count = 0
        
        for msg in messages:
            logger.info(f"Routing message {msg.id} -> {msg.to_agent} (Topic: {msg.topic})")
            
            # Find the target agent
            target_agent = get_agent_instance(msg.to_agent)
            
            if target_agent:
                try:
                    # Execute the agent's logic handler
                    # We inject the db session temporarily
                    target_agent.db_session = db
                    await target_agent.handle_message(msg)
                    
                    # Mark successful
                    msg.status = MessageStatus.DELIVERED.value
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Agent {msg.to_agent} failed to handle message {msg.id}", error=str(e))
                    msg.status = MessageStatus.FAILED.value
            else:
                logger.warning(f"No agent class found for ID: {msg.to_agent}")
                msg.status = MessageStatus.FAILED.value
                
        await db.commit()
        return processed_count

@celery_app.task
def sweep_message_bus():
    """
    Celery entrypoint for sweeping the A2A message bus.
    Can be hooked into celery-beat to run every minute.
    """
    # Wrap the async function in the synchronous celery envelope
    count = asyncio.run(process_a2a_messages_async())
    if count > 0:
        logger.info(f"Message Bus Sweep complete. Processed {count} messages.")
    return count
