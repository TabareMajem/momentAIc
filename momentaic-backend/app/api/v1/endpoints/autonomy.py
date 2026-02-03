"""
Autonomy Settings Endpoints
API for managing proactive agent configuration
"""

from typing import List
from uuid import UUID
import structlog

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.startup import Startup
from app.models.autonomy import StartupAutonomySettings, ProactiveActionLog
from app.schemas.autonomy import (
    AutonomySettingsCreate, AutonomySettingsUpdate, AutonomySettingsResponse,
    ProactiveActionResponse
)

router = APIRouter()
logger = structlog.get_logger()


async def verify_startup_access(startup_id: UUID, user: User, db: AsyncSession) -> Startup:
    """Verify user has access to startup"""
    result = await db.execute(
        select(Startup).where(Startup.id == startup_id, Startup.owner_id == user.id)
    )
    startup = result.scalar_one_or_none()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    return startup


@router.get("/{startup_id}/autonomy", response_model=AutonomySettingsResponse)
async def get_autonomy_settings(
    startup_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get autonomy settings for a startup"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(StartupAutonomySettings).where(
            StartupAutonomySettings.startup_id == startup_id
        )
    )
    settings = result.scalar_one_or_none()
    
    # Create default settings if none exist
    if not settings:
        settings = StartupAutonomySettings(startup_id=startup_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return settings


@router.put("/{startup_id}/autonomy", response_model=AutonomySettingsResponse)
async def update_autonomy_settings(
    startup_id: UUID,
    payload: AutonomySettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update autonomy settings for a startup"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(StartupAutonomySettings).where(
            StartupAutonomySettings.startup_id == startup_id
        )
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = StartupAutonomySettings(startup_id=startup_id)
        db.add(settings)
    
    # Update only provided fields
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    # Handle pause timestamp
    if payload.is_paused is True and settings.paused_at is None:
        from datetime import datetime
        settings.paused_at = datetime.utcnow()
    elif payload.is_paused is False:
        settings.paused_at = None
        settings.paused_reason = None
    
    await db.commit()
    await db.refresh(settings)
    
    logger.info("Autonomy settings updated", startup_id=str(startup_id), level=settings.global_level)
    return settings


@router.post("/{startup_id}/autonomy/pause")
async def pause_proactive_agents(
    startup_id: UUID,
    reason: str = "Manual pause",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Emergency pause all proactive agents for a startup"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(StartupAutonomySettings).where(
            StartupAutonomySettings.startup_id == startup_id
        )
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = StartupAutonomySettings(startup_id=startup_id)
        db.add(settings)
    
    from datetime import datetime
    settings.is_paused = True
    settings.paused_at = datetime.utcnow()
    settings.paused_reason = reason
    
    await db.commit()
    logger.warning("Proactive agents PAUSED", startup_id=str(startup_id), reason=reason)
    
    return {"success": True, "message": "All proactive agents have been paused"}


@router.post("/{startup_id}/autonomy/resume")
async def resume_proactive_agents(
    startup_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resume proactive agents for a startup"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(StartupAutonomySettings).where(
            StartupAutonomySettings.startup_id == startup_id
        )
    )
    settings = result.scalar_one_or_none()
    
    if settings:
        settings.is_paused = False
        settings.paused_at = None
        settings.paused_reason = None
        await db.commit()
    
    logger.info("Proactive agents RESUMED", startup_id=str(startup_id))
    return {"success": True, "message": "Proactive agents have been resumed"}


@router.get("/{startup_id}/autonomy/actions", response_model=List[ProactiveActionResponse])
async def get_proactive_actions(
    startup_id: UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent proactive actions for a startup"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(ProactiveActionLog)
        .where(ProactiveActionLog.startup_id == startup_id)
        .order_by(ProactiveActionLog.created_at.desc())
        .limit(limit)
    )
    actions = result.scalars().all()
    return actions


@router.post("/{startup_id}/autonomy/actions/{action_id}/approve")
async def approve_pending_action(
    startup_id: UUID,
    action_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a pending proactive action"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(ProactiveActionLog).where(
            ProactiveActionLog.id == action_id,
            ProactiveActionLog.startup_id == startup_id,
        )
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    if action.status != "pending_approval":
        raise HTTPException(status_code=400, detail="Action is not pending approval")
    
    from datetime import datetime
    action.status = "approved"
    action.approved_by = current_user.id
    action.approved_at = datetime.utcnow()
    
    await db.commit()
    
    # TODO: Execute the approved action
    
    return {"success": True, "message": "Action approved"}


@router.post("/{startup_id}/autonomy/actions/{action_id}/reject")
async def reject_pending_action(
    startup_id: UUID,
    action_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a pending proactive action"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(ProactiveActionLog).where(
            ProactiveActionLog.id == action_id,
            ProactiveActionLog.startup_id == startup_id,
        )
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    action.status = "rejected"
    await db.commit()
    
    return {"success": True, "message": "Action rejected"}
