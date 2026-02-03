"""
Autonomy Settings Model
Stores user-controlled autonomy levels for proactive agents
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text,
    Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class AutonomyLevel(enum.IntEnum):
    """User-controlled autonomy grades"""
    OBSERVER = 0      # Information only
    ADVISOR = 1       # Draft & suggest
    COPILOT = 2       # Act with confirmation
    AUTOPILOT = 3     # Full autonomy


class ActionCategory(str, enum.Enum):
    """Categories for granular autonomy control"""
    MARKETING = "marketing"
    SALES = "sales"
    FINANCE = "finance"
    OPERATIONS = "operations"
    CONTENT = "content"
    COMPETITIVE = "competitive"


class ActionStatus(str, enum.Enum):
    """Status of a proactive action"""
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"
    UNDONE = "undone"


class StartupAutonomySettings(Base):
    """
    Stores autonomy preferences for each startup.
    Users can set a global level and override per category.
    """
    __tablename__ = "startup_autonomy_settings"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    startup_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), 
        unique=True, nullable=False
    )
    
    # Global autonomy level (0-3)
    global_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Per-category overrides (null = use global)
    marketing_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sales_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    finance_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    competitive_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Safety limits
    daily_action_limit: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    daily_spend_limit_usd: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    
    # Emergency controls
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paused_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Notification preferences
    notify_on_action: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_channel: Mapped[str] = mapped_column(String(50), default="email", nullable=False)  # email, slack, push
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    startup = relationship("Startup", back_populates="autonomy_settings")
    
    def get_level_for_category(self, category: ActionCategory) -> int:
        """Returns the effective autonomy level for a given category"""
        category_map = {
            ActionCategory.MARKETING: self.marketing_level,
            ActionCategory.SALES: self.sales_level,
            ActionCategory.FINANCE: self.finance_level,
            ActionCategory.CONTENT: self.content_level,
            ActionCategory.COMPETITIVE: self.competitive_level,
        }
        level = category_map.get(category)
        return level if level is not None else self.global_level


class ProactiveActionLog(Base):
    """
    Audit log of all proactive actions taken by agents.
    Enables undo/review and trust building.
    """
    __tablename__ = "proactive_action_logs"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    startup_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    
    # Action metadata
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "growth_hacker"
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "social_post_publish"
    category: Mapped[ActionCategory] = mapped_column(SQLEnum(ActionCategory), nullable=False)
    
    # Action details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON payload
    
    # Status tracking
    status: Mapped[ActionStatus] = mapped_column(
        SQLEnum(ActionStatus), default=ActionStatus.PENDING_APPROVAL, nullable=False
    )
    autonomy_level_used: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Execution details
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON result
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Human-in-loop
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Undo capability
    is_reversible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    undone_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    undo_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    
    # Relationships
    startup = relationship("Startup", back_populates="proactive_actions")
