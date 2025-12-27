"""
Trigger Endpoints
Manage proactive agent triggers
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User
from app.models.trigger import (
    TriggerRule, TriggerLog, TriggerType, TriggerLogStatus
)

logger = structlog.get_logger()
router = APIRouter()


# ==================
# Schemas
# ==================

class TriggerRuleCreate(BaseModel):
    """Create trigger rule"""
    name: str
    description: Optional[str] = None
    trigger_type: TriggerType
    condition: dict
    action: dict
    cooldown_minutes: int = 60
    max_triggers_per_day: int = 10


class TriggerRuleUpdate(BaseModel):
    """Update trigger rule"""
    name: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[dict] = None
    action: Optional[dict] = None
    is_active: Optional[bool] = None
    is_paused: Optional[bool] = None
    cooldown_minutes: Optional[int] = None
    max_triggers_per_day: Optional[int] = None


class TriggerRuleResponse(BaseModel):
    """Trigger rule response"""
    id: UUID
    name: str
    description: Optional[str]
    trigger_type: TriggerType
    condition: dict
    action: dict
    is_active: bool
    is_paused: bool
    last_triggered_at: Optional[str]
    trigger_count: int

    class Config:
        from_attributes = True


class TriggerLogResponse(BaseModel):
    """Trigger log response"""
    id: UUID
    status: TriggerLogStatus
    trigger_context: dict
    agent_response: Optional[dict]
    requires_approval: bool
    triggered_at: str
    completed_at: Optional[str]


class ApprovalDecision(BaseModel):
    """Approval decision for pending trigger"""
    approved: bool
    notes: Optional[str] = None


# ==================
# Endpoints
# ==================

@router.get("", response_model=List[TriggerRuleResponse])
async def list_triggers(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all trigger rules for a startup"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(TriggerRule).where(
            TriggerRule.startup_id == startup_id,
        ).order_by(TriggerRule.created_at.desc())
    )
    rules = result.scalars().all()
    
    return [
        TriggerRuleResponse(
            id=r.id,
            name=r.name,
            description=r.description,
            trigger_type=r.trigger_type,
            condition=r.condition,
            action=r.action,
            is_active=r.is_active,
            is_paused=r.is_paused,
            last_triggered_at=r.last_triggered_at.isoformat() if r.last_triggered_at else None,
            trigger_count=r.trigger_count,
        )
        for r in rules
    ]


@router.post("", response_model=TriggerRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_trigger(
    startup_id: UUID,
    trigger_data: TriggerRuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new trigger rule"""
    await verify_startup_access(startup_id, current_user, db)
    
    rule = TriggerRule(
        startup_id=startup_id,
        user_id=current_user.id,
        name=trigger_data.name,
        description=trigger_data.description,
        trigger_type=trigger_data.trigger_type,
        condition=trigger_data.condition,
        action=trigger_data.action,
        cooldown_minutes=trigger_data.cooldown_minutes,
        max_triggers_per_day=trigger_data.max_triggers_per_day,
    )
    
    db.add(rule)
    await db.flush()
    
    logger.info("Trigger created", name=trigger_data.name, type=trigger_data.trigger_type.value)
    
    return TriggerRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        trigger_type=rule.trigger_type,
        condition=rule.condition,
        action=rule.action,
        is_active=rule.is_active,
        is_paused=rule.is_paused,
        last_triggered_at=None,
        trigger_count=0,
    )


@router.get("/{trigger_id}", response_model=TriggerRuleResponse)
async def get_trigger(
    startup_id: UUID,
    trigger_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get trigger rule details"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(TriggerRule).where(
            TriggerRule.id == trigger_id,
            TriggerRule.startup_id == startup_id,
        )
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger rule not found"
        )
    
    return TriggerRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        trigger_type=rule.trigger_type,
        condition=rule.condition,
        action=rule.action,
        is_active=rule.is_active,
        is_paused=rule.is_paused,
        last_triggered_at=rule.last_triggered_at.isoformat() if rule.last_triggered_at else None,
        trigger_count=rule.trigger_count,
    )


@router.put("/{trigger_id}", response_model=TriggerRuleResponse)
async def update_trigger(
    startup_id: UUID,
    trigger_id: UUID,
    update_data: TriggerRuleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a trigger rule"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(TriggerRule).where(
            TriggerRule.id == trigger_id,
            TriggerRule.startup_id == startup_id,
        )
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger rule not found"
        )
    
    # Update fields
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    
    await db.flush()
    
    return TriggerRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        trigger_type=rule.trigger_type,
        condition=rule.condition,
        action=rule.action,
        is_active=rule.is_active,
        is_paused=rule.is_paused,
        last_triggered_at=rule.last_triggered_at.isoformat() if rule.last_triggered_at else None,
        trigger_count=rule.trigger_count,
    )


@router.delete("/{trigger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trigger(
    startup_id: UUID,
    trigger_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a trigger rule"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(TriggerRule).where(
            TriggerRule.id == trigger_id,
            TriggerRule.startup_id == startup_id,
        )
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger rule not found"
        )
    
    await db.delete(rule)


@router.get("/{trigger_id}/logs", response_model=List[TriggerLogResponse])
async def get_trigger_logs(
    startup_id: UUID,
    trigger_id: UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get trigger execution logs"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(TriggerLog).where(
            TriggerLog.rule_id == trigger_id,
            TriggerLog.startup_id == startup_id,
        ).order_by(TriggerLog.triggered_at.desc()).limit(limit)
    )
    logs = result.scalars().all()
    
    return [
        TriggerLogResponse(
            id=log.id,
            status=log.status,
            trigger_context=log.trigger_context,
            agent_response=log.agent_response,
            requires_approval=log.requires_approval,
            triggered_at=log.triggered_at.isoformat(),
            completed_at=log.completed_at.isoformat() if log.completed_at else None,
        )
        for log in logs
    ]


@router.get("/pending-approvals", response_model=List[TriggerLogResponse])
async def get_pending_approvals(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all pending trigger approvals"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(TriggerLog).where(
            TriggerLog.startup_id == startup_id,
            TriggerLog.status == TriggerLogStatus.AWAITING_APPROVAL,
        ).order_by(TriggerLog.triggered_at.desc())
    )
    logs = result.scalars().all()
    
    return [
        TriggerLogResponse(
            id=log.id,
            status=log.status,
            trigger_context=log.trigger_context,
            agent_response=log.agent_response,
            requires_approval=log.requires_approval,
            triggered_at=log.triggered_at.isoformat(),
            completed_at=None,
        )
        for log in logs
    ]


@router.post("/logs/{log_id}/approve")
async def approve_trigger(
    startup_id: UUID,
    log_id: UUID,
    decision: ApprovalDecision,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject a pending trigger"""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(TriggerLog).where(
            TriggerLog.id == log_id,
            TriggerLog.startup_id == startup_id,
            TriggerLog.status == TriggerLogStatus.AWAITING_APPROVAL,
        )
    )
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending trigger log not found"
        )
    
    log.approved_by = current_user.id
    log.approved_at = datetime.utcnow()
    log.approval_notes = decision.notes
    
    if decision.approved:
        log.status = TriggerLogStatus.APPROVED
        # TODO: Execute the trigger action
        logger.info("Trigger approved", log_id=str(log_id))
    else:
        log.status = TriggerLogStatus.REJECTED
        logger.info("Trigger rejected", log_id=str(log_id))
    
    await db.flush()
    
    return {
        "success": True,
        "status": log.status.value,
        "message": f"Trigger {'approved' if decision.approved else 'rejected'}"
    }
