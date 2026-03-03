"""
Human-in-the-Loop (HitL) Endpoints
Manage the queue of actions proposed by proactive autonomous agents.
"""
from typing import List
from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User
from app.models.action_item import ActionItem, ActionStatus

from pydantic import BaseModel
from datetime import datetime

logger = structlog.get_logger()
router = APIRouter()

# --- Schemas ---
class ActionItemResponse(BaseModel):
    id: UUID
    startup_id: UUID
    source_agent: str
    title: str
    description: str
    priority: str
    payload: dict
    status: ActionStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class ActionApprovalRequest(BaseModel):
    action_ids: List[UUID]
    approve: bool = True # False means reject

# --- Endpoints ---
@router.get("/startups/{startup_id}/actions", response_model=List[ActionItemResponse])
async def list_pending_actions(
    startup_id: UUID,
    status_filter: ActionStatus = ActionStatus.pending,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the queue of proactive agent actions for HitL review."""
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(ActionItem)
        .where(
            ActionItem.startup_id == startup_id,
            ActionItem.status == status_filter
        )
        .order_by(ActionItem.created_at.desc())
    )
    items = result.scalars().all()
    return items

@router.post("/startups/{startup_id}/actions/review")
async def review_actions(
    startup_id: UUID,
    request: ActionApprovalRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve or reject a batch of autonomous actions.
    If approved, they are marked for execution by the background task engine.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(ActionItem).where(
            ActionItem.id.in_(request.action_ids),
            ActionItem.startup_id == startup_id
        )
    )
    items = result.scalars().all()
    
    if not items:
        raise HTTPException(status_code=404, detail="Actions not found")
        
    new_status = ActionStatus.approved if request.approve else ActionStatus.rejected
    
    updated_count = 0
    for item in items:
        if item.status == ActionStatus.pending:
            item.status = new_status
            updated_count += 1
            
            if new_status == ActionStatus.approved:
                # In a full message queue architecture, we would emit to Celery/SQS here
                # For this MVP, the background agent loop or engine will pick up 'approved' items
                logger.info(f"Action {item.id} approved for execution: {item.title}")
            else:
                logger.info(f"Action {item.id} rejected by founder")
                
    await db.commit()
    
    return {
        "success": True, 
        "message": f"{updated_count} actions {new_status.value}",
        "updated_ids": [item.id for item in items if item.status == new_status]
    }

@router.get("/magic-resolve")
async def magic_resolve_action(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    1-Click Magic Link approval/rejection straight from the founder's email inbox.
    No login required as the JWT is cryptographically signed.
    """
    import jwt
    from fastapi.responses import HTMLResponse
    from app.core.config import settings
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        action_id = payload.get("action_id")
        approve = payload.get("approve", True)
        
        result = await db.execute(select(ActionItem).where(ActionItem.id == action_id))
        item = result.scalars().first()
        
        if not item or item.status != ActionStatus.pending:
            return HTMLResponse(
                content="<body style='background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:50px;'>"
                        "<h2>Link Expired or Already Resolved</h2><p>This action is no longer pending.</p></body>",
                status_code=400
            )
            
        new_status = ActionStatus.approved if approve else ActionStatus.rejected
        item.status = new_status
        await db.commit()
        
        # In a real environment we would trigger the engine, but this MVPs it as approved
        logger.info(f"Action {action_id} {'approved' if approve else 'rejected'} via Magic Link")
        
        color = "#10b981" if approve else "#ef4444"
        verb = "Approved" if approve else "Rejected"
        
        return HTMLResponse(content=f"""
        <body style='background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:50px;'>
            <h1 style='color: {color}'>Action {verb} Successfully</h1>
            <p>The agent will proceed accordingly. You may close this window.</p>
        </body>
        """)
        
    except jwt.PyJWTError:
        return HTMLResponse(
            content="<body style='background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:50px;'>"
                    "<h2>Invalid or Expired Magic Link</h2></body>",
            status_code=400
        )
