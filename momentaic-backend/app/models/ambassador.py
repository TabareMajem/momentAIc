"""
Ambassador Program Models
Database models for ambassador tracking, conversions, and payouts
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid
import enum

from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


def generate_ambassador_code():
    """Generate unique ambassador code like AMBX-A1B2C3"""
    return f"AMBX-{uuid.uuid4().hex[:6].upper()}"


class AmbassadorTier(str, enum.Enum):
    """Ambassador tiers based on follower count"""
    MICRO = "micro"      # <10k followers, 20% commission
    MID = "mid"          # 10k-100k followers, 25% commission
    MACRO = "macro"      # >100k followers, 30% commission


class AmbassadorStatus(str, enum.Enum):
    """Ambassador application/account status"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class ConversionStatus(str, enum.Enum):
    """Conversion payment status"""
    PENDING = "pending"          # User signed up but not paid
    CLEARED = "cleared"          # Payment cleared, commission available
    PAID = "paid"                # Commission paid out
    REFUNDED = "refunded"        # User refunded, commission reversed
    CHARGEBACKED = "chargebacked"  # Chargeback occurred


class PayoutStatus(str, enum.Enum):
    """Payout status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Commission rates by tier
COMMISSION_RATES = {
    AmbassadorTier.MICRO: 0.20,   # 20%
    AmbassadorTier.MID: 0.25,     # 25%
    AmbassadorTier.MACRO: 0.30,   # 30%
}


class Ambassador(Base):
    """Ambassador profile and tracking"""
    __tablename__ = "ambassadors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Profile
    display_name = Column(String(100), nullable=False)
    bio = Column(String(500), nullable=True)
    
    # Social presence
    social_platform = Column(String(50), nullable=False)  # twitter, linkedin, instagram, youtube, tiktok
    social_username = Column(String(100), nullable=False)
    social_url = Column(String(255), nullable=True)
    follower_count = Column(Integer, default=0)
    
    # Tier and commission
    tier = Column(SQLEnum(AmbassadorTier), default=AmbassadorTier.MICRO)
    commission_rate = Column(Float, default=0.20)
    
    # Referral tracking
    referral_code = Column(String(16), unique=True, nullable=False, default=generate_ambassador_code)
    
    # Stripe Connect
    stripe_connect_id = Column(String(100), nullable=True)  # acct_xxxxx
    stripe_onboarding_complete = Column(Boolean, default=False)
    stripe_payouts_enabled = Column(Boolean, default=False)
    
    # Earnings
    total_earnings = Column(Float, default=0.0)       # Lifetime earnings
    pending_balance = Column(Float, default=0.0)     # In chargeback hold period
    available_balance = Column(Float, default=0.0)   # Ready for payout
    total_paid_out = Column(Float, default=0.0)      # Already paid
    
    # Stats
    total_clicks = Column(Integer, default=0)
    total_signups = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)  # Paid subscriptions
    
    # Status
    status = Column(SQLEnum(AmbassadorStatus), default=AmbassadorStatus.PENDING)
    rejection_reason = Column(String(500), nullable=True)
    
    # Application info
    application_reason = Column(String(1000), nullable=True)  # Why they want to be ambassador
    promotion_plan = Column(String(1000), nullable=True)      # How they plan to promote
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="ambassador_profile")
    conversions = relationship("AmbassadorConversion", back_populates="ambassador")
    payouts = relationship("AmbassadorPayout", back_populates="ambassador")
    
    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate (conversions / signups)"""
        if self.total_signups == 0:
            return 0.0
        return (self.total_conversions / self.total_signups) * 100
    
    @classmethod
    def determine_tier(cls, follower_count: int) -> AmbassadorTier:
        """Determine tier based on follower count"""
        if follower_count >= 100000:
            return AmbassadorTier.MACRO
        elif follower_count >= 10000:
            return AmbassadorTier.MID
        else:
            return AmbassadorTier.MICRO
    
    @classmethod
    def get_commission_rate(cls, tier: AmbassadorTier) -> float:
        """Get commission rate for tier"""
        return COMMISSION_RATES.get(tier, 0.20)


class AmbassadorConversion(Base):
    """Track ambassador referral conversions"""
    __tablename__ = "ambassador_conversions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ambassador_id = Column(UUID(as_uuid=True), ForeignKey("ambassadors.id"), nullable=False)
    referred_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Transaction details
    subscription_plan = Column(String(50), nullable=True)  # starter, growth, founder
    subscription_amount = Column(Float, default=0.0)       # Amount paid by user
    commission_amount = Column(Float, default=0.0)         # Ambassador's cut
    
    # Stripe references
    stripe_payment_id = Column(String(100), nullable=True)      # pi_xxxxx
    stripe_subscription_id = Column(String(100), nullable=True) # sub_xxxxx
    
    # Status tracking
    status = Column(SQLEnum(ConversionStatus), default=ConversionStatus.PENDING)
    
    # Chargeback protection
    chargeback_hold_until = Column(DateTime, nullable=True)  # 30 days after payment
    cleared_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ambassador = relationship("Ambassador", back_populates="conversions")
    referred_user = relationship("User", foreign_keys=[referred_user_id])
    
    def calculate_commission(self, amount: float, rate: float) -> float:
        """Calculate commission from subscription amount"""
        return round(amount * rate, 2)
    
    def set_chargeback_hold(self, days: int = 30):
        """Set chargeback hold period"""
        self.chargeback_hold_until = datetime.utcnow() + timedelta(days=days)


class AmbassadorPayout(Base):
    """Track ambassador payouts"""
    __tablename__ = "ambassador_payouts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ambassador_id = Column(UUID(as_uuid=True), ForeignKey("ambassadors.id"), nullable=False)
    
    # Payout details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Stripe Connect transfer
    stripe_transfer_id = Column(String(100), nullable=True)  # tr_xxxxx
    stripe_payout_id = Column(String(100), nullable=True)    # po_xxxxx
    
    # Status
    status = Column(SQLEnum(PayoutStatus), default=PayoutStatus.PENDING)
    failure_reason = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    ambassador = relationship("Ambassador", back_populates="payouts")


class AmbassadorClick(Base):
    """Track referral link clicks for analytics"""
    __tablename__ = "ambassador_clicks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ambassador_id = Column(UUID(as_uuid=True), ForeignKey("ambassadors.id"), nullable=False)
    
    # Click metadata
    source = Column(String(50), nullable=True)    # twitter, linkedin, email, etc.
    campaign = Column(String(100), nullable=True) # Optional campaign tag
    ip_hash = Column(String(64), nullable=True)   # Hashed IP for dedup
    user_agent = Column(String(255), nullable=True)
    referrer = Column(String(255), nullable=True)
    
    # Conversion tracking
    converted = Column(Boolean, default=False)
    conversion_id = Column(String(36), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
