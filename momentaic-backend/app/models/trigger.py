"""
Trigger Models
Database models for proactive agent triggers
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


class TriggerType(str, enum.Enum):
    """Types of triggers"""
    METRIC = "metric"          # When a metric crosses threshold
    TIME = "time"              # Scheduled (cron-based)
    EVENT = "event"            # When an event occurs
    WEBHOOK = "webhook"        # External webhook trigger


class TriggerOperator(str, enum.Enum):
    """Operators for metric comparisons"""
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    EQUALS = "eq"
    NOT_EQUALS = "neq"
    INCREASES_BY = "increases_by"
    DECREASES_BY = "decreases_by"
    CHANGES_BY = "changes_by"


class TriggerRule(Base):
    """Proactive trigger rule"""
    __tablename__ = "trigger_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    # Rule definition
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[TriggerType] = mapped_column(
        SQLEnum(TriggerType), nullable=False
    )
    
    # Condition (what triggers it)
    condition: Mapped[dict] = mapped_column(JSONB, default=dict)
    """
    Examples:
    Metric: {"metric": "mrr", "operator": "decreases_by", "value": 10, "unit": "percent"}
    Time: {"cron": "0 9 * * 1", "timezone": "UTC"}  # Every Monday 9am
    Event: {"event": "lead_created", "filter": {"score": {"gt": 80}}}
    Webhook: {"secret": "abc123"}
    """
    
    # Action (what happens)
    action: Mapped[dict] = mapped_column(JSONB, default=dict)
    """
    Example:
    {
        "agent": "finance_cfo",
        "task": "analyze_metric_change",
        "notify": ["email", "slack"],
        "auto_execute": false  # Requires approval if true
    }
    """
    
    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Execution tracking
    last_evaluated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    trigger_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Rate limiting
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=60)  # Min time between triggers
    max_triggers_per_day: Mapped[int] = mapped_column(Integer, default=10)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    logs: Mapped[List["TriggerLog"]] = relationship(
        "TriggerLog", back_populates="rule", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_trigger_rules_startup", "startup_id"),
        Index("ix_trigger_rules_type", "trigger_type"),
        Index("ix_trigger_rules_active", "is_active"),
    )


class TriggerLogStatus(str, enum.Enum):
    """Trigger execution status"""
    TRIGGERED = "triggered"
    SKIPPED = "skipped"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class TriggerLog(Base):
    """Log of trigger executions"""
    __tablename__ = "trigger_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trigger_rules.id", ondelete="CASCADE"), nullable=False
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    
    # Execution details
    status: Mapped[TriggerLogStatus] = mapped_column(
        SQLEnum(TriggerLogStatus), default=TriggerLogStatus.TRIGGERED
    )
    
    # What triggered it
    trigger_context: Mapped[dict] = mapped_column(JSONB, default=dict)
    """
    Example:
    {
        "metric": "mrr",
        "previous_value": 10000,
        "current_value": 8500,
        "change_percent": -15
    }
    """
    
    # Agent response
    agent_response: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Approval (if required)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Error tracking
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    rule: Mapped["TriggerRule"] = relationship("TriggerRule", back_populates="logs")

    __table_args__ = (
        Index("ix_trigger_logs_rule", "rule_id"),
        Index("ix_trigger_logs_status", "status"),
        Index("ix_trigger_logs_triggered", "triggered_at"),
    )


class AgentAction(Base):
    """Actions taken by agents (with audit trail)"""
    __tablename__ = "agent_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    trigger_log_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trigger_logs.id", ondelete="SET NULL"), nullable=True
    )
    
    # Action details
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # Examples: "send_email", "post_linkedin", "update_crm", "browse_web"
    
    # What was done
    action_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    """
    Example:
    {
        "action": "send_email",
        "to": "lead@company.com",
        "subject": "Following up...",
        "body": "...",
        "integration_id": "..."
    }
    """
    
    # Result
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Approval (for destructive actions)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approved: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_agent_actions_startup", "startup_id"),
        Index("ix_agent_actions_type", "action_type"),
        Index("ix_agent_actions_pending", "requires_approval", "approved"),
    )
