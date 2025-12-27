"""
Integration Models
Database models for connecting external services
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


class IntegrationProvider(str, enum.Enum):
    """Supported integration providers"""
    # Analytics & Data
    STRIPE = "stripe"
    GOOGLE_ANALYTICS = "google_analytics"
    MIXPANEL = "mixpanel"
    AMPLITUDE = "amplitude"
    
    # Development
    GITHUB = "github"
    GITLAB = "gitlab"
    LINEAR = "linear"
    JIRA = "jira"
    
    # Communication
    SLACK = "slack"
    DISCORD = "discord"
    EMAIL_SMTP = "email_smtp"
    SENDGRID = "sendgrid"
    
    # CRM
    HUBSPOT = "hubspot"
    PIPEDRIVE = "pipedrive"
    SALESFORCE = "salesforce"
    
    # Social
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    
    # Productivity
    NOTION = "notion"
    AIRTABLE = "airtable"
    GOOGLE_SHEETS = "google_sheets"
    CALENDLY = "calendly"
    
    # Custom
    WEBHOOK = "webhook"
    API = "api"


class IntegrationStatus(str, enum.Enum):
    """Integration connection status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    ERROR = "error"
    PENDING = "pending"
    DISCONNECTED = "disconnected"


class Integration(Base):
    """Connected external service"""
    __tablename__ = "integrations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    
    # Provider info
    provider: Mapped[IntegrationProvider] = mapped_column(
        SQLEnum(IntegrationProvider), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)  # User-friendly name
    
    # OAuth tokens (encrypted in production)
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # For API key based integrations
    api_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_secret: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Configuration
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"workspace_id": "...", "channel": "#general"}
    
    # Scopes granted
    scopes: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Status
    status: Mapped[IntegrationStatus] = mapped_column(
        SQLEnum(IntegrationStatus), default=IntegrationStatus.PENDING
    )
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    data_points: Mapped[List["IntegrationData"]] = relationship(
        "IntegrationData", back_populates="integration", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_integrations_startup", "startup_id"),
        Index("ix_integrations_provider", "provider"),
        Index("ix_integrations_status", "status"),
    )


class DataCategory(str, enum.Enum):
    """Categories of synced data"""
    REVENUE = "revenue"
    CUSTOMERS = "customers"
    LEADS = "leads"
    COMMITS = "commits"
    ISSUES = "issues"
    MESSAGES = "messages"
    EVENTS = "events"
    METRICS = "metrics"
    CONTENT = "content"
    CUSTOM = "custom"


class IntegrationData(Base):
    """Synced data from integrations"""
    __tablename__ = "integration_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    integration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    
    # Data classification
    category: Mapped[DataCategory] = mapped_column(
        SQLEnum(DataCategory), nullable=False
    )
    data_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # Examples: "mrr", "dau", "commit_count", "lead_count"
    
    # The actual data
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"value": 10000, "currency": "USD", "period": "monthly"}
    
    # For time-series data
    metric_value: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    metric_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Sync info
    external_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    integration: Mapped["Integration"] = relationship("Integration", back_populates="data_points")

    __table_args__ = (
        Index("ix_integration_data_startup", "startup_id"),
        Index("ix_integration_data_category", "category"),
        Index("ix_integration_data_type", "data_type"),
        Index("ix_integration_data_date", "metric_date"),
    )
