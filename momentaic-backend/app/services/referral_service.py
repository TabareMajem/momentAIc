"""
Referral Service - Viral Growth Engine
Tracks referral codes and manages viral unlock mechanics.
"""

from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel
import structlog
import secrets
import string

logger = structlog.get_logger()


class ReferralCode(BaseModel):
    """Referral code details."""
    code: str
    user_id: str
    created_at: datetime
    referral_count: int = 0
    unlocked: bool = False


class ReferralStats(BaseModel):
    """User's referral statistics."""
    user_id: str
    code: str
    total_referrals: int
    successful_signups: int
    unlocked_features: List[str]
    earnings: float = 0.0


class ReferralService:
    """
    Manages the viral referral system.
    
    Mechanics:
    - Each user gets a unique referral code
    - 3 successful referrals = unlock premium features
    - Alternative unlock: Tweet with #MomentAIcRoast
    """
    
    UNLOCK_THRESHOLD = 3  # Referrals needed to unlock
    UNLOCK_FEATURES = [
        "full_roast_report",
        "ai_strategy_session",
        "priority_support"
    ]
    
    def __init__(self):
        # In production, this would be backed by database
        self._codes: Dict[str, ReferralCode] = {}
        self._user_to_code: Dict[str, str] = {}
        self._referral_chain: Dict[str, str] = {}  # new_user -> referrer_code
    
    def generate_code(self, user_id: str) -> str:
        """
        Generate a unique referral code for a user.
        
        Args:
            user_id: The user's ID
        
        Returns:
            Unique referral code
        """
        if user_id in self._user_to_code:
            return self._user_to_code[user_id]
        
        # Generate 8-character alphanumeric code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        self._codes[code] = ReferralCode(
            code=code,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        self._user_to_code[user_id] = code
        
        logger.info("Referral code generated", user_id=user_id, code=code)
        return code
    
    def track_referral(self, code: str, new_user_id: str) -> int:
        """
        Track a successful referral.
        
        Args:
            code: The referral code used
            new_user_id: The new user who signed up
        
        Returns:
            Current referral count for the referrer
        """
        if code not in self._codes:
            logger.warning("Invalid referral code", code=code)
            return 0
        
        # Check for self-referral
        if self._codes[code].user_id == new_user_id:
            logger.warning("Self-referral attempted", user_id=new_user_id)
            return self._codes[code].referral_count
        
        # Track the referral
        self._codes[code].referral_count += 1
        self._referral_chain[new_user_id] = code
        
        count = self._codes[code].referral_count
        
        # Check for unlock
        if count >= self.UNLOCK_THRESHOLD and not self._codes[code].unlocked:
            self._codes[code].unlocked = True
            logger.info(
                "Referral unlock achieved!",
                user_id=self._codes[code].user_id,
                count=count
            )
        
        logger.info(
            "Referral tracked",
            code=code,
            new_user=new_user_id,
            total=count
        )
        
        return count
    
    def check_unlock(self, user_id: str) -> bool:
        """
        Check if a user has unlocked premium features.
        
        Args:
            user_id: The user's ID
        
        Returns:
            True if unlocked, False otherwise
        """
        if user_id not in self._user_to_code:
            return False
        
        code = self._user_to_code[user_id]
        return self._codes[code].unlocked
    
    def unlock_via_tweet(self, user_id: str, tweet_id: str) -> bool:
        """
        Unlock features via verified tweet.
        
        Args:
            user_id: The user's ID
            tweet_id: The tweet ID to verify
        
        Returns:
            True if successfully unlocked
        """
        # In production, verify tweet via Twitter API
        # Check for #MomentAIcRoast hashtag
        
        if user_id not in self._user_to_code:
            code = self.generate_code(user_id)
        else:
            code = self._user_to_code[user_id]
        
        self._codes[code].unlocked = True
        
        logger.info(
            "Twitter unlock achieved",
            user_id=user_id,
            tweet_id=tweet_id
        )
        
        return True
    
    def get_stats(self, user_id: str) -> Optional[ReferralStats]:
        """
        Get referral statistics for a user.
        
        Args:
            user_id: The user's ID
        
        Returns:
            ReferralStats or None if user has no code
        """
        if user_id not in self._user_to_code:
            return None
        
        code = self._user_to_code[user_id]
        ref_code = self._codes[code]
        
        unlocked_features = self.UNLOCK_FEATURES if ref_code.unlocked else []
        
        return ReferralStats(
            user_id=user_id,
            code=code,
            total_referrals=ref_code.referral_count,
            successful_signups=ref_code.referral_count,
            unlocked_features=unlocked_features
        )
    
    def get_referrer(self, user_id: str) -> Optional[str]:
        """
        Get the referrer's user ID for a given user.
        
        Args:
            user_id: The referred user's ID
        
        Returns:
            Referrer's user ID or None
        """
        if user_id not in self._referral_chain:
            return None
        
        code = self._referral_chain[user_id]
        return self._codes[code].user_id if code in self._codes else None


# Singleton instance
referral_service = ReferralService()
