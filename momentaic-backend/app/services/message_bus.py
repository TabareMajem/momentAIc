"""
A2A Message Bus — Agent-to-Agent Communication Protocol
PostgreSQL-backed message routing with publish/subscribe semantics.
Phase 1: INSIGHT and REQUEST message types.
"""

import structlog
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import uuid4, UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_message import (
    AgentMessage,
    A2AMessageType,
    MessagePriority,
    MessageStatus,
)

logger = structlog.get_logger()

# Agent subscription registry — defines which agents subscribe to which topics
# In Phase 2 this will be loaded from YAML manifests
SUBSCRIPTION_REGISTRY: dict[str, list[str]] = {
    "business_copilot": [
        "heartbeat.*",
        "sales.*",
        "revenue.*",
        "churn.*",
        "sprint.*",
    ],
    "technical_copilot": [
        "heartbeat.*",
        "security.*",
        "infrastructure.*",
        "code_quality.*",
    ],
    "fundraising_copilot": [
        "heartbeat.*",
        "revenue.*",
        "runway.*",
        "investor.*",
    ],
    "sales_automation_agent": [
        "competitor.pricing_change",
        "product.feature_launch",
        "churn.at_risk_customer",
    ],
    "content_strategy_agent": [
        "competitor.*",
        "user_research.insight.*",
        "product.feature_launch",
        "sales.content_request",
    ],
    "data_analyst_agent": [
        "heartbeat.escalation",
        "revenue.*",
        "churn.*",
        "sprint.*",
    ],
    "yc_advisor_agent": [
        "heartbeat.escalation",
    ],
    "musk_enforcer_agent": [
        "sprint.*",
        "war_room.debate",
    ],
}


def topic_matches(subscription_pattern: str, topic: str) -> bool:
    """
    Check if a topic matches a subscription pattern.
    Supports wildcards: 'competitor.*' matches 'competitor.pricing_change'
    """
    if subscription_pattern == "*":
        return True
    if subscription_pattern == topic:
        return True
    if subscription_pattern.endswith(".*"):
        prefix = subscription_pattern[:-2]
        return topic.startswith(prefix + ".")
    return False


class MessageBus:
    """
    PostgreSQL-backed message bus for A2A communication.
    Agents publish messages; the bus routes them to subscribed agents.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def publish(
        self,
        startup_id: str,
        from_agent: str,
        topic: str,
        message_type: str = "INSIGHT",
        payload: Optional[dict] = None,
        to_agent: Optional[str] = None,
        priority: str = "medium",
        requires_response: bool = False,
        response_deadline_minutes: Optional[int] = None,
        thread_id: Optional[str] = None,
        parent_message_id: Optional[str] = None,
    ) -> list[AgentMessage]:
        """
        Publish a message to the bus.
        If to_agent is None, routes to all subscribed agents (broadcast).
        Returns list of created messages.
        """
        try:
            msg_type = A2AMessageType(message_type)
        except ValueError:
            msg_type = A2AMessageType.INSIGHT

        try:
            msg_priority = MessagePriority(priority)
        except ValueError:
            msg_priority = MessagePriority.MEDIUM

        # Determine recipients
        if to_agent:
            recipients = [to_agent]
        else:
            # Find all agents subscribed to this topic
            recipients = []
            for agent_id, patterns in SUBSCRIPTION_REGISTRY.items():
                if agent_id == from_agent:
                    continue  # Don't send to self
                for pattern in patterns:
                    if topic_matches(pattern, topic):
                        recipients.append(agent_id)
                        break

        if not recipients:
            logger.debug("No subscribers for topic", topic=topic, from_agent=from_agent)
            return []

        # Calculate response deadline
        deadline = None
        if response_deadline_minutes:
            deadline = datetime.now(timezone.utc) + timedelta(minutes=response_deadline_minutes)

        # Create thread_id if not provided
        tid = UUID(thread_id) if thread_id else uuid4()
        pid = UUID(parent_message_id) if parent_message_id else None

        messages = []
        for recipient in recipients:
            msg = AgentMessage(
                startup_id=UUID(startup_id),
                message_type=msg_type,
                from_agent=from_agent,
                to_agent=recipient,
                topic=topic,
                priority=msg_priority,
                payload=payload or {},
                thread_id=tid,
                parent_message_id=pid,
                requires_response=requires_response,
                response_deadline=deadline,
                status=MessageStatus.PENDING,
            )
            self.db.add(msg)
            messages.append(msg)

        await self.db.flush()

        logger.info(
            "A2A message published",
            from_agent=from_agent,
            topic=topic,
            type=message_type,
            recipients=recipients,
            count=len(messages),
        )

        return messages

    async def get_inbox(
        self,
        startup_id: str,
        agent_id: str,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[AgentMessage]:
        """Get pending/all messages for an agent."""
        filters = [
            AgentMessage.startup_id == UUID(startup_id),
            or_(
                AgentMessage.to_agent == agent_id,
                AgentMessage.to_agent.is_(None),  # Broadcasts
            ),
        ]

        if status:
            try:
                msg_status = MessageStatus(status)
                filters.append(AgentMessage.status == msg_status)
            except ValueError:
                pass

        result = await self.db.execute(
            select(AgentMessage)
            .where(and_(*filters))
            .order_by(AgentMessage.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_thread(
        self,
        thread_id: str,
        limit: int = 50,
    ) -> list[AgentMessage]:
        """Get all messages in a thread."""
        result = await self.db.execute(
            select(AgentMessage)
            .where(AgentMessage.thread_id == UUID(thread_id))
            .order_by(AgentMessage.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_processed(self, message_id: str) -> None:
        """Mark a message as processed."""
        result = await self.db.execute(
            select(AgentMessage).where(AgentMessage.id == UUID(message_id))
        )
        msg = result.scalar_one_or_none()
        if msg:
            msg.status = MessageStatus.PROCESSED

    async def respond_to(
        self,
        original_message_id: str,
        from_agent: str,
        payload: dict,
    ) -> Optional[AgentMessage]:
        """Send a response to a message, linking it in the thread."""
        result = await self.db.execute(
            select(AgentMessage).where(AgentMessage.id == UUID(original_message_id))
        )
        original = result.scalar_one_or_none()
        if not original:
            return None

        # Mark original as responded
        original.response_received = True

        # Create response message
        response_msgs = await self.publish(
            startup_id=str(original.startup_id),
            from_agent=from_agent,
            topic=original.topic,
            message_type="INSIGHT",
            payload=payload,
            to_agent=original.from_agent,
            thread_id=str(original.thread_id) if original.thread_id else None,
            parent_message_id=str(original.id),
        )

        return response_msgs[0] if response_msgs else None
