
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.action_item import ActionItem, ActionStatus
from app.models.startup import Startup

router = APIRouter()

@router.get("/pending", response_model=List[dict])
async def get_pending_actions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all pending proactive actions for the user's startups.
    """
    # 1. Get user's startups
    startup_ids = [s.id for s in current_user.startups]
    
    if not startup_ids:
        return []

    # 2. Query pending items
    result = await db.execute(
        select(ActionItem)
        .where(ActionItem.startup_id.in_(startup_ids))
        .where(ActionItem.status == ActionStatus.pending)
        .order_by(ActionItem.priority.desc(), ActionItem.created_at.desc())
    )
    items = result.scalars().all()
    
    # Simple list return (could be Pydantic model)
    return [
        {
            "id": str(item.id),
            "source": item.source_agent,
            "title": item.title,
            "description": item.description,
            "priority": item.priority.value,
            "payload": item.payload,
            "created_at": item.created_at.isoformat()
        }
        for item in items
    ]

@router.post("/{action_id}/approve")
async def approve_action(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Approve an action item. This triggers execution (mocked for now).
    """
    # 1. Get item and verify ownership
    result = await db.execute(select(ActionItem).where(ActionItem.id == action_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Action not found")
        
    # Verify accessible
    accessible = False
    for s in current_user.startups:
        if s.id == item.startup_id:
            accessible = True
            break
            
    if not accessible:
         raise HTTPException(status_code=403, detail="Not authorized")
         
    # 2. Execute (Mock logic based on source)
    execution_log = {}
    if item.source_agent == "SalesHunter":
        # In real life: Queue emails in OutreachMessage table
        execution_log = {"message": "5 emails queued for sending via Gmail API"}
    elif item.source_agent == "MarketingAgent":
        # In real life: Post to Twitter/Linkedin
        execution_log = {"message": "Thread scheduled for posting at optimal time"}
        
    # 3. Update Status
    item.status = ActionStatus.approved
    item.execution_result = execution_log
    item.updated_at = current_user.updated_at # trick to just refresh timestamp
    
    await db.commit()
    
    return {"status": "approved", "result": execution_log}

@router.post("/{action_id}/reject")
async def reject_action(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Reject an action item.
    """
    result = await db.execute(select(ActionItem).where(ActionItem.id == action_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Action not found")
        
    # Verify accessible
    # (Simplified check same as approve)
    accessible = any(s.id == item.startup_id for s in current_user.startups)
    if not accessible:
         raise HTTPException(status_code=403, detail="Not authorized")

    item.status = ActionStatus.rejected
    await db.commit()
    
    return {"status": "rejected"}
