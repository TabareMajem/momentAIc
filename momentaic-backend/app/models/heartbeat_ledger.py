"""
Heartbeat Ledger Model
Tracks every heartbeat cycle for every agent — the autonomic nervous system's audit trail.
OpenClaw-inspired: each agent wakes, evaluates, acts, and logs.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, DateTime, Integer, Float, String, Text,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base


class HeartbeatResult(str, enum.Enum):
    """The four possible outcomes of a heartbeat cycle"""
    OK = "OK"                     # Nothing requires attention
    INSIGHT = "INSIGHT"           # Something noteworthy detected
    ACTION = "ACTION"             # Autonomous action taken within guardrails
    ESCALATION = "ESCALATION"    # Requires human decision


class HeartbeatLedger(Base):
    """
    Audit log of every agent heartbeat cycle.
    Tracks what the agent checked, what it found, what it did, and what it cost.
    """
    __tablename__ = "heartbeat_ledger"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )

    # Agent identification
    agent_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # Heartbeat result
    heartbeat_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    result_type: Mapped[HeartbeatResult] = mapped_column(
        SQLEnum(HeartbeatResult), nullable=False
    )

    # What triggered this result
    checklist_item: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    context_snapshot: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # metrics/data

    # What was done
    action_taken: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Cost tracking
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Human-in-loop
    founder_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    founder_response: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    startup = relationship("Startup")

    __table_args__ = (
        Index("ix_hb_startup_agent", "startup_id", "agent_id"),
        Index("ix_hb_result_type", "result_type"),
        Index("ix_hb_timestamp", "heartbeat_timestamp"),
        Index("ix_hb_startup_ts", "startup_id", "heartbeat_timestamp"),
    )
