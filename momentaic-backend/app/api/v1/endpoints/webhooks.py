import structlog
from fastapi import APIRouter, Request, HTTPException, status, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, Dict, Any
import stripe

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.startup import Startup
from app.triggers.engine import TriggerEngine

logger = structlog.get_logger()
router = APIRouter(tags=["webhooks"])

# Configuration (should ideally come from settings)
YOKAIZEN_WEBHOOK_KEY = "sk_dev_momentaic_123"

class WebhookPayload(BaseModel):
    event: str
    data: Dict[str, Any]

@router.post("/yokaizen")
async def yokaizen_webhook(
    payload: WebhookPayload,
    x_yokaizen_webhook_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingests execution signals from the Yokaizen AgentExecutor.
    """
    if x_yokaizen_webhook_key != YOKAIZEN_WEBHOOK_KEY:
        logger.warning("Unauthorized webhook attempt from Yokaizen", provided_key=x_yokaizen_webhook_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Webhook Secret"
        )

    logger.info("Received Yokaizen Webhook", webhook_event=payload.event, data=payload.data)

    if payload.event == "task.completed":
        job_id = payload.data.get("job_id")
        agent = payload.data.get("agent")
        result = payload.data.get("result_payload", {})
        
        # Here we would update the Momentaic DB with the output (e.g., video_url)
        logger.info(f"Task {job_id} by {agent} completed.", result=result)

    elif payload.event == "lead.captured":
        character_id = payload.data.get("character_id")
        lead_email = payload.data.get("lead_email")
        sentiment = payload.data.get("sentiment")
        startup_id = payload.data.get("startup_id")
        
        logger.info(f"Lead captured for {character_id}: {lead_email} ({sentiment})")
        
        if startup_id:
            # Trigger Proactive Agent Engine (Phase 14 Cross-Platform Reflex)
            trigger_context = {
                "event": "yokaizen.lead.captured",
                "event_data": payload.data,
                "user_email": lead_email
            }
            engine = TriggerEngine(db)
            await engine.evaluate_startup_triggers(
                startup_id=startup_id,
                data_context=trigger_context
            )
            logger.info("Yokaizen TriggerEngine evaluation complete", startup_id=startup_id)
        else:
            logger.warning("Yokaizen lead captured but no startup_id mapped for Momentaic proactivity.")

    else:
        logger.warning("Unknown webhook event type", event=payload.event)

    return {"status": "accepted"}

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingests Stripe webhooks and evaluates proactive triggers (Phase 20).
    """
    if not settings.stripe_webhook_secret or not settings.stripe_secret_key:
        logger.warning("Stripe credentials not configured for webhooks")
        return {"status": "ignored"}

    stripe.api_key = settings.stripe_secret_key
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except ValueError as e:
        logger.error("Invalid Stripe payload", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid Stripe signature", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid signature")

    logger.info("Received Stripe Webhook", event_type=event["type"])
    
    # Extract customer ID to look up the Startup
    data_obj = event["data"]["object"]
    customer_id = data_obj.get("customer")
    
    if not customer_id:
        return {"status": "accepted", "message": "No customer ID attached"}
        
    # Find the corresponding User and their Startup
    user_res = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
    user = user_res.scalar_one_or_none()
    
    if user:
        # Get active startup for user
        startup_res = await db.execute(select(Startup).where(Startup.owner_id == user.id))
        user_startup = startup_res.scalars().first()
        
        if user_startup:
            # Trigger Proactive Agent Engine (Phase 20 Reflex System)
            trigger_context = {
                "event": f"stripe.{event['type']}",
                "event_data": data_obj,
                "user_email": user.email
            }
            engine = TriggerEngine(db)
            await engine.evaluate_startup_triggers(
                startup_id=user_startup.id,
                data_context=trigger_context
            )
            logger.info("Stripe TriggerEngine evaluation complete", startup_id=str(user_startup.id))

    return {"status": "success"}
