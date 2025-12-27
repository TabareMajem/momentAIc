"""
Ambassador Program API Endpoints
Full ambassador management with Stripe Connect integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid
import structlog
import stripe

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.ambassador import Ambassador, AmbassadorConversion, AmbassadorPayout, AmbassadorClick
from app.agents.ambassador_outreach_agent import ambassador_agent
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()


# ============ SCHEMAS ============

class AmbassadorApplicationRequest(BaseModel):
    display_name: str
    social_platform: str  # twitter, linkedin, instagram, youtube, tiktok
    social_username: str
    social_url: Optional[str] = None
    follower_count: int
    application_reason: str
    promotion_plan: Optional[str] = None


class AmbassadorProfileResponse(BaseModel):
    id: str
    display_name: str
    tier: str
    commission_rate: float
    referral_code: str
    referral_url: str
    
    # Stripe Connect
    stripe_connected: bool
    stripe_payouts_enabled: bool
    
    # Stats
    total_clicks: int
    total_signups: int
    total_conversions: int
    conversion_rate: float
    
    # Earnings
    total_earnings: float
    pending_balance: float
    available_balance: float
    total_paid_out: float
    
    status: str
    created_at: datetime


class ConversionResponse(BaseModel):
    id: str
    referred_user_email: str
    subscription_plan: Optional[str]
    subscription_amount: float
    commission_amount: float
    status: str
    created_at: datetime
    cleared_at: Optional[datetime]


class EarningsBreakdownResponse(BaseModel):
    total_earnings: float
    pending_balance: float
    available_balance: float
    total_paid_out: float
    next_payout_eligible: float
    chargeback_hold_amount: float
    monthly_earnings: List[Dict[str, Any]]


class PayoutRequestResponse(BaseModel):
    id: str
    amount: float
    status: str
    estimated_arrival: datetime


class StripeOnboardResponse(BaseModel):
    onboarding_url: str


# ============ HELPERS ============

def _determine_tier(follower_count: int) -> tuple:
    """Determine tier and commission rate"""
    if follower_count >= 100000:
        return "macro", 0.30
    elif follower_count >= 10000:
        return "mid", 0.25
    else:
        return "micro", 0.20


# ============ PUBLIC ENDPOINTS ============

@router.post("/apply", status_code=status.HTTP_201_CREATED)
async def apply_ambassador(
    data: AmbassadorApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply to become an ambassador"""
    # Check if already an ambassador
    existing = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an ambassador application"
        )
    
    # Determine tier based on follower count
    tier, commission_rate = _determine_tier(data.follower_count)
    
    # Generate referral code
    referral_code = f"AMBX-{uuid.uuid4().hex[:6].upper()}"
    
    # Create ambassador
    ambassador = Ambassador(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        display_name=data.display_name,
        social_platform=data.social_platform,
        social_username=data.social_username,
        social_url=data.social_url,
        follower_count=data.follower_count,
        tier=tier,
        commission_rate=commission_rate,
        referral_code=referral_code,
        status="pending",
        application_reason=data.application_reason,
        promotion_plan=data.promotion_plan,
        created_at=datetime.utcnow(),
    )
    
    db.add(ambassador)
    db.commit()
    db.refresh(ambassador)
    
    return {
        "message": "Application submitted successfully",
        "status": "pending",
        "tier": tier,
        "commission_rate": f"{int(commission_rate * 100)}%",
        "referral_code": referral_code,
    }


@router.get("/track/{code}")
async def track_referral_click(
    code: str,
    request: Request,
    source: Optional[str] = Query(None),
    campaign: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Track a referral link click"""
    ambassador = db.query(Ambassador).filter(Ambassador.referral_code == code.upper()).first()
    if not ambassador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid referral code"
        )
    
    if ambassador.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ambassador account not active"
        )
    
    # Increment click count
    ambassador.total_clicks += 1
    
    # Log click
    click = AmbassadorClick(
        id=str(uuid.uuid4()),
        ambassador_id=ambassador.id,
        source=source,
        campaign=campaign,
        # ip_hash could be added here
        created_at=datetime.utcnow()
    )
    db.add(click)
    db.commit()
    
    return {
        "tracked": True,
        "ambassador": ambassador.display_name,
        "redirect_url": f"https://momentaic.com/signup?ref={code}&src={source or 'direct'}",
    }


# ============ AMBASSADOR DASHBOARD ENDPOINTS ============

@router.get("/me", response_model=AmbassadorProfileResponse)
async def get_ambassador_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's ambassador profile
    Syncs with Stripe if connected to get latest status
    """
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if not ambassador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not an ambassador"
        )
    
    # Sync Stripe Status if connected but seemingly incomplete
    if ambassador.stripe_connect_id and settings.stripe_secret_key:
        stripe.api_key = settings.stripe_secret_key
        try:
            account = stripe.Account.retrieve(ambassador.stripe_connect_id)
            payouts_enabled = account.get("payouts_enabled", False)
            details_submitted = account.get("details_submitted", False)
            
            if payouts_enabled != ambassador.stripe_payouts_enabled or details_submitted != ambassador.stripe_onboarding_complete:
                ambassador.stripe_payouts_enabled = payouts_enabled
                ambassador.stripe_onboarding_complete = details_submitted
                if payouts_enabled and details_submitted and ambassador.status == "pending":
                    ambassador.status = "active"
                db.commit()
        except Exception as e:
            logger.warning(f"Failed to sync stripe status: {e}")
    
    signups = ambassador.total_signups
    conversions = ambassador.total_conversions
    conversion_rate = (conversions / signups * 100) if signups > 0 else 0.0
    
    return {
        "id": ambassador.id,
        "display_name": ambassador.display_name,
        "tier": ambassador.tier,
        "commission_rate": ambassador.commission_rate,
        "referral_code": ambassador.referral_code,
        "referral_url": f"https://momentaic.com/signup?ref={ambassador.referral_code}",
        "stripe_connected": ambassador.stripe_connect_id is not None,
        "stripe_payouts_enabled": ambassador.stripe_payouts_enabled,
        "total_clicks": ambassador.total_clicks,
        "total_signups": signups,
        "total_conversions": conversions,
        "conversion_rate": round(conversion_rate, 1),
        "total_earnings": ambassador.total_earnings,
        "pending_balance": ambassador.pending_balance,
        "available_balance": ambassador.available_balance,
        "total_paid_out": ambassador.total_paid_out,
        "status": ambassador.status,
        "created_at": ambassador.created_at,
    }


@router.get("/conversions")
async def get_ambassador_conversions(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Get ambassador's conversion history"""
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if not ambassador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not an ambassador"
        )
    
    conversions = db.query(AmbassadorConversion)\
        .filter(AmbassadorConversion.ambassador_id == ambassador.id)\
        .order_by(AmbassadorConversion.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "conversions": conversions, # Pydantic will serialize
        "total": len(conversions), # Pagination count would need separate count query
    }


@router.get("/earnings")
async def get_ambassador_earnings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed earnings breakdown"""
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if not ambassador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not an ambassador"
        )
    
    # Aggregate monthly earnings (Mock logic for now, or SQL group by)
    # For now returning placeholder structure
    monthly_earnings = [
        {"month": "Dec 2024", "earnings": 0.0, "conversions": 0},
    ]
    
    return {
        "total_earnings": ambassador.total_earnings,
        "pending_balance": ambassador.pending_balance,
        "available_balance": ambassador.available_balance,
        "total_paid_out": ambassador.total_paid_out,
        "next_payout_eligible": ambassador.available_balance,
        "chargeback_hold_amount": ambassador.pending_balance,
        "min_payout_threshold": settings.ambassador_min_payout,
        "monthly_earnings": monthly_earnings,
    }


# ============ STRIPE CONNECT ENDPOINTS ============

@router.post("/stripe/onboard")
async def create_stripe_connect_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate Stripe Connect onboarding link (Real)"""
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if not ambassador:
        raise HTTPException(status_code=404, detail="Not an ambassador")
    
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe API key not configured")
    
    stripe.api_key = settings.stripe_secret_key
    
    try:
        # Create account if not exists
        if not ambassador.stripe_connect_id:
            account = stripe.Account.create(
                type="express",
                country="US", # Default, user can change
                email=current_user.email,
                capabilities={
                    "transfers": {"requested": True},
                },
            )
            ambassador.stripe_connect_id = account.id
            db.commit()
            account_id = account.id
        else:
            account_id = ambassador.stripe_connect_id

        # Create account link
        account_link = stripe.AccountLink.create(
            account=account_id,
            refresh_url="https://momentaic.com/ambassador?refresh=true",
            return_url="https://momentaic.com/ambassador?success=true",
            type="account_onboarding",
        )
        
        return {
            "onboarding_url": account_link.url,
            "account_id": account_id,
        }

    except Exception as e:
        logger.error(f"Stripe onboarding failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stripe/dashboard")
async def get_stripe_dashboard_link(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get link to Stripe Express Dashboard"""
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if not ambassador or not ambassador.stripe_connect_id:
        raise HTTPException(status_code=400, detail="Ambassador account not connected")
    
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe API key not configured")
    
    stripe.api_key = settings.stripe_secret_key
    
    try:
        login_link = stripe.Account.create_login_link(ambassador.stripe_connect_id)
        return {"dashboard_url": login_link.url}
    except Exception as e:
        logger.error(f"Stripe login link failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payout")
async def request_payout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Request a payout of available balance"""
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if not ambassador:
        raise HTTPException(status_code=404, detail="Not an ambassador")
    
    if not ambassador.stripe_payouts_enabled or not ambassador.stripe_connect_id:
        raise HTTPException(status_code=400, detail="Stripe account not connected")
    
    min_payout = settings.ambassador_min_payout
    if ambassador.available_balance < min_payout:
        raise HTTPException(status_code=400, detail=f"Minimum payout is ${min_payout}")
    
    payout_amount = ambassador.available_balance
    amount_cents = int(payout_amount * 100)
    
    # Initiate Transfer using Stripe API
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe API key not configured")
    
    stripe.api_key = settings.stripe_secret_key
    
    try:
        transfer = stripe.Transfer.create(
            amount=amount_cents,
            currency="usd",
            destination=ambassador.stripe_connect_id,
            description="Ambassador Payout",
        )
        
        # Record payout
        payout = AmbassadorPayout(
            id=str(uuid.uuid4()),
            ambassador_id=ambassador.id,
            amount=payout_amount,
            stripe_transfer_id=transfer.id,
            status="completed", # Transfer is immediate
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db.add(payout)
        
        # Update balance
        ambassador.available_balance = 0.0
        ambassador.total_paid_out += payout_amount
        db.commit()
        
        return {
            "id": payout.id,
            "amount": payout_amount,
            "status": "completed",
            "message": f"Payout of ${payout_amount:.2f} transferred successfully.",
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe transfer failed: {e}")
        raise HTTPException(status_code=400, detail=f"Payout failed: {e.user_message}")


@router.get("/payouts")
async def get_payout_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get payout history"""
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user.id).first()
    if not ambassador:
        raise HTTPException(status_code=404, detail="Not an ambassador")
    
    payouts = db.query(AmbassadorPayout).filter(AmbassadorPayout.ambassador_id == ambassador.id).all()
    return {"payouts": payouts, "total": len(payouts)}


# ============ ADMIN ENDPOINTS ============

@router.get("/admin/list")
async def list_all_ambassadors(
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all ambassadors (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(Ambassador)
    if status_filter:
        query = query.filter(Ambassador.status == status_filter)
    
    ambassadors = query.all()
    return {"ambassadors": ambassadors, "total": len(ambassadors)}


@router.post("/admin/{ambassador_id}/approve")
async def approve_ambassador(
    ambassador_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve an ambassador application"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    ambassador = db.query(Ambassador).filter(Ambassador.id == ambassador_id).first()
    if not ambassador:
        raise HTTPException(status_code=404, detail="Ambassador not found")
    
    ambassador.status = "active"
    ambassador.approved_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Ambassador approved", "status": "active"}


@router.post("/admin/{ambassador_id}/suspend")
async def suspend_ambassador(
    ambassador_id: str,
    reason: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Suspend an ambassador"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
        
    ambassador = db.query(Ambassador).filter(Ambassador.id == ambassador_id).first()
    if not ambassador:
        raise HTTPException(status_code=404, detail="Ambassador not found")
    
    ambassador.status = "suspended"
    ambassador.rejection_reason = reason
    db.commit()
    
    return {"message": "Ambassador suspended", "status": "suspended"}


# ============ WEBHOOK ENDPOINT ============

@router.post("/webhook/stripe-connect")
async def handle_stripe_connect_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handle Stripe Connect webhooks
    Verifies signature and processes account/payout events
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        if not settings.stripe_connect_webhook_secret:
            logger.error("Stripe Connect webhook secret not configured")
            raise HTTPException(status_code=500, detail="Webhook configuration error")

        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_connect_webhook_secret
        )
    except ValueError as e:
        logger.error("Invalid payload", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid signature", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    data = event["data"]["object"]
    
    logger.info(f"Received Stripe Connect event: {event_type}")

    # 1. Handle Account Updates (Onboarding completion)
    if event_type == "account.updated":
        account_id = data["id"]
        ambassador = db.query(Ambassador).filter(Ambassador.stripe_connect_id == account_id).first()
        
        if ambassador:
            payouts_enabled = data.get("payouts_enabled", False)
            details_submitted = data.get("details_submitted", False)
            
            ambassador.stripe_payouts_enabled = payouts_enabled
            ambassador.stripe_onboarding_complete = details_submitted
            
            if payouts_enabled and details_submitted and ambassador.status == "pending":
                ambassador.status = "active"
                
            db.commit()
            logger.info(f"Updated ambassador {ambassador.id} stripe status: payouts={payouts_enabled}")
        else:
            logger.info(f"Account {account_id} not found locally (ignoring)")

    elif event_type == "transfer.created":
        logger.info(f"Transfer created: {data['id']} amount={data['amount']}")
        
    return {"received": True}


# ============ OUTREACH ENDPOINTS ============

@router.post("/outreach/generate")
async def generate_ambassador_outreach(
    candidate_name: str,
    platform: str,
    program_summary: str,
    startup_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate personalized outreach for a potential ambassador.
    """
    # Get startup context (using first startup if none provided)
    from app.models.startup import Startup
    
    query = db.query(Startup)
    if startup_id:
        query = query.filter(Startup.id == startup_id)
    else:
        query = query.filter(Startup.owner_id == current_user.id)
        
    startup = query.first()
    
    if not startup:
        raise HTTPException(status_code=404, detail="Startup context not found")
        
    result = await ambassador_agent.generate_outreach(
        candidate_name=candidate_name,
        platform=platform,
        startup_context={
            "name": startup.name,
            "description": startup.description,
            "tagline": startup.tagline,
            "industry": startup.industry,
        },
        program_summary=program_summary
    )
    
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result.get("error"))
        
    return result
