"""
Free Roast API Endpoint
Public "Roast My Startup" tool with gated full results.
The tip of the viral spear for #MomentAIcRoast campaign.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field, EmailStr
import structlog

from app.services.referral_service import referral_service

logger = structlog.get_logger()

router = APIRouter(prefix="/roast", tags=["Free Roast"])


class RoastRequest(BaseModel):
    """Request for a startup roast."""
    startup_name: str = Field(min_length=2, max_length=100)
    startup_description: str = Field(min_length=20, max_length=1000)
    website_url: Optional[str] = None
    email: EmailStr = Field(description="Email to receive full results")


class QuickRoast(BaseModel):
    """Quick roast preview (no login required)."""
    startup_name: str
    overall_score: int  # 0-100
    one_liner: str
    top_issue: str
    share_link: str
    unlock_message: str


class FullRoast(BaseModel):
    """Full roast report (gated)."""
    startup_name: str
    overall_score: int
    executive_summary: str
    strengths: list
    weaknesses: list
    market_fit_analysis: str
    competitor_landscape: str
    growth_recommendations: list
    action_plan: list
    investor_readiness: str


@router.post("/quick", response_model=QuickRoast)
async def get_quick_roast(
    request: RoastRequest,
    background_tasks: BackgroundTasks
) -> QuickRoast:
    """
    Get a quick startup roast (FREE, no login).
    
    This is the viral hook:
    - Returns a teaser roast immediately
    - Full results emailed (captures lead)
    - Unlock full report by: 3 referrals OR tweet #MomentAIcRoast
    """
    logger.info(
        "Roast requested",
        startup=request.startup_name,
        email=request.email
    )
    
    # Generate teaser roast (actual LLM call in production)
    score = 65  # Placeholder - calculate from LLM analysis
    one_liner = f"'{request.startup_name}' has potential, but you're solving a problem nobody's willing to pay for. Yet."
    top_issue = "Value proposition is unclear. Your grandmother couldn't explain what you do."
    
    # Generate referral code for this email
    user_id = f"roast_{request.email.replace('@', '_').replace('.', '_')}"
    ref_code = referral_service.generate_code(user_id)
    
    share_link = f"https://momentaic.com/roast?ref={ref_code}"
    
    # Queue email with full results preview
    async def send_full_results_email():
        # In production, send via email service
        logger.info(f"Sending roast results to {request.email}")
    
    background_tasks.add_task(send_full_results_email)
    
    return QuickRoast(
        startup_name=request.startup_name,
        overall_score=score,
        one_liner=one_liner,
        top_issue=top_issue,
        share_link=share_link,
        unlock_message=f"🔓 Unlock your Full Fix Plan: Share with 3 friends OR tweet with #MomentAIcRoast. Your referral link: {share_link}"
    )


@router.get("/full/{roast_id}")
async def get_full_roast(
    roast_id: str,
    email: EmailStr
) -> Dict[str, Any]:
    """
    Get full roast report (gated behind referrals or tweet).
    """
    user_id = f"roast_{email.replace('@', '_').replace('.', '_')}"
    
    # Check if unlocked
    if not referral_service.check_unlock(user_id):
        stats = referral_service.get_stats(user_id)
        referrals_needed = 3 - (stats.total_referrals if stats else 0)
        
        return {
            "locked": True,
            "referrals_needed": referrals_needed,
            "unlock_options": [
                f"Refer {referrals_needed} more friends",
                "Tweet your roast with #MomentAIcRoast"
            ],
            "share_link": f"https://momentaic.com/roast?ref={stats.code if stats else ''}"
        }
    
    # Return full roast (placeholder - would fetch from DB)
    return {
        "locked": False,
        "roast": {
            "startup_name": "Your Startup",
            "overall_score": 65,
            "executive_summary": "Your startup has potential but needs work on value prop clarity.",
            "action_plan": [
                "Rewrite your landing page in 3rd grade reading level",
                "Interview 10 potential customers this week",
                "Cut 50% of your features"
            ]
        }
    }


@router.post("/unlock-via-tweet")
async def unlock_via_tweet(
    email: EmailStr,
    tweet_url: str
) -> Dict[str, Any]:
    """
    Unlock full roast by verifying a tweet with #MomentAIcRoast.
    """
    user_id = f"roast_{email.replace('@', '_').replace('.', '_')}"
    
    # Verify tweet contains correct hashtag (simplified - would use Twitter API)
    if "#MomentAIcRoast" not in tweet_url and "momentaicroast" not in tweet_url.lower():
        raise HTTPException(
            status_code=400,
            detail="Tweet must contain #MomentAIcRoast hashtag"
        )
    
    # Extract tweet ID from URL
    tweet_id = tweet_url.split("/")[-1].split("?")[0]
    
    # Unlock
    referral_service.unlock_via_tweet(user_id, tweet_id)
    
    return {
        "status": "unlocked",
        "message": "🎉 Your full roast report is now unlocked!",
        "redirect": f"/roast/full/{user_id}"
    }


@router.get("/stats/{email}")
async def get_referral_stats(email: EmailStr) -> Dict[str, Any]:
    """
    Get referral stats for a user.
    """
    user_id = f"roast_{email.replace('@', '_').replace('.', '_')}"
    stats = referral_service.get_stats(user_id)
    
    if not stats:
        return {
            "referrals": 0,
            "unlocked": False,
            "needed": 3
        }
    
    return {
        "referrals": stats.total_referrals,
        "unlocked": len(stats.unlocked_features) > 0,
        "needed": max(0, 3 - stats.total_referrals),
        "code": stats.code,
        "share_link": f"https://momentaic.com/roast?ref={stats.code}"
    }
