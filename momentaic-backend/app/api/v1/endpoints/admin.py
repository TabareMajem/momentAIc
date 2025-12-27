"""
Admin Panel API Endpoints
Superuser-only access for system management
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserTier, CreditTransaction
from app.models.startup import Startup
from pydantic import BaseModel

router = APIRouter()


class AdminStats(BaseModel):
    total_users: int
    active_subscriptions: int
    total_revenue: float
    agents_deployed: int


class AdminUser(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    subscription_tier: str
    status: str
    credits_balance: int
    created_at: str

    class Config:
        from_attributes = True


def require_superuser(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to require superuser access"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get admin dashboard statistics.
    Requires superuser privileges.
    """
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0

    # Active subscriptions (paid tiers)
    result = await db.execute(
        select(func.count(User.id)).where(User.tier != UserTier.STARTER)
    )
    active_subscriptions = result.scalar() or 0

    # Total revenue estimate (placeholder - would come from Stripe)
    # Rough estimate: Growth = $49/mo, God Mode = $199/mo
    result = await db.execute(
        select(func.count(User.id)).where(User.tier == UserTier.GROWTH)
    )
    growth_count = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(User.id)).where(User.tier == UserTier.GOD_MODE)
    )
    god_mode_count = result.scalar() or 0
    
    total_revenue = (growth_count * 49) + (god_mode_count * 199)

    # Agents deployed (count of 17 agents * active users as rough estimate)
    agents_deployed = 17  # Current agent count

    return AdminStats(
        total_users=total_users,
        active_subscriptions=active_subscriptions,
        total_revenue=total_revenue,
        agents_deployed=agents_deployed,
    )


@router.get("/users", response_model=List[AdminUser])
async def get_admin_users(
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    List all users for admin management.
    Requires superuser privileges.
    """
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()

    return [
        AdminUser(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role="admin" if user.is_superuser else "user",
            subscription_tier=user.tier.value.lower(),
            status="active" if user.is_active else "banned",
            credits_balance=user.credits_balance,
            created_at=user.created_at.isoformat(),
        )
        for user in users
    ]


@router.patch("/users/{user_id}/ban")
async def ban_user(
    user_id: str,
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Ban or unban a user.
    Requires superuser privileges.
    """
    from uuid import UUID
    
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    await db.commit()
    
    return {"success": True, "is_active": user.is_active}


@router.patch("/users/{user_id}/tier")
async def update_user_tier(
    user_id: str,
    tier: str,
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user subscription tier.
    Requires superuser privileges.
    """
    from uuid import UUID
    
    tier_map = {
        "starter": UserTier.STARTER,
        "growth": UserTier.GROWTH,
        "god_mode": UserTier.GOD_MODE,
    }
    
    if tier.lower() not in tier_map:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.tier = tier_map[tier.lower()]
    await db.commit()
    
    return {"success": True, "tier": user.tier.value}


class AdminChatRequest(BaseModel):
    message: str


@router.post("/agents/nano/chat")
async def chat_nano_bananas(
    request: AdminChatRequest,
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Chat with Nano Bananas (Admin-only Growth Agent).
    """
    from app.agents.nano_agent import nano_agent
    
    response = await nano_agent.process(
        message=request.message,
        user_id=str(admin.id),
        context={}
    )
    
    return response
