"""
Tier Limits Configuration
Defines feature access per subscription tier
"""

from enum import Enum
from typing import Dict, Any, List
from app.models.user import UserTier


# Tier Limits Configuration
TIER_LIMITS: Dict[UserTier, Dict[str, Any]] = {
    UserTier.STARTER: {
        "display_name": "Starter",
        "price_monthly": 9,
        "max_startups": 1,
        "credits_per_month": 100,
        "power_plays_per_month": 3,
        "agentforge_access": False,
        "agentforge_workflows_per_month": 0,
        "yokaizen_access": False,
        "yokaizen_modules": [],
        "social_posting": False,
        "social_platforms": [],
        "browser_scraping": False,
        "vault_access": True,
        "vault_priority": False,
        "trial_days": 14,
        "trial_tier_access": "growth",  # During trial, user gets Growth access
    },
    UserTier.GROWTH: {
        "display_name": "Growth",
        "price_monthly": 29,
        "max_startups": 3,
        "credits_per_month": 500,
        "power_plays_per_month": -1,  # -1 = unlimited
        "agentforge_access": True,
        "agentforge_workflows_per_month": 5,
        "yokaizen_access": True,
        "yokaizen_modules": ["sales"],
        "social_posting": True,
        "social_platforms": ["linkedin", "twitter"],
        "browser_scraping": False,
        "vault_access": True,
        "vault_priority": False,
        "trial_days": 0,
        "trial_tier_access": None,
    },
    UserTier.GOD_MODE: {
        "display_name": "God Mode",
        "price_monthly": 49,
        "max_startups": -1,  # -1 = unlimited
        "credits_per_month": 2000,
        "power_plays_per_month": -1,
        "agentforge_access": True,
        "agentforge_workflows_per_month": -1,
        "yokaizen_access": True,
        "yokaizen_modules": ["sales", "marketing", "ops"],
        "social_posting": True,
        "social_platforms": ["linkedin", "twitter", "instagram", "tiktok"],
        "browser_scraping": True,
        "vault_access": True,
        "vault_priority": True,
        "trial_days": 0,
        "trial_tier_access": None,
    },
}


def get_tier_limits(tier: UserTier) -> Dict[str, Any]:
    """Get limits for a specific tier"""
    return TIER_LIMITS.get(tier, TIER_LIMITS[UserTier.STARTER])


def get_effective_tier(user) -> UserTier:
    """
    Get the effective tier for a user (considering trial period).
    
    If user is in trial and has trial_tier_access, return that tier's limits.
    """
    from datetime import datetime, timedelta
    
    tier = user.tier
    limits = TIER_LIMITS[tier]
    
    # Check if user is in trial period
    trial_days = limits.get("trial_days", 0)
    if trial_days > 0:
        trial_end = user.created_at + timedelta(days=trial_days)
        if datetime.utcnow() < trial_end:
            trial_access = limits.get("trial_tier_access")
            if trial_access:
                return UserTier(trial_access)
    
    return tier


def can_create_startup(user, current_startup_count: int) -> tuple:
    """
    Check if user can create a new startup.
    
    Returns: (allowed: bool, message: str)
    """
    effective_tier = get_effective_tier(user)
    limits = TIER_LIMITS[effective_tier]
    max_startups = limits["max_startups"]
    
    if max_startups == -1:  # Unlimited
        return (True, "")
    
    if current_startup_count >= max_startups:
        upgrade_tier = UserTier.GROWTH if effective_tier == UserTier.STARTER else UserTier.GOD_MODE
        return (
            False,
            f"You've reached the maximum of {max_startups} startup(s) on the {limits['display_name']} plan. "
            f"Upgrade to {TIER_LIMITS[upgrade_tier]['display_name']} for more."
        )
    
    # Soft warning when at limit - 1
    if current_startup_count == max_startups - 1:
        return (
            True,
            f"This will be your last available startup slot on the {limits['display_name']} plan."
        )
    
    return (True, "")


def can_use_power_play(user, power_plays_used_this_month: int) -> tuple:
    """
    Check if user can execute a Power Play.
    
    Returns: (allowed: bool, message: str)
    """
    effective_tier = get_effective_tier(user)
    limits = TIER_LIMITS[effective_tier]
    max_power_plays = limits["power_plays_per_month"]
    
    if max_power_plays == -1:  # Unlimited
        return (True, "")
    
    if power_plays_used_this_month >= max_power_plays:
        return (
            False,
            f"You've used all {max_power_plays} Power Plays for this month. "
            f"Upgrade to Growth for unlimited Power Plays."
        )
    
    return (True, "")


def can_access_ecosystem(user, platform: str) -> tuple:
    """
    Check if user can access AgentForge or Yokaizen.
    
    Args:
        platform: "agentforge" or "yokaizen"
    
    Returns: (allowed: bool, message: str)
    """
    effective_tier = get_effective_tier(user)
    limits = TIER_LIMITS[effective_tier]
    
    if platform == "agentforge":
        if not limits["agentforge_access"]:
            return (False, "AgentForge access requires Growth plan or higher.")
        return (True, "")
    
    elif platform == "yokaizen":
        if not limits["yokaizen_access"]:
            return (False, "Yokaizen access requires Growth plan or higher.")
        return (True, "")
    
    return (False, f"Unknown platform: {platform}")


def can_post_to_social(user, platform: str) -> tuple:
    """
    Check if user can post to a social platform.
    
    Returns: (allowed: bool, message: str)
    """
    effective_tier = get_effective_tier(user)
    limits = TIER_LIMITS[effective_tier]
    
    if not limits["social_posting"]:
        return (False, "Social posting requires Growth plan or higher.")
    
    allowed_platforms = limits.get("social_platforms", [])
    if platform.lower() not in allowed_platforms:
        return (
            False,
            f"Posting to {platform} requires God Mode plan."
        )
    
    return (True, "")


def get_trial_status(user) -> Dict[str, Any]:
    """
    Get user's trial status.
    
    Returns dict with:
    - in_trial: bool
    - days_remaining: int
    - trial_tier: str (tier they have access to during trial)
    """
    from datetime import datetime, timedelta
    
    limits = TIER_LIMITS[user.tier]
    trial_days = limits.get("trial_days", 0)
    
    if trial_days == 0:
        return {"in_trial": False, "days_remaining": 0, "trial_tier": None}
    
    trial_end = user.created_at + timedelta(days=trial_days)
    now = datetime.utcnow()
    
    if now >= trial_end:
        return {"in_trial": False, "days_remaining": 0, "trial_tier": None}
    
    days_remaining = (trial_end - now).days
    return {
        "in_trial": True,
        "days_remaining": days_remaining,
        "trial_tier": limits.get("trial_tier_access"),
    }
