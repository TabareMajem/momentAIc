"""
Agent-to-Agent Message Model
A2A Protocol: enables direct, structured communication between agents.
Phase 1 supports INSIGHT and REQUEST message types.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, DateTime, String, Text,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base


class A2AMessageType(str, enum.Enum):
    """Core A2A message types"""
    INSIGHT = "INSIGHT"     # Share a discovery or observation
    REQUEST = "REQUEST"     # Ask another agent to perform a task
    ALERT = "ALERT"         # Urgent notification (Phase 2)
    HANDOFF = "HANDOFF"     # Transfer ownership of a task (Phase 2)
    DEBATE = "DEBATE"       # Structured disagreement (Phase 2)


class MessagePriority(str, enum.Enum):
    """Message priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MessageStatus(str, enum.Enum):
    """Message processing status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSED = "processed"
    EXPIRED = "expired"
    FAILED = "failed"


class AgentMessage(Base):
    """
    Inter-agent message following the A2A Protocol envelope schema.
    Enables loose-coupled agent coordination without the founder as intermediary.
    """
    __tablename__ = "agent_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )

    # Message envelope
    message_type: Mapped[A2AMessageType] = mapped_column(
        SQLEnum(A2AMessageType, native_enum=False, length=50), nullable=False
    )
    from_agent: Mapped[str] = mapped_column(String(100), nullable=False)
    to_agent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # NULL = broadcast
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    priority: Mapped[MessagePriority] = mapped_column(
        SQLEnum(MessagePriority, native_enum=False, length=50), default=MessagePriority.MEDIUM, nullable=False
    )

    # Payload
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Threading
    thread_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    parent_message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_messages.id"), nullable=True
    )

    # Response tracking
    requires_response: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    response_deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    response_received: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Status
    status: Mapped[MessageStatus] = mapped_column(
        SQLEnum(MessageStatus, native_enum=False, length=50), default=MessageStatus.PENDING, nullable=False
    )

    # Resolution (for DEBATE messages in Phase 2)
    resolution: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Founder escalation
    escalated_to_founder: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    founder_decision: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Self-referential relationship for threading
    parent_message = relationship("AgentMessage", remote_side="AgentMessage.id", uselist=False)
    startup = relationship("Startup")

    __table_args__ = (
        Index("ix_a2a_startup_to", "startup_id", "to_agent"),
        Index("ix_a2a_startup_from", "startup_id", "from_agent"),
        Index("ix_a2a_topic", "topic"),
        Index("ix_a2a_thread", "thread_id"),
        Index("ix_a2a_status", "status"),
        Index("ix_a2a_created", "created_at"),
    )
