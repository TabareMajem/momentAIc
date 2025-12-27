"""
User and Authentication Models
Multi-tenant user management with credit system
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, 
    ForeignKey, Enum as SQLEnum, Index, JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base


class UserTier(str, enum.Enum):
    """User subscription tiers"""
    STARTER = "starter"
    GROWTH = "growth"
    GOD_MODE = "god_mode"


class User(Base):
    """User model with credit-based billing"""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Subscription & Credits
    tier: Mapped[UserTier] = mapped_column(
        SQLEnum(UserTier), default=UserTier.STARTER, nullable=False
    )
    credits_balance: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # OAuth tokens (encrypted)
    github_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    linkedin_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gmail_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Preferences
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    startups: Mapped[List["Startup"]] = relationship(
        "Startup", back_populates="owner", cascade="all, delete-orphan"
    )
    credit_transactions: Mapped[List["CreditTransaction"]] = relationship(
        "CreditTransaction", back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


class RefreshToken(Base):
    """Refresh token storage for JWT auth"""
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class CreditTransaction(Base):
    """Audit log for credit transactions"""
    __tablename__ = "credit_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # Negative for deductions
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'deduction', 'topup', 'refund'
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    transaction_meta: Mapped[dict] = mapped_column(JSONB, default=dict)  # Renamed from 'metadata' (reserved)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="credit_transactions")

    __table_args__ = (
        Index("ix_credit_transactions_user_created", "user_id", "created_at"),
    )


# Forward reference for Startup model
from app.models.startup import Startup
