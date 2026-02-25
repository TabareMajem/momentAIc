"""
Agent Outcome Tracking & Memory Models
Phase 3: Tracks what agents did, what worked, and what they remember.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
import hashlib

from app.core.database import Base


# ═══════════════════════════════════════════════════════════════════════════════
# OUTCOME TRACKING — Did the agent's output actually work?
# ═══════════════════════════════════════════════════════════════════════════════

class OutcomeStatus(str, enum.Enum):
    pending = "pending"         # Output generated, awaiting result
    successful = "successful"   # Output led to positive outcome
    failed = "failed"           # Output failed or was rejected
    neutral = "neutral"         # No measurable impact


class AgentOutcome(Base):
    """
    Tracks every autonomous agent action and its result.
    Enables learning: which strategies work for which startups.
    """
    __tablename__ = "agent_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )

    # What agent did what
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "SalesAgent"
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "auto_hunt"
    
    # The input and output
    input_context: Mapped[dict] = mapped_column(JSONB, default=dict)   # What was fed to the agent
    output_data: Mapped[dict] = mapped_column(JSONB, default=dict)     # What agent produced
    
    # Results tracking
    outcome_status: Mapped[OutcomeStatus] = mapped_column(
        SQLEnum(OutcomeStatus), default=OutcomeStatus.pending
    )
    outcome_metric: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g. "leads_converted"
    outcome_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)       # e.g. 3.0
    outcome_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Cost tracking
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_outcomes_startup_agent", "startup_id", "agent_name"),
        Index("ix_outcomes_status", "outcome_status"),
        Index("ix_outcomes_created", "created_at"),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT MEMORY — What the agent remembers between runs
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryType(str, enum.Enum):
    fact = "fact"               # "Startup X targets elderly care market"
    preference = "preference"   # "Founder prefers LinkedIn over Twitter"
    learning = "learning"       # "Reddit posts at 9am get 2x engagement"
    strategy = "strategy"       # "Focus on nursing homes for Q1"
    warning = "warning"         # "Competitor Y just raised $10M"


class AgentMemoryEntry(Base):
    """
    Persistent memory for agents scoped to a startup.
    Agents can read/write memories to maintain context between runs.
    """
    __tablename__ = "agent_memory_store"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )

    # Scope
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)  # "*" for global
    memory_type: Mapped[MemoryType] = mapped_column(
        SQLEnum(MemoryType), default=MemoryType.fact
    )

    # Content
    key: Mapped[str] = mapped_column(String(255), nullable=False)   # Lookup key
    value: Mapped[str] = mapped_column(Text, nullable=False)        # The memory content
    extra_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)     # Extra context
    
    # Relevance
    importance: Mapped[int] = mapped_column(Integer, default=5)     # 1-10 scale
    access_count: Mapped[int] = mapped_column(Integer, default=0)   # How often recalled
    
    # Expiry
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_memstore_startup_agent", "startup_id", "agent_name"),
        Index("ix_memstore_key", "startup_id", "key"),
        Index("ix_memstore_type", "memory_type"),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# LEAD DEDUPLICATION — Hash-based dedup to prevent duplicate leads
# ═══════════════════════════════════════════════════════════════════════════════

class LeadFingerprint(Base):
    """
    Stores hashed fingerprints of discovered leads to prevent duplicates.
    Hash = sha256(startup_id + company_name.lower() + contact_email.lower())
    """
    __tablename__ = "lead_fingerprints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    fingerprint_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    source_agent: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_fingerprints_hash", "fingerprint_hash"),
        Index("ix_fingerprints_startup", "startup_id"),
    )

    @staticmethod
    def compute_hash(startup_id: str, company_name: str, contact_email: str = "") -> str:
        """Compute a dedup hash for a lead."""
        raw = f"{startup_id}|{company_name.lower().strip()}|{(contact_email or '').lower().strip()}"
        return hashlib.sha256(raw.encode()).hexdigest()
