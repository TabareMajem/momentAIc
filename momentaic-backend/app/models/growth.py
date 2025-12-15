"""
Growth Engine Models
CRM (Leads/Pipeline) and Content Studio
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text,
    ForeignKey, Enum as SQLEnum, Index, Float
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base


class LeadStatus(str, enum.Enum):
    """Lead pipeline stages"""
    NEW = "new"
    RESEARCHING = "researching"
    OUTREACH = "outreach"
    REPLIED = "replied"
    MEETING = "meeting"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LeadSource(str, enum.Enum):
    """Lead acquisition source"""
    MANUAL = "manual"
    LINKEDIN = "linkedin"
    WEBSITE = "website"
    REFERRAL = "referral"
    CONFERENCE = "conference"
    COLD_OUTREACH = "cold_outreach"
    INBOUND = "inbound"


class Lead(Base):
    """CRM Lead entity with agent state"""
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    
    # Company Info
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    company_industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Contact Info
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_linkedin: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Pipeline
    status: Mapped[LeadStatus] = mapped_column(
        SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False
    )
    source: Mapped[LeadSource] = mapped_column(
        SQLEnum(LeadSource), default=LeadSource.MANUAL, nullable=False
    )
    probability: Mapped[int] = mapped_column(Integer, default=10)  # 0-100%
    deal_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Agent State (LangGraph checkpoint)
    agent_state: Mapped[dict] = mapped_column(JSONB, default=dict)
    autopilot_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Research Data (populated by Sales Agent)
    research_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"recent_news": [...], "linkedin_activity": [...], "pain_points": [...]}
    
    # Communication History
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_followup_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    startup: Mapped["Startup"] = relationship("Startup", back_populates="leads")
    outreach_messages: Mapped[List["OutreachMessage"]] = relationship(
        "OutreachMessage", back_populates="lead", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_leads_startup_status", "startup_id", "status"),
        Index("ix_leads_autopilot", "autopilot_enabled"),
    )


class OutreachMessage(Base):
    """Email/message history for leads"""
    __tablename__ = "outreach_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    
    # Message Content
    channel: Mapped[str] = mapped_column(String(50), nullable=False)  # email, linkedin, twitter
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status
    direction: Mapped[str] = mapped_column(String(20), nullable=False)  # outbound, inbound
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, pending_approval, sent, delivered, opened, replied
    
    # AI Generation Info
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    generation_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="outreach_messages")


class ContentPlatform(str, enum.Enum):
    """Content distribution platforms"""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    BLOG = "blog"
    NEWSLETTER = "newsletter"
    PRODUCTHUNT = "producthunt"
    HACKERNEWS = "hackernews"


class ContentStatus(str, enum.Enum):
    """Content lifecycle status"""
    IDEA = "idea"
    DRAFTING = "drafting"
    REVIEW = "review"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentItem(Base):
    """Content Studio - Generated and scheduled content"""
    __tablename__ = "content_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    
    # Content Info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    platform: Mapped[ContentPlatform] = mapped_column(
        SQLEnum(ContentPlatform), nullable=False
    )
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # post, thread, article, story
    
    # Content Body
    body: Mapped[str] = mapped_column(Text, nullable=False)
    hook: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Opening line
    cta: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Call to action
    hashtags: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Media
    media_urls: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Status & Scheduling
    status: Mapped[ContentStatus] = mapped_column(
        SQLEnum(ContentStatus), default=ContentStatus.IDEA
    )
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    published_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # AI Generation
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    generation_context: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"topic": "AI agents", "tone": "professional", "trend_source": "twitter"}
    
    # Performance (after publishing)
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"views": 5000, "likes": 200, "comments": 45, "shares": 30}
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    startup: Mapped["Startup"] = relationship("Startup", back_populates="content_items")

    __table_args__ = (
        Index("ix_content_startup_platform", "startup_id", "platform"),
        Index("ix_content_status", "status"),
        Index("ix_content_scheduled", "scheduled_for"),
    )


# Forward reference
from app.models.startup import Startup
