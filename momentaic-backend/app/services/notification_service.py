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

# Singleton
notification_service = NotificationService()
