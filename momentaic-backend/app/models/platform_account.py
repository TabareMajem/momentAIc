"""
PlatformAccount Model
Stores user-provided social media credentials (encrypted) for the scraper's
account rotation pool. Credentials are encrypted at rest using Fernet.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class PlatformAccount(Base):
    """
    A social media account provided by the user for scraping.
    Credentials are Fernet-encrypted before storage.
    """
    __tablename__ = "platform_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    startup_id = Column(UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True)

    # Platform identifier
    platform = Column(String(50), nullable=False, index=True)  # instagram, twitter, tiktok
    username = Column(String(255), nullable=False)

    # Encrypted credentials (Fernet)
    encrypted_password = Column(Text, nullable=True)
    encrypted_cookies = Column(Text, nullable=True)

    # Optional dedicated proxy for this account
    proxy_url = Column(String(1024), nullable=True)

    # Status tracking
    status = Column(String(50), default="active")  # active, cooldown, banned
    is_active = Column(Boolean, default=True)
    last_error = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
