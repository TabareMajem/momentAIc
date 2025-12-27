"""
Referral System API Endpoints
Viral growth through referrals
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


# ============ SCHEMAS ============

class ReferralLinkResponse(BaseModel):
    referral_code: str
    referral_url: str
    share_message: str
    share_templates: dict


class ReferralStatsResponse(BaseModel):
    total_referrals: int
    successful_signups: int
    converted_users: int
    total_credits_earned: int
    current_streak: int
    rank: int
    next_milestone: dict
    milestones_achieved: List[str]


class ReferralLeaderboardEntry(BaseModel):
    rank: int
    username: str
    referral_count: int
    avatar_url: Optional[str] = None


class ClaimRewardRequest(BaseModel):
    milestone_id: str


class TrackReferralRequest(BaseModel):
    referral_code: str
    source: Optional[str] = None


# ============ MOCK DATA STORE ============
# In production, this would be database tables

_referral_codes = {}  # user_id -> code
_referral_stats = {}  # user_id -> stats dict
_referrals = []  # List of referral records


def _get_or_create_code(user_id: str) -> str:
    """Get or create referral code for user"""
    if user_id not in _referral_codes:
        _referral_codes[user_id] = uuid.uuid4().hex[:8].upper()
    return _referral_codes[user_id]


def _get_stats(user_id: str) -> dict:
    """Get referral stats for user"""
    if user_id not in _referral_stats:
        _referral_stats[user_id] = {
            "total_referrals": 0,
            "successful_signups": 0,
            "converted_users": 0,
            "total_credits_earned": 0,
            "milestones": [],
        }
    return _referral_stats[user_id]


# ============ ENDPOINTS ============

@router.post("/generate-link", response_model=ReferralLinkResponse)
async def generate_referral_link(
    current_user: User = Depends(get_current_user),
):
    """Generate a unique referral link for the user"""
    referral_code = _get_or_create_code(current_user.id)
    base_url = "https://momentaic.com"
    
    return {
        "referral_code": referral_code,
        "referral_url": f"{base_url}/signup?ref={referral_code}",
        "share_message": f"🚀 I'm building my startup with MomentAIc - the AI operating system for founders. Join me and get 100 bonus credits! {base_url}/signup?ref={referral_code}",
        "share_templates": {
            "twitter": f"🚀 Building my startup 10x faster with @MomentAIc - the AI OS for founders.\n\nIt's like having a full C-suite team powered by AI.\n\nJoin me & get 100 bonus credits 👇\n{base_url}/signup?ref={referral_code}",
            "linkedin": f"I've been using MomentAIc to run my startup and it's a game-changer.\n\nImagine having AI agents for:\n✅ Growth & Marketing\n✅ Finance & CFO\n✅ Product Management\n✅ Legal & Compliance\n\nAll in one platform.\n\nIf you're a founder, check it out (you'll get 100 bonus credits): {base_url}/signup?ref={referral_code}",
            "email_subject": "You need to try this AI tool for startups",
            "email_body": f"Hey!\n\nI wanted to share something that's been helping me run my startup way more efficiently.\n\nIt's called MomentAIc - basically an AI operating system that gives you a virtual C-suite team.\n\nI can chat with AI agents for growth, finance, legal, product - everything.\n\nIf you sign up with my link, you get 100 bonus credits:\n{base_url}/signup?ref={referral_code}\n\nLet me know what you think!",
            "whatsapp": f"🚀 Found this amazing AI tool for startups - MomentAIc. It's like having a full team powered by AI. Sign up with my link for 100 bonus credits: {base_url}/signup?ref={referral_code}",
        }
    }


@router.get("/stats", response_model=ReferralStatsResponse)
async def get_referral_stats(
    current_user: User = Depends(get_current_user),
):
    """Get referral statistics for current user"""
    stats = _get_stats(current_user.id)
    
    # Calculate next milestone
    milestones = [
        {"count": 5, "name": "Starter", "reward": 250, "badge": "🌱"},
        {"count": 10, "name": "Rising Star", "reward": 500, "badge": "⭐"},
        {"count": 25, "name": "Growth Master", "reward": 1000, "badge": "🚀"},
        {"count": 50, "name": "Viral Legend", "reward": 2500, "badge": "🔥"},
        {"count": 100, "name": "Unicorn Hunter", "reward": 5000, "badge": "🦄"},
    ]
    
    current_count = stats["successful_signups"]
    next_milestone = None
    achieved = []
    
    for m in milestones:
        if current_count >= m["count"]:
            achieved.append(f"{m['badge']} {m['name']}")
        elif next_milestone is None:
            next_milestone = {
                "name": m["name"],
                "required": m["count"],
                "current": current_count,
                "reward_credits": m["reward"],
                "progress_percent": int((current_count / m["count"]) * 100),
            }
    
    if next_milestone is None:
        next_milestone = {
            "name": "Max Level",
            "required": 100,
            "current": current_count,
            "reward_credits": 0,
            "progress_percent": 100,
        }
    
    # Calculate rank (mock - would be from leaderboard query)
    rank = max(1, 100 - stats["successful_signups"])
    
    return {
        "total_referrals": stats["total_referrals"],
        "successful_signups": stats["successful_signups"],
        "converted_users": stats["converted_users"],
        "total_credits_earned": stats["total_credits_earned"],
        "current_streak": 0,  # TODO: implement streak tracking
        "rank": rank,
        "next_milestone": next_milestone,
        "milestones_achieved": achieved,
    }


@router.get("/leaderboard", response_model=List[ReferralLeaderboardEntry])
async def get_referral_leaderboard(
    limit: int = Query(default=10, le=50),
    current_user: User = Depends(get_current_user),
):
    """Get top referrers leaderboard"""
    # Mock leaderboard data
    leaderboard = [
        {"rank": 1, "username": "alex_founder", "referral_count": 47, "avatar_url": None},
        {"rank": 2, "username": "sarah_startup", "referral_count": 38, "avatar_url": None},
        {"rank": 3, "username": "mike_growth", "referral_count": 31, "avatar_url": None},
        {"rank": 4, "username": "emma_ceo", "referral_count": 24, "avatar_url": None},
        {"rank": 5, "username": "david_hustle", "referral_count": 19, "avatar_url": None},
        {"rank": 6, "username": "lisa_tech", "referral_count": 15, "avatar_url": None},
        {"rank": 7, "username": "john_build", "referral_count": 12, "avatar_url": None},
        {"rank": 8, "username": "amy_scale", "referral_count": 9, "avatar_url": None},
        {"rank": 9, "username": "chris_launch", "referral_count": 7, "avatar_url": None},
        {"rank": 10, "username": "nina_grow", "referral_count": 5, "avatar_url": None},
    ]
    
    return leaderboard[:limit]


@router.post("/track")
async def track_referral(
    data: TrackReferralRequest,
    db: Session = Depends(get_db),
):
    """Track a referral when someone uses a referral code"""
    # Find referrer by code
    referrer_id = None
    for uid, code in _referral_codes.items():
        if code == data.referral_code.upper():
            referrer_id = uid
            break
    
    if not referrer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid referral code"
        )
    
    # Update stats
    stats = _get_stats(referrer_id)
    stats["total_referrals"] += 1
    
    return {"status": "tracked", "referrer_id": referrer_id}


@router.post("/confirm-signup")
async def confirm_referral_signup(
    referral_code: str,
    new_user_id: str,
    db: Session = Depends(get_db),
):
    """Confirm a successful signup from referral"""
    # Find referrer
    referrer_id = None
    for uid, code in _referral_codes.items():
        if code == referral_code.upper():
            referrer_id = uid
            break
    
    if not referrer_id:
        return {"status": "invalid_code"}
    
    # Update stats
    stats = _get_stats(referrer_id)
    stats["successful_signups"] += 1
    
    # Award credits
    SIGNUP_REWARD = 50
    stats["total_credits_earned"] += SIGNUP_REWARD
    
    # Check milestones
    count = stats["successful_signups"]
    milestone_rewards = {5: 250, 10: 500, 25: 1000, 50: 2500, 100: 5000}
    
    if count in milestone_rewards:
        stats["total_credits_earned"] += milestone_rewards[count]
        stats["milestones"].append(count)
    
    return {
        "status": "confirmed",
        "credits_awarded": SIGNUP_REWARD,
        "new_total": stats["successful_signups"],
    }


@router.post("/claim-reward")
async def claim_milestone_reward(
    data: ClaimRewardRequest,
    current_user: User = Depends(get_current_user),
):
    """Claim a milestone reward"""
    # In production, verify milestone is reached and not already claimed
    return {
        "status": "claimed",
        "credits_awarded": 250,
        "message": "Congratulations! You've earned 250 credits for reaching 5 referrals! 🎉"
    }
