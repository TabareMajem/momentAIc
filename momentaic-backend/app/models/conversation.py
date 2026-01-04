"""
Conversation Models
Multi-agent chat system with supervisor routing
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


class AgentType(str, enum.Enum):
    """Available agent types in the swarm"""
    # Core Agents
    SUPERVISOR = "supervisor"  # Routes to other agents
    SALES_HUNTER = "sales_hunter"  # Lead research & outreach
    CONTENT_CREATOR = "content_creator"  # Content generation
    # Phase 1 Specialists
    TECH_LEAD = "tech_lead"  # Technical advice
    FINANCE_CFO = "finance_cfo"  # Financial analysis
    LEGAL_COUNSEL = "legal_counsel"  # Legal guidance
    GROWTH_HACKER = "growth_hacker"  # Growth strategies
    PRODUCT_PM = "product_pm"  # Product management
    # Phase 2 Specialists
    CUSTOMER_SUCCESS = "customer_success"  # Retention & churn
    DATA_ANALYST = "data_analyst"  # Metrics & analytics
    HR_OPERATIONS = "hr_operations"  # Hiring & people ops
    MARKETING = "marketing"  # Brand & campaigns
    COMMUNITY = "community"  # Community building
    DEVOPS = "devops"  # Infrastructure & deployment
    STRATEGY = "strategy"  # Vision & planning
    JUDGEMENT = "judgement"  # Content critique & optimization
    # Special Agents
    BROWSER = "browser"  # Web automation
    QA_TESTER = "qa_tester"  # App auditing & automated testing
    GENERAL = "general"  # General assistant
    # Personas
    ELON_MUSK = "elon_musk" # First principles, hardcore
    PAUL_GRAHAM = "paul_graham" # YC Founder wisdom
    # New Guidance Agents
    ONBOARDING_COACH = "onboarding_coach"  # Guides users through startup journey
    COMPETITOR_INTEL = "competitor_intel"  # Competitive intelligence
    FUNDRAISING_COACH = "fundraising_coach" # Fundraising guidance


class MessageRole(str, enum.Enum):
    """Message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class Conversation(Base):
    """Chat conversation container"""
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    # Conversation Info
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    agent_type: Mapped[AgentType] = mapped_column(
        SQLEnum(AgentType), default=AgentType.SUPERVISOR
    )
    
    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Context (injected into each message)
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    startup: Mapped["Startup"] = relationship("Startup", back_populates="conversations")
    user: Mapped["User"] = relationship("User")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    __table_args__ = (
        Index("ix_conversations_startup_user", "startup_id", "user_id"),
        Index("ix_conversations_active", "is_active"),
    )


class Message(Base):
    """Individual chat message"""
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    
    # Message Content
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Agent Info (for assistant messages)
    agent_type: Mapped[Optional[AgentType]] = mapped_column(SQLEnum(AgentType), nullable=True)
    
    # Tool Calls (if any)
    tool_calls: Mapped[List[dict]] = mapped_column(JSONB, default=list)
    """
    Example:
    [
        {
            "id": "call_123",
            "type": "function",
            "function": {"name": "web_search", "arguments": {...}}
        }
    ]
    """
    
    tool_results: Mapped[List[dict]] = mapped_column(JSONB, default=list)
    
    # Metadata
    message_meta: Mapped[dict] = mapped_column(JSONB, default=dict)  # Renamed from 'metadata' (reserved)
    # Example: {"tokens_used": 500, "model": "gemini-pro", "latency_ms": 1200}
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )


class AgentMemory(Base):
    """Long-term memory storage for agents (per startup context)"""
    __tablename__ = "agent_memories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    agent_type: Mapped[AgentType] = mapped_column(SQLEnum(AgentType), nullable=False)
    
    # Memory Content
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False)  # fact, preference, context, summary
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Importance (for retrieval ranking)
    importance: Mapped[float] = mapped_column(Integer, default=5)  # 1-10
    
    # Source
    source_conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    source_message_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    access_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        Index("ix_agent_memories_startup_agent", "startup_id", "agent_type"),
        Index("ix_agent_memories_importance", "importance"),
    )


# Forward references
from app.models.startup import Startup
from app.models.user import User
