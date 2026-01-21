"""
Billing Endpoints
Stripe integration, credit management, and subscriptions
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import stripe
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.user import User, UserTier, CreditTransaction
from app.schemas.auth import CreditTransactionResponse, CreditBalanceResponse
from pydantic import BaseModel

logger = structlog.get_logger()
router = APIRouter()

# Initialize Stripe
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


# ==================
# Schemas
# ==================

class CreateCheckoutSessionRequest(BaseModel):
    """Create checkout session request"""
    tier: str  # starter, growth, god_mode
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """Checkout session response"""
    session_id: str
    url: str


class CreatePortalSessionRequest(BaseModel):
    """Create customer portal session"""
    return_url: str


class PortalSessionResponse(BaseModel):
    """Portal session response"""
    url: str


class TopUpCreditsRequest(BaseModel):
    """Manual credit top-up request"""
    amount: int
    reason: str = "Manual top-up"


class SubscriptionResponse(BaseModel):
    """Subscription details"""
    tier: UserTier
    status: str
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False


class TierInfo(BaseModel):
    """Subscription tier information"""
    id: str
    name: str
    price: float
    currency: str = "USD"
    interval: str = "month"
    credits: int
    features: List[str]
    stripe_price_id: Optional[str] = None


class TiersResponse(BaseModel):
    """All available tiers"""
    tiers: List[TierInfo]


# ==================
# Public Endpoints
# ==================

@router.get("/tiers", response_model=TiersResponse)
async def get_tiers():
    """
    Get all available subscription tiers.
    Public endpoint - no authentication required.
    """
    tiers = [
        TierInfo(
            id="starter",
            name="Starter",
            price=9.0,
            credits=settings.default_starter_credits,
            features=[
                "100 AI credits/month",
                "Basic Agent Access",
                "Email Support",
                "1 Startup Profile",
            ],
            stripe_price_id=settings.stripe_starter_price_id,
        ),
        TierInfo(
            id="growth",
            name="Growth",
            price=19.0,
            credits=settings.default_growth_credits,
            features=[
                "500 AI credits/month",
                "Full Agent Swarm Access",
                "Hunter Sales Automation",
                "Priority Support",
                "5 Startup Profiles",
                "Content Scheduling",
            ],
            stripe_price_id=settings.stripe_growth_price_id,
        ),
        TierInfo(
            id="god_mode",
            name="God Mode",
            price=39.0,
            credits=settings.default_god_mode_credits,
            features=[
                "2000 AI credits/month",
                "Unlimited Agent Access",
                "White-glove Onboarding",
                "Custom Integrations",
                "Unlimited Startups",
                "API Access",
                "Dedicated Success Manager",
            ],
            stripe_price_id=settings.stripe_god_mode_price_id,
        ),
    ]
    
    return TiersResponse(tiers=tiers)


# ==================
# Credit Management
# ==================

@router.get("/credits", response_model=CreditBalanceResponse)
async def get_credits(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current credit balance.
    """
    tier_credits = {
        UserTier.STARTER: settings.default_starter_credits,
        UserTier.GROWTH: settings.default_growth_credits,
        UserTier.GOD_MODE: settings.default_god_mode_credits,
    }
    
    
    # [PHASE 25 FIX] Calculate actual usage this month
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    result = await db.execute(
        select(func.sum(CreditTransaction.amount))
        .where(
            CreditTransaction.user_id == current_user.id,
            CreditTransaction.amount < 0, # Debits are usage
            CreditTransaction.created_at >= first_day_of_month
        )
    )
    usage = result.scalar() or 0
    usage_this_month = abs(usage)
    
    return CreditBalanceResponse(
        balance=current_user.credits_balance,
        tier=current_user.tier,
        tier_monthly_credits=tier_credits.get(current_user.tier, 50),
        usage_this_month=usage_this_month,
    )


@router.get("/credits/history", response_model=List[CreditTransactionResponse])
async def get_credit_history(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get credit transaction history.
    """
    result = await db.execute(
        select(CreditTransaction)
        .where(CreditTransaction.user_id == current_user.id)
        .order_by(CreditTransaction.created_at.desc())
        .limit(limit)
    )
    transactions = result.scalars().all()
    
    return [CreditTransactionResponse.model_validate(t) for t in transactions]


@router.post("/credits/topup", response_model=CreditBalanceResponse)
async def topup_credits(
    topup_request: TopUpCreditsRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually top up credits (for testing/admin).
    
    In production, this should be admin-only.
    """
    if topup_request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    # Add credits
    current_user.credits_balance += topup_request.amount
    
    # Log transaction
    transaction = CreditTransaction(
        user_id=current_user.id,
        amount=topup_request.amount,
        balance_after=current_user.credits_balance,
        transaction_type="topup",
        reason=topup_request.reason,
    )
    db.add(transaction)
    
    logger.info(
        "Credits topped up",
        user_id=str(current_user.id),
        amount=topup_request.amount,
        new_balance=current_user.credits_balance,
    )
    
    tier_credits = {
        UserTier.STARTER: settings.default_starter_credits,
        UserTier.GROWTH: settings.default_growth_credits,
        UserTier.GOD_MODE: settings.default_god_mode_credits,
    }
    
    return CreditBalanceResponse(
        balance=current_user.credits_balance,
        tier=current_user.tier,
        tier_monthly_credits=tier_credits.get(current_user.tier, 50),
        usage_this_month=0,
    )


# ==================
# Stripe Integration
# ==================

@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current subscription details.
    """
    response = SubscriptionResponse(
        tier=current_user.tier,
        status="active" if current_user.stripe_subscription_id else "free",
    )
    
    if current_user.stripe_subscription_id and settings.stripe_secret_key:
        try:
            subscription = stripe.Subscription.retrieve(
                current_user.stripe_subscription_id
            )
            response.status = subscription.status
            response.current_period_end = datetime.fromtimestamp(
                subscription.current_period_end
            )
            response.cancel_at_period_end = subscription.cancel_at_period_end
        except stripe.error.StripeError as e:
            logger.error("Stripe subscription fetch error", error=str(e))
    
    return response


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    checkout_request: CreateCheckoutSessionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Stripe Checkout session for subscription.
    """
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured"
        )
    
    # Map tier to price ID
    price_map = {
        "starter": settings.stripe_starter_price_id,
        "growth": settings.stripe_growth_price_id,
        "god_mode": settings.stripe_god_mode_price_id,
    }
    
    price_id = price_map.get(checkout_request.tier)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {checkout_request.tier}"
        )
    
    # Create or get Stripe customer
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.full_name,
            metadata={"user_id": str(current_user.id)},
        )
        current_user.stripe_customer_id = customer.id
    
    try:
        session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=checkout_request.success_url,
            cancel_url=checkout_request.cancel_url,
            metadata={
                "user_id": str(current_user.id),
                "tier": checkout_request.tier,
            },
        )
        
        return CheckoutSessionResponse(
            session_id=session.id,
            url=session.url,
        )
        
    except stripe.error.StripeError as e:
        logger.error("Stripe checkout error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/checkout/founders-club", response_model=CheckoutSessionResponse)
async def create_founders_club_checkout(
    success_url: str,
    cancel_url: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create checkout session for "Founders Club" ($350 Lifetime).
    """
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured"
        )
        
    # Fixed price ID for Founders Club (configured in env)
    # If not set, use a fallback or error
    price_id = getattr(settings, "stripe_founders_club_price_id", "price_founders_club_test")
    
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.full_name,
            metadata={"user_id": str(current_user.id)},
        )
        current_user.stripe_customer_id = customer.id
        
    try:
        session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment", # One-time payment
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(current_user.id),
                "type": "founders_club_presale",
            },
        )
        
        logger.info("Created Founders Club checkout session", user_id=str(current_user.id))
        
        return CheckoutSessionResponse(
            session_id=session.id,
            url=session.url,
        )
        
    except stripe.error.StripeError as e:
        logger.error("Founders Club checkout error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )
@router.post("/portal", response_model=PortalSessionResponse)
async def create_portal_session(
    portal_request: CreatePortalSessionRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a Stripe Customer Portal session.
    """
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured"
        )
    
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer found"
        )
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=portal_request.return_url,
        )
        
        return PortalSessionResponse(url=session.url)
        
    except stripe.error.StripeError as e:
        logger.error("Stripe portal error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Stripe webhook events.
    """
    if not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured"
        )
    
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    logger.info("Stripe webhook received", event_type=event.type)
    
    # Handle events
    if event.type == "checkout.session.completed":
        session = event.data.object
        await handle_checkout_completed(session, db)
    
    elif event.type == "customer.subscription.updated":
        subscription = event.data.object
        await handle_subscription_updated(subscription, db)
    
    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        await handle_subscription_deleted(subscription, db)
    
    elif event.type == "invoice.payment_succeeded":
        invoice = event.data.object
        await handle_payment_succeeded(invoice, db)
    
    return {"status": "ok"}


async def handle_checkout_completed(session: dict, db: AsyncSession):
    """Handle successful checkout"""
    user_id = session.get("metadata", {}).get("user_id")
    tier = session.get("metadata", {}).get("tier")
    subscription_id = session.get("subscription")
    
    if not user_id:
        logger.warning("Checkout completed without user_id")
        return
    
    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.stripe_subscription_id = subscription_id
        
        # Update tier
        tier_map = {
            "starter": UserTier.STARTER,
            "growth": UserTier.GROWTH,
            "god_mode": UserTier.GOD_MODE,
        }
        if tier in tier_map:
            user.tier = tier_map[tier]
        
        # Add credits based on tier
        credits_map = {
            UserTier.STARTER: settings.default_starter_credits,
            UserTier.GROWTH: settings.default_growth_credits,
            UserTier.GOD_MODE: settings.default_god_mode_credits,
        }
        credits_to_add = credits_map.get(user.tier, 50)
        user.credits_balance += credits_to_add
        
        # Log transaction
        transaction = CreditTransaction(
            user_id=user.id,
            amount=credits_to_add,
            balance_after=user.credits_balance,
            transaction_type="topup",
            reason=f"Subscription upgrade to {user.tier.value}",
            metadata={"subscription_id": subscription_id},
        )
        db.add(transaction)
        
        logger.info(
            "Checkout completed",
            user_id=user_id,
            tier=tier,
            credits_added=credits_to_add,
        )


async def handle_subscription_updated(subscription: dict, db: AsyncSession):
    """Handle subscription update"""
    result = await db.execute(
        select(User).where(User.stripe_subscription_id == subscription.id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        if subscription.status == "canceled":
            user.tier = UserTier.STARTER
        
        logger.info(
            "Subscription updated",
            user_id=str(user.id),
            status=subscription.status,
        )


async def handle_subscription_deleted(subscription: dict, db: AsyncSession):
    """Handle subscription deletion"""
    result = await db.execute(
        select(User).where(User.stripe_subscription_id == subscription.id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.tier = UserTier.STARTER
        user.stripe_subscription_id = None
        
        logger.info("Subscription deleted", user_id=str(user.id))


async def handle_payment_succeeded(invoice: dict, db: AsyncSession):
    """Handle successful payment (monthly renewal)"""
    subscription_id = invoice.get("subscription")
    
    if not subscription_id:
        return
    
    result = await db.execute(
        select(User).where(User.stripe_subscription_id == subscription_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Add monthly credits
        credits_map = {
            UserTier.STARTER: settings.default_starter_credits,
            UserTier.GROWTH: settings.default_growth_credits,
            UserTier.GOD_MODE: settings.default_god_mode_credits,
        }
        credits_to_add = credits_map.get(user.tier, 50)
        user.credits_balance += credits_to_add
        
        transaction = CreditTransaction(
            user_id=user.id,
            amount=credits_to_add,
            balance_after=user.credits_balance,
            transaction_type="topup",
            reason=f"Monthly {user.tier.value} renewal",
            metadata={"invoice_id": invoice.get("id")},
        )
        db.add(transaction)
        
        logger.info(
            "Payment succeeded, credits added",
            user_id=str(user.id),
            credits=credits_to_add,
        )
