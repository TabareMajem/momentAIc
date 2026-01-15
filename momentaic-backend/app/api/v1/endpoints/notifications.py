
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.notification_service import notification_service

router = APIRouter()

@router.post("/subscribe", status_code=201)
async def subscribe_push(
    subscription: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Register a Web Push subscription.
    Payload: { endpoint: "...", keys: { p256dh: "...", auth: "..." } }
    """
    try:
        await notification_service.subscribe(db, str(current_user.id), subscription)
        return {"status": "subscribed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-push")
async def test_push(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Trigger a test push notification to yourself.
    """
    results = await notification_service.notify_user(
        user=current_user,
        subject="Test Notification",
        body="This is a test notification from the MomentAIc platform.",
        action_url="https://app.momentaic.com/dashboard",
        db=db
    )
    return results
