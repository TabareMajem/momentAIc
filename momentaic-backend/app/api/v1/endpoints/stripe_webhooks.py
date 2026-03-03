"""
Stripe Webhook Endpoint
Receives real-time events from Stripe and triggers proactive CFO Agent actions.
Supports: invoice.payment_failed, customer.subscription.deleted, charge.refunded, charge.succeeded
"""

import hmac
import hashlib
import json
import structlog
from fastapi import APIRouter, Request, HTTPException

logger = structlog.get_logger()

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Receive Stripe webhook events and dispatch to agents.
    
    Configure in Stripe Dashboard → Developers → Webhooks:
    URL: https://api.momentaic.com/api/v1/webhooks/stripe
    Events: invoice.payment_failed, customer.subscription.deleted, charge.refunded, charge.succeeded
    """
    import os
    from app.core.database import async_session_maker
    from sqlalchemy import select
    from app.models.startup import Startup
    from app.models.user import User

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # ── Verify Signature (if configured) ──────────────────────
    if webhook_secret and sig_header:
        try:
            import stripe
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except Exception as e:
            logger.error("Stripe webhook signature verification failed", error=str(e))
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        # Fallback: parse raw (dev mode)
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = event.get("type", "")
    event_data = event.get("data", {}).get("object", {})

    logger.info(f"Stripe Webhook received: {event_type}", event_id=event.get("id"))

    # ── Route to CFO Agent ────────────────────────────────────
    try:
        async with async_session_maker() as db:
            # Find the startup that owns this Stripe account
            # Look for startups with Stripe credentials matching this event
            result = await db.execute(select(Startup).limit(50))
            startups = result.scalars().all()

            for startup in startups:
                # Check if this startup has Stripe integration configured
                settings = dict(startup.settings or {})
                integrations = settings.get("integrations", {})
                stripe_config = integrations.get("stripe", {})

                if not stripe_config.get("enabled"):
                    continue

                # Build context for the agent
                startup_context = {
                    "id": str(startup.id),
                    "name": startup.name,
                    "industry": startup.industry,
                    "metrics": dict(startup.metrics or {}),
                }

                # Get founder email
                owner_result = await db.execute(select(User).where(User.id == startup.owner_id))
                owner = owner_result.scalar_one_or_none()
                if owner:
                    startup_context["founder_email"] = owner.email

                # ── Handle Event Types ────────────────────────
                if event_type == "invoice.payment_failed":
                    invoice_id = event_data.get("id")
                    customer_email = event_data.get("customer_email", "Unknown")
                    amount = event_data.get("amount_due", 0) / 100

                    logger.warning(f"💳 Payment failed for {customer_email}: ${amount}")

                    # Trigger CFO agent autonomous action
                    from app.agents.finance_cfo_agent import FinanceCFOAgent
                    cfo = FinanceCFOAgent()
                    await cfo.initialize()
                    await cfo.autonomous_action(
                        action={
                            "type": "failed_payment_retry",
                            "invoice_id": invoice_id,
                            "customer_email": customer_email,
                            "amount": amount,
                            "severity": "critical",
                        },
                        startup_context=startup_context,
                    )

                elif event_type == "customer.subscription.deleted":
                    customer_id = event_data.get("customer")
                    plan = event_data.get("plan", {}).get("nickname", "Unknown Plan")
                    amount = event_data.get("plan", {}).get("amount", 0) / 100

                    logger.warning(f"📉 Subscription canceled: {customer_id} — {plan} (${amount}/mo)")

                    from app.agents.finance_cfo_agent import FinanceCFOAgent
                    cfo = FinanceCFOAgent()
                    await cfo.initialize()
                    await cfo.autonomous_action(
                        action={
                            "type": "revenue_anomaly_detected",
                            "event": "subscription_canceled",
                            "customer_id": customer_id,
                            "plan": plan,
                            "mrr_impact": -amount,
                            "severity": "warning",
                        },
                        startup_context=startup_context,
                    )

                elif event_type == "charge.refunded":
                    amount = event_data.get("amount_refunded", 0) / 100
                    customer = event_data.get("customer", "Unknown")

                    logger.warning(f"💸 Charge refunded: ${amount} from {customer}")

                    from app.agents.finance_cfo_agent import FinanceCFOAgent
                    cfo = FinanceCFOAgent()
                    await cfo.initialize()
                    await cfo.autonomous_action(
                        action={
                            "type": "revenue_anomaly_detected",
                            "event": "charge_refunded",
                            "customer_id": customer,
                            "amount_refunded": amount,
                            "severity": "warning",
                        },
                        startup_context=startup_context,
                    )

                elif event_type == "charge.succeeded":
                    amount = event_data.get("amount", 0) / 100
                    logger.info(f"✅ Charge succeeded: ${amount}")
                    # No agent action needed — just log for the activity stream
                    from app.services.activity_stream import activity_stream
                    await activity_stream.publish(
                        startup_id=str(startup.id),
                        event_type="revenue_event",
                        title=f"💰 Payment received: ${amount:.2f}",
                        description=f"Stripe charge succeeded for {event_data.get('customer_email', 'customer')}",
                        agent="FinanceCFOAgent",
                    )

                # Only process for the first matching startup
                break

    except Exception as e:
        logger.error("Stripe webhook processing failed", error=str(e), event_type=event_type)

    # Always return 200 to avoid Stripe retries
    return {"received": True, "event_type": event_type}
