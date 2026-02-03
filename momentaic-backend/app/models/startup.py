"""
Startup Domain Models
Core entity management for the Entrepreneur OS
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, Date,
    ForeignKey, Enum as SQLEnum, Index, Float
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
import uuid
import enum

from app.core.database import Base


class StartupStage(str, enum.Enum):
    """Startup lifecycle stages"""
    IDEA = "idea"
    MVP = "mvp"
    PMF = "pmf"
    SCALING = "scaling"
    MATURE = "mature"


class Startup(Base):
    """Startup entity - the core tenant object"""
    __tablename__ = "startups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tagline: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    stage: Mapped[StartupStage] = mapped_column(
        SQLEnum(StartupStage), default=StartupStage.IDEA, nullable=False
    )
    
    # RAG Support - Embedding for context matching
    description_embedding: Mapped[Optional[List[float]]] = mapped_column(
        Vector(1536), nullable=True
    )
    
    # Metrics (Flexible JSONB)
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"mrr": 5000, "dau": 150, "runway_months": 18, "burn_rate": 15000}
    
    # Integrations (Encrypted tokens stored separately)
    github_repo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Settings
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="startups")
    signals: Mapped[List["Signal"]] = relationship(
        "Signal", back_populates="startup", cascade="all, delete-orphan"
    )
    sprints: Mapped[List["Sprint"]] = relationship(
        "Sprint", back_populates="startup", cascade="all, delete-orphan"
    )
    leads: Mapped[List["Lead"]] = relationship(
        "Lead", back_populates="startup", cascade="all, delete-orphan"
    )
    content_items: Mapped[List["ContentItem"]] = relationship(
        "ContentItem", back_populates="startup", cascade="all, delete-orphan"
    )
    workflows: Mapped[List["Workflow"]] = relationship(
        "Workflow", back_populates="startup", cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="startup", cascade="all, delete-orphan"
    )
    acquisition_channels: Mapped[List["AcquisitionChannel"]] = relationship(
        "AcquisitionChannel", back_populates="startup", cascade="all, delete-orphan"
    )
    action_items: Mapped[List["ActionItem"]] = relationship(
        "ActionItem", back_populates="startup", cascade="all, delete-orphan"
    )
    
    # Proactive Agent System
    autonomy_settings: Mapped[Optional["StartupAutonomySettings"]] = relationship(
        "StartupAutonomySettings", back_populates="startup", uselist=False, cascade="all, delete-orphan"
    )
    proactive_actions: Mapped[List["ProactiveActionLog"]] = relationship(
        "ProactiveActionLog", back_populates="startup", cascade="all, delete-orphan"
    )


    __table_args__ = (
        Index("ix_startups_owner", "owner_id"),
        Index("ix_startups_industry", "industry"),
    )


class Signal(Base):
    """Neural Signal Engine - Computed startup health scores"""
    __tablename__ = "signals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    
    # Computed Scores (0-100)
    tech_velocity: Mapped[float] = mapped_column(Float, default=0)
    pmf_score: Mapped[float] = mapped_column(Float, default=0)
    growth_momentum: Mapped[float] = mapped_column(Float, default=0)
    runway_health: Mapped[float] = mapped_column(Float, default=0)
    overall_score: Mapped[float] = mapped_column(Float, default=0)
    
    # Raw Data Used for Calculation
    raw_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"commits_7d": 45, "commits_prev_7d": 30, "mrr_growth": 0.15}
    
    # AI Analysis
    ai_insights: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendations: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    startup: Mapped["Startup"] = relationship("Startup", back_populates="signals")

    __table_args__ = (
        Index("ix_signals_startup_calculated", "startup_id", "calculated_at"),
    )


class Sprint(Base):
    """Weekly sprint/goal management"""
    __tablename__ = "sprints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    
    # Sprint Info
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    key_results: Mapped[List[str]] = mapped_column(JSONB, default=list)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, completed, abandoned
    
    # Progress
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    completed_results: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # AI Feedback
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    startup: Mapped["Startup"] = relationship("Startup", back_populates="sprints")
    standups: Mapped[List["Standup"]] = relationship(
        "Standup", back_populates="sprint", cascade="all, delete-orphan"
    )


class Standup(Base):
    """Daily standup entries"""
    __tablename__ = "standups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sprint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sprints.id", ondelete="CASCADE"), nullable=False
    )
    
    # Standup Content
    yesterday: Mapped[str] = mapped_column(Text, nullable=False)
    today: Mapped[str] = mapped_column(Text, nullable=False)
    blockers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mood: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # great, good, meh, struggling
    
    # AI Analysis
    alignment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # How aligned with sprint goal
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    sprint: Mapped["Sprint"] = relationship("Sprint", back_populates="standups")


# Forward references
from app.models.user import User
from app.models.growth import Lead, ContentItem, AcquisitionChannel
from app.models.workflow import Workflow
from app.models.conversation import Conversation
from app.models.autonomy import StartupAutonomySettings, ProactiveActionLog
