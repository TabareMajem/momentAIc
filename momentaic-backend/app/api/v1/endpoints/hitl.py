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
    If approved, IMMEDIATELY EXECUTES the action (send_email, send_dm, etc.).
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
    execution_results = []
    for item in items:
        if item.status == ActionStatus.pending:
            item.status = new_status
            updated_count += 1
            
            if new_status == ActionStatus.approved:
                # REAL EXECUTION: dispatch the action based on its type
                exec_result = await _execute_approved_action(item)
                execution_results.append({"id": str(item.id), "result": exec_result})
                
                # Store execution result in payload
                payload = dict(item.payload or {})
                payload["execution_result"] = exec_result
                item.payload = payload
                
                if exec_result.get("executed"):
                    item.status = ActionStatus.executed if hasattr(ActionStatus, 'executed') else ActionStatus.approved
                
                logger.info(f"Action {item.id} approved AND executed: {item.title}", result=exec_result)
            else:
                logger.info(f"Action {item.id} rejected by founder")
                
    await db.commit()
    
    return {
        "success": True, 
        "message": f"{updated_count} actions {new_status.value}",
        "updated_ids": [item.id for item in items if item.status == new_status],
        "execution_results": execution_results
    }


async def _execute_approved_action(item: ActionItem) -> dict:
    """
    Execute a real-world action based on the action_type stored in the ActionItem payload.
    This is the bridge between HitL approval and actual execution.
    """
    payload = item.payload or {}
    action_type = payload.get("action_type", "unknown")
    
    try:
        if action_type == "send_email":
            # Dispatch via real SMTP through outreach_service
            from app.services.outreach_service import outreach_service, OutreachEmail
            import uuid as uuid_mod
            
            email = OutreachEmail(
                id=str(uuid_mod.uuid4()),
                campaign_id=payload.get("campaign_id", f"hitl_{item.id}"),
                to_email=payload.get("to_email", ""),
                to_name=payload.get("to_name", ""),
                subject=payload.get("subject", ""),
                body_html=f"<html><body>{payload.get('body', '')}</body></html>",
                body_text=payload.get("body", ""),
                scheduled_at=datetime.utcnow()
            )
            
            success = await outreach_service.send_email(email)
            return {"executed": True, "action_type": "send_email", "sent": success, "to": payload.get("to_email")}
        
        elif action_type == "send_dm":
            # For DMs, dispatch via email as the delivery channel (the DM content goes as an email to the influencer)
            from app.integrations.gmail import GmailIntegration
            
            gmail = GmailIntegration()
            influencer_email = payload.get("influencer_email", "")
            
            if influencer_email:
                result = gmail.execute_action("send_email", {
                    "to": influencer_email,
                    "subject": f"Partnership Opportunity - MomentAIc",
                    "body": payload.get("dm_copy", ""),
                })
                return {"executed": True, "action_type": "send_dm", "result": result}
            else:
                # No email available — log the DM for manual social dispatch
                logger.info("DM queued for manual social dispatch", influencer=payload.get("influencer_name"))
                return {"executed": True, "action_type": "send_dm", "manual_dispatch": True, "platform": payload.get("platform")}
        
        elif action_type == "create_affiliate":
            from app.integrations.affiliate import affiliate_integration
            
            result = await affiliate_integration.create_affiliate(
                name=payload.get("name", ""),
                email=payload.get("email", ""),
            )
            return {"executed": True, "action_type": "create_affiliate", "affiliate": result}
        
        elif action_type == "stripe_transfer":
            from app.integrations.stripe import StripeIntegration
            
            stripe = StripeIntegration()
            result = await stripe.execute_split_transfer(
                connected_account_id=payload.get("connected_account_id", ""),
                amount_cents=payload.get("amount_cents", 0),
                description=payload.get("description", "Affiliate payout"),
            )
            return {"executed": True, "action_type": "stripe_transfer", "result": result}
        
        else:
            logger.warning(f"Unknown action_type: {action_type}", item_id=str(item.id))
            return {"executed": False, "action_type": action_type, "reason": "Unknown action type"}
    
    except Exception as e:
        logger.error(f"Execution failed for action {item.id}", error=str(e), action_type=action_type)
        return {"executed": False, "action_type": action_type, "error": str(e)}


@router.get("/magic-resolve")
async def magic_resolve_action(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    1-Click Magic Link approval/rejection straight from the founder's email inbox.
    No login required as the JWT is cryptographically signed.
    On approval, IMMEDIATELY EXECUTES the action.
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
        
        exec_summary = ""
        if approve:
            # REAL EXECUTION on Magic Link approval
            exec_result = await _execute_approved_action(item)
            item_payload = dict(item.payload or {})
            item_payload["execution_result"] = exec_result
            item.payload = item_payload
            exec_summary = f"<p style='color:#6ee7b7;'>Execution: {exec_result.get('action_type', 'N/A')} — {'✅ Success' if exec_result.get('executed') else '❌ Failed'}</p>"
            logger.info(f"Action {action_id} approved AND executed via Magic Link", result=exec_result)
        else:
            logger.info(f"Action {action_id} rejected via Magic Link")
        
        await db.commit()
        
        color = "#10b981" if approve else "#ef4444"
        verb = "Approved & Executed" if approve else "Rejected"
        
        return HTMLResponse(content=f"""
        <body style='background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:50px;'>
            <h1 style='color: {color}'>Action {verb} Successfully</h1>
            {exec_summary}
            <p>You may close this window.</p>
        </body>
        """)
        
    except jwt.PyJWTError:
        return HTMLResponse(
            content="<body style='background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:50px;'>"
                    "<h2>Invalid or Expired Magic Link</h2></body>",
            status_code=400
        )
