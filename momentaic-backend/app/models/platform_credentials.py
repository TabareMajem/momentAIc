"""
Platform Credentials Model
Encrypted storage for user platform login credentials (Twitter, HubSpot, etc.)
Used by the Browser Agent to log into platforms on behalf of users.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, DateTime, Text, Boolean,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base


class PlatformType(str, enum.Enum):
    """Supported platforms for browser-based automation"""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    HUBSPOT = "hubspot"
    FACEBOOK = "facebook"
    REDDIT = "reddit"
    DISCORD = "discord"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    ATTIO = "attio"
    NOTION = "notion"
    CUSTOM = "custom"


class CredentialStatus(str, enum.Enum):
    """Status of stored credentials"""
    ACTIVE = "active"
    EXPIRED = "expired"
    TWO_FA_REQUIRED = "2fa_required"
    LOGIN_FAILED = "login_failed"
    PENDING = "pending"


class PlatformCredential(Base):
    """
    Encrypted platform credentials for browser-based automation.
    When a user provides their Twitter/LinkedIn/etc credentials,
    the Browser Agent can log in and execute actions on their behalf.
    """
    __tablename__ = "platform_credentials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    startup_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="SET NULL"), nullable=True
    )

    # Platform identification
    platform: Mapped[PlatformType] = mapped_column(
        SQLEnum(PlatformType), nullable=False
    )
    
    # Encrypted credentials (Fernet encryption)
    username: Mapped[str] = mapped_column(String(500), nullable=False)  # email or username
    encrypted_password: Mapped[str] = mapped_column(Text, nullable=False)  # Fernet encrypted
    
    # Browser session persistence (Playwright storage state JSON)
    session_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Status tracking
    status: Mapped[CredentialStatus] = mapped_column(
        SQLEnum(CredentialStatus), default=CredentialStatus.PENDING, nullable=False
    )
    
    # Metadata
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_action_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    login_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User")

    __table_args__ = (
        Index("ix_platform_creds_user_platform", "user_id", "platform", unique=True),
        Index("ix_platform_creds_status", "status"),
    )

    def __repr__(self):
        return f"<PlatformCredential {self.platform.value} for user {self.user_id}>"
