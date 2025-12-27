"""
Referral System Models
Database models for viral referral tracking
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


def generate_referral_code():
    """Generate a unique referral code"""
    return uuid.uuid4().hex[:8].upper()


class Referral(Base):
    """Referral tracking model"""
    __tablename__ = "referrals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Referrer (the user who shared)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    referrer_code = Column(String(16), unique=True, nullable=False, default=generate_referral_code)
    
    # Referred user (who signed up)
    referred_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    referred_email = Column(String(255), nullable=True)
    
    # Tracking
    status = Column(String(20), default="pending")  # pending, signed_up, converted, rewarded
    source = Column(String(50), nullable=True)  # twitter, linkedin, email, direct
    
    # Rewards
    referrer_reward_credits = Column(Integer, default=0)
    referred_reward_credits = Column(Integer, default=0)
    reward_claimed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    signed_up_at = Column(DateTime, nullable=True)
    converted_at = Column(DateTime, nullable=True)
    
    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_id], backref="referrals_made")
    referred = relationship("User", foreign_keys=[referred_id], backref="referred_by")


class ReferralStats(Base):
    """Aggregated referral stats per user"""
    __tablename__ = "referral_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Stats
    total_referrals = Column(Integer, default=0)
    successful_signups = Column(Integer, default=0)
    converted_users = Column(Integer, default=0)
    total_credits_earned = Column(Integer, default=0)
    
    # Milestones
    milestone_5_reached = Column(Boolean, default=False)
    milestone_10_reached = Column(Boolean, default=False)
    milestone_25_reached = Column(Boolean, default=False)
    milestone_50_reached = Column(Boolean, default=False)
    milestone_100_reached = Column(Boolean, default=False)
    
    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="referral_stats")


class ReferralReward(Base):
    """Reward tiers and milestones"""
    __tablename__ = "referral_rewards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Requirements
    referrals_required = Column(Integer, nullable=False)
    
    # Rewards
    credits_reward = Column(Integer, default=0)
    badge_name = Column(String(50), nullable=True)
    special_feature = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
