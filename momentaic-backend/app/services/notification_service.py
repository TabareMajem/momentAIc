import json
import structlog
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pywebpush import webpush, WebPushException

from app.core.config import settings
from app.services.email_service import email_service
from app.models.user import User
from app.models.push_subscription import PushSubscription
from app.core.database import async_session_maker

logger = structlog.get_logger()

class NotificationService:
    """
    Unified Notification Service.
    Handles Email + Web Push.
    """
    
    def __init__(self):
        # Load VAPID keys from env or file
        self.vapid_private_key = settings.vapid_private_key_path or "private_key.pem"
        self.vapid_claims = {"sub": f"mailto:{settings.smtp_from_email or 'admin@momentaic.com'}"}

    async def notify_user(
        self, 
        user: User, 
        subject: str, 
        body: str, 
        action_url: str = "https://app.momentaic.com/dashboard",
        db: Optional[AsyncSession] = None
    ):
        """
        Send notification to user via all available channels.
        """
        results = {"email": False, "push": 0}
        
        # 1. Send Email
        if user.email:
            try:
                # Use send_email directly or templated if needed. 
                # For generic notifications, simple text is fine.
                sent = await email_service.send_email(
                    to_email=user.email,
                    subject=subject,
                    body=f"{body}\n\nView details: {action_url}"
                )
                results["email"] = sent
            except Exception as e:
                logger.error("NotificationService: Email failed", error=str(e))

        # 2. Send Push (if Db session provided to fetch subs)
        if db:
            try:
                # Fetch subscriptions
                subs_result = await db.execute(select(PushSubscription).where(PushSubscription.user_id == user.id))
                subscriptions = subs_result.scalars().all()
                
                payload = json.dumps({
                    "title": subject,
                    "body": body,
                    "url": action_url,
                    "icon": "/logo-new.png"
                })
                
                for sub in subscriptions:
                    try:
                        webpush(
                            subscription_info={
                                "endpoint": sub.endpoint,
                                "keys": {
                                    "p256dh": sub.p256dh,
                                    "auth": sub.auth
                                }
                            },
                            data=payload,
                            vapid_private_key=self.vapid_private_key,
                            vapid_claims=self.vapid_claims
                        )
                        results["push"] += 1
                    except WebPushException as ex:
                        if ex.response and ex.response.status_code == 410:
                            # Expired, delete
                            await db.delete(sub)
                            logger.info("NotificationService: Pruned expired subscription")
                        else:
                            logger.error("NotificationService: Push failed", error=str(ex))
                            
            except Exception as e:
                logger.error("NotificationService: Push orchestration failed", error=str(e))
        
        return results

    async def subscribe(self, db: AsyncSession, user_id: str, sub_info: Dict[str, Any]):
        """
        Register a push subscription.
        sub_info expected format: { endpoint: str, keys: { p256dh: str, auth: str } }
        """
        endpoint = sub_info.get("endpoint")
        keys = sub_info.get("keys", {})
        
        # Check if exists
        result = await db.execute(select(PushSubscription).where(
            PushSubscription.user_id == user_id,
            PushSubscription.endpoint == endpoint
        ))
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update keys if changed
            existing.p256dh = keys.get("p256dh")
            existing.auth = keys.get("auth")
        else:
            new_sub = PushSubscription(
                user_id=user_id,
                endpoint=endpoint,
                p256dh=keys.get("p256dh"),
                auth=keys.get("auth"),
                user_agent=sub_info.get("user_agent")
            )
            db.add(new_sub)
        
        await db.commit()
        return True

    async def notify_hitl_action(self, user: User, startup_name: str, action: Any):
        """
        Send a magic link approval email for a pending HITL action.
        """
        import jwt
        from app.core.config import settings
        from app.integrations.gmail import gmail_integration
        import os
        
        # 1. Generate Magic Links
        backend_url = os.environ.get("BACKEND_URL", "https://api.momentaic.com")
        if backend_url.endswith("/"): backend_url = backend_url[:-1]
        
        approve_token = jwt.encode({"action_id": str(action.id), "approve": True}, settings.SECRET_KEY, algorithm="HS256")
        reject_token = jwt.encode({"action_id": str(action.id), "approve": False}, settings.SECRET_KEY, algorithm="HS256")
        
        approve_url = f"{backend_url}/api/v1/hitl/magic-resolve?token={approve_token}"
        reject_url = f"{backend_url}/api/v1/hitl/magic-resolve?token={reject_token}"
        
        # 2. Build Buttons
        buttons_html = f'''
        <a href="{approve_url}" style="background-color: #10b981; color: #ffffff !important; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: 600; font-size: 14px; display: inline-block;">✓ Approve Action</a>
        <a href="{reject_url}" style="background-color: transparent; border: 1px solid #ef4444; color: #ef4444 !important; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: 600; font-size: 14px; display: inline-block; margin-left: 12px;">✕ Reject</a>
        '''
        
        # 3. Dispatch via Agent Router
        try:
             await gmail_integration.execute_action("send_email", {
                 "to": user.email,
                 "subject": f"✋ Review Required: {action.title}",
                 "body": f"{action.description}",
                 "priority": "urgent", # HITL approvals should bypass the digest queue
                 "agent_name": action.source_agent,
                 "action_buttons": buttons_html
             })
             logger.info(f"NotificationService: HITL approval email sent to {user.email}")
        except Exception as e:
             logger.error("Failed to send HITL magic link email", error=str(e))

        # 4. Schedule SMS Escalation for critical/urgent/high-priority items
        try:
            priority = getattr(action, 'priority', None)
            priority_val = priority.value if hasattr(priority, 'value') else str(priority)
            if priority_val in ("urgent", "high"):
                startup_id = getattr(action, 'startup_id', None)
                if startup_id:
                    await self.schedule_sms_escalation(
                        action_item_id=str(action.id),
                        startup_id=str(startup_id),
                        delay_minutes=15
                    )
        except Exception as esc_err:
            logger.warning("SMS escalation scheduling failed", error=str(esc_err))

    async def process_new_action_items(self, db: AsyncSession, new_items: List[Any]):
        """
        Takes a list of tuples (Startup, ActionItem) and securely dispatches
        magic link emails for any pending items. Safe to call post-commit.
        """
        for startup, item in new_items:
            if getattr(item, 'status', None) == "pending" or getattr(item, 'status', None) == getattr(__import__('app.models.action_item', fromlist=['ActionStatus']).ActionStatus, 'pending', "pending"):
                owner_result = await db.execute(select(User).where(User.id == startup.owner_id))
                owner = owner_result.scalar_one_or_none()
                if owner:
                     await self.notify_hitl_action(owner, startup.name, item)

    async def dispatch_agent_alert(
        self, 
        startup_id: Any, 
        agent_name: str, 
        channel: str, 
        dispatch_func: Any, 
        *args, **kwargs
    ) -> Any:
        """
        Central routing hub for proactive agent alerts.
        Checks the Startup's notification preferences before dispatching.
        Preferences format: settings.notification_preferences = {"FinanceCFOAgent": {"slack": false, "email": true}}
        """
        from app.models.startup import Startup
        
        async with async_session_maker() as db:
            startup_result = await db.execute(select(Startup).where(Startup.id == startup_id))
            startup = startup_result.scalar_one_or_none()
            
            if startup:
                settings = dict(startup.settings or {})
                prefs = settings.get("notification_preferences", {})
                
                # Check specifics (default True if unset to prevent missing alerts)
                agent_prefs = prefs.get(agent_name, {})
                channel_enabled = agent_prefs.get(channel.lower(), True)
                
                if not channel_enabled:
                    logger.info(f"NotificationService: Gated {channel} alert from {agent_name} for Startup {startup.name} due to preferences.")
                    return {"success": False, "gated": True, "reason": "user_preferences"}
        
        # If passed, invoke the underlying dispatch function (e.g. gmail_integration.execute_action)
        return await dispatch_func(*args, **kwargs)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SMS URGENCY ESCALATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def schedule_sms_escalation(self, action_item_id: str, startup_id: str, delay_minutes: int = 15):
        """
        Schedule a delayed SMS escalation for a critical alert.
        Stores a Redis key that expires after the delay.
        The periodic check_sms_escalations() job will pick it up.
        """
        try:
            from app.core.redis_client import redis_client
            import json, time

            escalation_key = f"sms_escalation:{action_item_id}"
            escalation_data = json.dumps({
                "action_item_id": action_item_id,
                "startup_id": startup_id,
                "scheduled_at": time.time(),
                "escalate_after": time.time() + (delay_minutes * 60),
            })

            # Store with no TTL — the check job will delete it after escalation or resolution
            await redis_client.set(escalation_key, escalation_data)
            logger.info(f"SMS escalation scheduled for action {action_item_id} in {delay_minutes} minutes")

        except Exception as e:
            logger.error("Failed to schedule SMS escalation", error=str(e))

    async def check_sms_escalations(self):
        """
        Periodic job (runs every 5 minutes).
        Scans for pending SMS escalation keys, checks if the ActionItem is still
        unresolved past the delay window, and sends an SMS to the founder.
        """
        try:
            from app.core.redis_client import redis_client
            from app.models.action_item import ActionItem, ActionStatus
            from app.models.startup import Startup
            from app.services.twilio_service import twilio_service
            import json, time

            # Find all escalation keys
            keys = []
            async for key in redis_client.scan_iter(match="sms_escalation:*"):
                keys.append(key)

            if not keys:
                return

            logger.info(f"SMS Escalation Check: {len(keys)} pending escalations")

            async with async_session_maker() as db:
                for key in keys:
                    try:
                        raw = await redis_client.get(key)
                        if not raw:
                            continue

                        data = json.loads(raw)
                        escalate_after = data.get("escalate_after", 0)
                        action_item_id = data.get("action_item_id")

                        # Not yet time to escalate
                        if time.time() < escalate_after:
                            continue

                        # Check if the ActionItem is still pending
                        from sqlalchemy import select
                        result = await db.execute(
                            select(ActionItem).where(ActionItem.id == action_item_id)
                        )
                        action = result.scalar_one_or_none()

                        if not action:
                            await redis_client.delete(key)
                            continue

                        # If already resolved, clean up
                        if action.status != ActionStatus.pending:
                            await redis_client.delete(key)
                            logger.info(f"SMS Escalation cancelled — action {action_item_id} already {action.status.value}")
                            continue

                        # Still pending → escalate via SMS
                        startup_result = await db.execute(
                            select(Startup).where(Startup.id == action.startup_id)
                        )
                        startup = startup_result.scalar_one_or_none()

                        if not startup:
                            await redis_client.delete(key)
                            continue

                        owner_result = await db.execute(
                            select(User).where(User.id == startup.owner_id)
                        )
                        owner = owner_result.scalar_one_or_none()

                        if not owner:
                            await redis_client.delete(key)
                            continue

                        # Check if SMS is enabled for this agent
                        prefs = dict(startup.settings or {}).get("notification_preferences", {})
                        agent_prefs = prefs.get(action.source_agent, {})
                        sms_enabled = agent_prefs.get("sms", True)  # Default TRUE for critical escalations

                        if not sms_enabled:
                            await redis_client.delete(key)
                            logger.info(f"SMS escalation suppressed by preferences for {action.source_agent}")
                            continue

                        # Get phone number from user profile or startup settings
                        phone = getattr(owner, 'phone', None) or dict(startup.settings or {}).get("founder_phone")

                        if not phone:
                            logger.warning(f"No phone number found for founder of {startup.name}, cannot escalate via SMS")
                            await redis_client.delete(key)
                            continue

                        # SEND THE SMS
                        sms_body = (
                            f"🚨 URGENT — {startup.name}\n"
                            f"{action.title}\n"
                            f"{action.description[:200]}\n\n"
                            f"This alert has been pending for 15+ minutes. "
                            f"Reply APPROVE or log in to resolve."
                        )

                        sent = await twilio_service.send_sms(to_phone=phone, message=sms_body)

                        if sent:
                            logger.info(f"SMS escalation sent for action {action_item_id} to {phone}")
                        else:
                            logger.warning(f"SMS escalation failed for action {action_item_id}")

                        # Clean up — don't re-escalate
                        await redis_client.delete(key)

                    except Exception as inner_err:
                        logger.error("SMS escalation check error for single key", error=str(inner_err))

        except Exception as e:
            logger.error("SMS escalation check failed", error=str(e))

# Singleton
notification_service = NotificationService()

