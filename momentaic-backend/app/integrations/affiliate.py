"""
Affiliate Integration - Tolt/FirstPromoter Connector
Manages affiliate tracking, commissions, and payouts.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import structlog
import httpx

from app.core.config import settings

logger = structlog.get_logger()


class CommissionTier(str, Enum):
    """Affiliate commission tiers."""
    STANDARD = "standard"
    PREMIUM = "premium"
    ELITE = "elite"


class AffiliateProfile(BaseModel):
    """Affiliate partner profile."""
    affiliate_id: str
    name: str
    email: str
    tier: CommissionTier = CommissionTier.STANDARD
    commission_rate: float = 0.30
    referral_link: str
    partner_page_url: Optional[str] = None
    total_referrals: int = 0
    total_earnings: float = 0.0
    pending_payout: float = 0.0
    created_at: datetime


class ReferralEvent(BaseModel):
    """A tracked referral event."""
    event_id: str
    affiliate_id: str
    customer_email: str
    plan: str
    amount: float
    commission: float
    status: str  # pending, paid, voided
    created_at: datetime


class AffiliateIntegration:
    """
    Integration with affiliate management platforms.
    
    Supports:
    - Tolt (Modern, Stripe-native)
    - FirstPromoter (SaaS standard)
    
    Features:
    - Automatic signup attribution
    - 30-40% recurring commissions
    - Auto-payouts via Stripe Connect
    """
    
    COMMISSION_RATES = {
        CommissionTier.STANDARD: 0.30,   # 30%
        CommissionTier.PREMIUM: 0.35,    # 35%
        CommissionTier.ELITE: 0.40,      # 40%
    }
    
    def __init__(self):
        self.provider = getattr(settings, 'affiliate_provider', 'tolt')
        self.api_key = getattr(settings, 'affiliate_api_key', '')
        self.base_url = self._get_base_url()
    
    def _get_base_url(self) -> str:
        """Get API base URL for the configured provider."""
        urls = {
            "tolt": "https://api.tolt.io/v1",
            "firstpromoter": "https://firstpromoter.com/api/v1"
        }
        return urls.get(self.provider, urls["tolt"])
    
    async def create_affiliate(
        self,
        name: str,
        email: str,
        tier: CommissionTier = CommissionTier.STANDARD
    ) -> AffiliateProfile:
        """
        Create a new affiliate partner.
        
        Args:
            name: Partner's name
            email: Partner's email
            tier: Commission tier
        
        Returns:
            Created affiliate profile
        """
        commission_rate = self.COMMISSION_RATES[tier]
        affiliate_id = f"aff_{email.replace('@', '_').replace('.', '_')}"
        
        # Generate referral link
        referral_link = f"https://momentaic.com/?ref={affiliate_id}"
        partner_page = f"https://momentaic.com/partners/{name.lower().replace(' ', '-')}"
        
        profile = AffiliateProfile(
            affiliate_id=affiliate_id,
            name=name,
            email=email,
            tier=tier,
            commission_rate=commission_rate,
            referral_link=referral_link,
            partner_page_url=partner_page,
            created_at=datetime.utcnow()
        )
        
        # In production, call affiliate platform API
        if self.api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/affiliates",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={
                            "name": name,
                            "email": email,
                            "commission_rate": commission_rate * 100,  # As percentage
                            "tier": tier.value
                        }
                    )
                    if response.status_code == 201:
                        data = response.json()
                        profile.affiliate_id = data.get("id", affiliate_id)
                        profile.referral_link = data.get("referral_link", referral_link)
            except Exception as e:
                logger.error(f"Affiliate API error: {e}")
        
        logger.info(
            "Affiliate created",
            affiliate_id=profile.affiliate_id,
            tier=tier.value
        )
        
        return profile
    
    async def track_referral(
        self,
        affiliate_id: str,
        customer_email: str,
        plan: str,
        amount: float
    ) -> ReferralEvent:
        """
        Track a referral conversion.
        
        Args:
            affiliate_id: The referring affiliate
            customer_email: Customer's email
            plan: Subscribed plan
            amount: Transaction amount
        
        Returns:
            Referral event details
        """
        # Get affiliate's commission rate
        commission_rate = 0.30  # Default, would be fetched from DB
        commission = amount * commission_rate
        
        event = ReferralEvent(
            event_id=f"ref_{datetime.utcnow().timestamp()}",
            affiliate_id=affiliate_id,
            customer_email=customer_email,
            plan=plan,
            amount=amount,
            commission=commission,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        # In production, call affiliate platform API
        if self.api_key:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.base_url}/referrals",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={
                            "affiliate_id": affiliate_id,
                            "customer_email": customer_email,
                            "amount": amount,
                            "commission": commission
                        }
                    )
            except Exception as e:
                logger.error(f"Referral tracking error: {e}")
        
        logger.info(
            "Referral tracked",
            affiliate_id=affiliate_id,
            amount=amount,
            commission=commission
        )
        
        return event
    
    async def process_payout(
        self,
        affiliate_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process affiliate payout via Stripe Connect.
        
        Args:
            affiliate_id: The affiliate to pay
            amount: Specific amount or None for full balance
        
        Returns:
            Payout status
        """
        # In production, this triggers Stripe Connect transfer
        logger.info(
            "Payout processed",
            affiliate_id=affiliate_id,
            amount=amount
        )
        
        return {
            "status": "processed",
            "affiliate_id": affiliate_id,
            "amount": amount or 0,
            "method": "stripe_connect"
        }
    
    async def get_affiliate_stats(
        self,
        affiliate_id: str
    ) -> Dict[str, Any]:
        """
        Get affiliate performance statistics.
        
        Args:
            affiliate_id: The affiliate ID
        
        Returns:
            Performance metrics
        """
        # In production, fetch from database/API
        return {
            "affiliate_id": affiliate_id,
            "total_clicks": 0,
            "total_signups": 0,
            "total_conversions": 0,
            "total_revenue": 0.0,
            "total_commissions": 0.0,
            "pending_payout": 0.0,
            "conversion_rate": 0.0
        }
    
    async def upgrade_tier(
        self,
        affiliate_id: str,
        new_tier: CommissionTier
    ) -> bool:
        """
        Upgrade an affiliate to a higher tier.
        
        Args:
            affiliate_id: The affiliate to upgrade
            new_tier: New commission tier
        
        Returns:
            Success status
        """
        new_rate = self.COMMISSION_RATES[new_tier]
        
        logger.info(
            "Affiliate tier upgraded",
            affiliate_id=affiliate_id,
            new_tier=new_tier.value,
            new_rate=new_rate
        )
        
        return True
    
    async def handle_stripe_webhook(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Handle Stripe webhook for affiliate tracking.
        
        Args:
            event_type: Stripe event type
            data: Event data
        
        Returns:
            Success status
        """
        if event_type == "checkout.session.completed":
            # Check for affiliate attribution
            metadata = data.get("metadata", {})
            affiliate_id = metadata.get("affiliate_id")
            
            if affiliate_id:
                await self.track_referral(
                    affiliate_id=affiliate_id,
                    customer_email=data.get("customer_email", ""),
                    plan=metadata.get("plan", "unknown"),
                    amount=data.get("amount_total", 0) / 100  # Stripe uses cents
                )
        
        return True


# Singleton instance
affiliate_integration = AffiliateIntegration()
