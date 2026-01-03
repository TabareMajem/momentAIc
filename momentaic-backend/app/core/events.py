
"""
Event Bus Module
Handles Redis Pub/Sub for real-time application events
"""

from typing import Dict, Any, Optional
import json
import redis.asyncio as redis
import structlog
from app.core.config import settings

logger = structlog.get_logger()

# Global Redis instance for events
_redis_client: Optional[redis.Redis] = None

async def get_redis_client() -> redis.Redis:
    """Get or create global Redis client for events"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client


async def publish_event(event_type: str, data: Dict[str, Any], channel: str = "momentaic:events"):
    """
    Publish an event to Redis channel
    """
    try:
        client = await get_redis_client()
        message = {
            "type": event_type,
            "data": data,
            "timestamp": str(data.get("timestamp", "")) 
        }
        await client.publish(channel, json.dumps(message))
        logger.debug("Event published", type=event_type, channel=channel)
    except Exception as e:
        logger.error("Failed to publish event", error=str(e))


async def subscribe_events(channel: str = "momentaic:events"):
    """
    Generator that yields events from Redis channel
    """
    client = await get_redis_client()
    pubsub = client.pubsub()
    await pubsub.subscribe(channel)
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield message["data"]
    except Exception as e:
        logger.error("Event subscription error", error=str(e))
    finally:
        await pubsub.unsubscribe(channel)
        # Note: We don't close the global client here as it's shared
