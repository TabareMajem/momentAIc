"""
Action Item Models
Stores proactive agent proposals waiting for user approval.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base
from app.models.startup import Startup

class ActionStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    executed = "executed"
    failed = "failed"

class ActionPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class ActionItem(Base):
    """
    A proactive proposal from an agent.
    Example: "I found a lead", "I drafted a post".
    """
    __tablename__ = "action_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    
    # Source
    source_agent: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "SalesAgent"
    
    # Display
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[ActionPriority] = mapped_column(
        SQLEnum(ActionPriority), default=ActionPriority.medium
    )
    
    # payload: The data needed to execute (e.g. the email draft, lead ID)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Status
    status: Mapped[ActionStatus] = mapped_column(
        SQLEnum(ActionStatus), default=ActionStatus.pending
    )
    
    # Execution result
    execution_result: Mapped[dict] = mapped_column(JSONB, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    startup: Mapped["Startup"] = relationship("Startup", back_populates="action_items")

    __table_args__ = (
        Index("ix_action_items_startup_status", "startup_id", "status"),
        Index("ix_action_items_created_at", "created_at"),
    )
