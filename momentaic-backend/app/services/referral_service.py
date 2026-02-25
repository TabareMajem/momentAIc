"""
Referral Service - Viral Growth Engine
Tracks referral codes and manages viral unlock mechanics.
Now backed by PostgreSQL via the Referral and ReferralStats models.
"""

from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import structlog
import secrets
import string
import uuid

from app.models.referral import Referral, ReferralStats as ReferralStatsModel

logger = structlog.get_logger()


class ReferralCodeDTO(BaseModel):
    """API-facing referral code details."""
    code: str
    user_id: str
    created_at: datetime
    referral_count: int = 0
    unlocked: bool = False


class ReferralStatsDTO(BaseModel):
    """API-facing referral statistics."""
    user_id: str
    code: str
    total_referrals: int
    successful_signups: int
    unlocked_features: List[str]
    earnings: float = 0.0


class ReferralService:
    """
    Manages the viral referral system.
    All state is persisted to PostgreSQL via the Referral and ReferralStats models.
    
    Mechanics:
    - Each user gets a unique referral code
    - 3 successful referrals = unlock premium features
    - Alternative unlock: Tweet with #MomentAIcRoast
    """
    
    UNLOCK_THRESHOLD = 3
    UNLOCK_FEATURES = [
        "full_roast_report",
        "ai_strategy_session",
        "priority_support"
    ]
    
    @staticmethod
    def _generate_code() -> str:
        """Generate an 8-character alphanumeric referral code."""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    
    async def generate_code(self, user_id: str, db: AsyncSession) -> str:
        """
        Generate or retrieve a unique referral code for a user.
        
        Args:
            user_id: The user's ID  
            db: Database session
        
        Returns:
            Unique referral code string
        """
        # Check for existing code
        result = await db.execute(
            select(Referral).where(
                Referral.referrer_id == uuid.UUID(user_id),
            ).limit(1)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing.referrer_code
        
        # Generate new referral record
        code = self._generate_code()
        referral = Referral(
            referrer_id=uuid.UUID(user_id),
            referrer_code=code,
            status="active",
        )
        db.add(referral)
        
        # Create stats record
        stats = ReferralStatsModel(
            user_id=uuid.UUID(user_id),
        )
        db.add(stats)
        
        await db.flush()
        logger.info("Referral code generated", user_id=user_id, code=code)
        return code
    
    async def track_referral(self, code: str, new_user_id: str, db: AsyncSession) -> int:
        """
        Track a successful referral.
        
        Args:
            code: The referral code used
            new_user_id: The new user who signed up
            db: Database session
        
        Returns:
            Current referral count for the referrer
        """
        # Find the referral by code
        result = await db.execute(
            select(Referral).where(Referral.referrer_code == code)
        )
        referral = result.scalar_one_or_none()
        
        if not referral:
            logger.warning("Invalid referral code", code=code)
            return 0
        
        # Block self-referral
        if str(referral.referrer_id) == new_user_id:
            logger.warning("Self-referral attempted", user_id=new_user_id)
            return 0
        
        # Create a new referral record for the referred user
        new_referral = Referral(
            referrer_id=referral.referrer_id,
            referrer_code=code,
            referred_id=uuid.UUID(new_user_id),
            status="signed_up",
            signed_up_at=datetime.utcnow(),
        )
        # Avoid duplicate unique constraint — update existing instead
        # Actually we'll use the referrer's code and track via referred_id
        referral.referred_id = uuid.UUID(new_user_id)
        referral.status = "signed_up"
        referral.signed_up_at = datetime.utcnow()
        
        # Update stats
        stats_result = await db.execute(
            select(ReferralStatsModel).where(
                ReferralStatsModel.user_id == referral.referrer_id
            )
        )
        stats = stats_result.scalar_one_or_none()
        
        if stats:
            stats.total_referrals += 1
            stats.successful_signups += 1
            count = stats.successful_signups
            
            # Check milestones
            if count >= 5:
                stats.milestone_5_reached = True
            if count >= 10:
                stats.milestone_10_reached = True
            if count >= 25:
                stats.milestone_25_reached = True
        else:
            count = 1
        
        await db.flush()
        
        logger.info("Referral tracked", code=code, new_user=new_user_id, total=count)
        return count
    
    async def check_unlock(self, user_id: str, db: AsyncSession) -> bool:
        """
        Check if a user has unlocked premium features.
        
        Args:
            user_id: The user's ID
            db: Database session
        
        Returns:
            True if user has >= UNLOCK_THRESHOLD successful referrals
        """
        result = await db.execute(
            select(ReferralStatsModel).where(
                ReferralStatsModel.user_id == uuid.UUID(user_id)
            )
        )
        stats = result.scalar_one_or_none()
        
        if not stats:
            return False
        
        return stats.successful_signups >= self.UNLOCK_THRESHOLD
    
    async def get_stats(self, user_id: str, db: AsyncSession) -> Optional[ReferralStatsDTO]:
        """
        Get referral statistics for a user.
        """
        # Get the user's code
        ref_result = await db.execute(
            select(Referral).where(Referral.referrer_id == uuid.UUID(user_id)).limit(1)
        )
        referral = ref_result.scalar_one_or_none()
        
        if not referral:
            return None
        
        # Get stats
        stats_result = await db.execute(
            select(ReferralStatsModel).where(ReferralStatsModel.user_id == uuid.UUID(user_id))
        )
        stats = stats_result.scalar_one_or_none()
        
        unlocked = (stats.successful_signups >= self.UNLOCK_THRESHOLD) if stats else False
        
        return ReferralStatsDTO(
            user_id=user_id,
            code=referral.referrer_code,
            total_referrals=stats.total_referrals if stats else 0,
            successful_signups=stats.successful_signups if stats else 0,
            unlocked_features=self.UNLOCK_FEATURES if unlocked else [],
        )
    
    async def get_referrer(self, user_id: str, db: AsyncSession) -> Optional[str]:
        """
        Get the referrer's user ID for a given user.
        """
        result = await db.execute(
            select(Referral).where(Referral.referred_id == uuid.UUID(user_id))
        )
        referral = result.scalar_one_or_none()
        
        if not referral:
            return None
        return str(referral.referrer_id)


# Singleton instance
referral_service = ReferralService()
