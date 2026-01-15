"""
Self-Hosted Email Outreach System
Native email outreach without external tools like Instantly.ai
Uses existing SMTP/SendGrid/Resend integration
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import structlog
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = structlog.get_logger()


class EmailStatus(str, Enum):
    """Email delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    REPLIED = "replied"


class OutreachEmail(BaseModel):
    """An email in an outreach sequence."""
    id: str
    campaign_id: str
    to_email: EmailStr
    to_name: str
    subject: str
    body_html: str
    body_text: str
    sequence_step: int = 1
    status: EmailStatus = EmailStatus.PENDING
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None


class OutreachCampaign(BaseModel):
    """A complete outreach campaign."""
    id: str
    name: str
    target_region: str
    total_recipients: int
    emails_sent: int = 0
    emails_opened: int = 0
    emails_replied: int = 0
    status: str = "active"
    created_at: datetime


class SelfHostedOutreach:
    """
    Self-hosted email outreach system.
    
    Features:
    - No external dependencies (Instantly.ai, SmartLead, etc.)
    - Uses existing SMTP or transactional email provider
    - Rate limiting to avoid spam filters
    - Sequence automation
    - Basic tracking (opens, clicks via pixel)
    """
    
    # Rate limits to avoid spam
    MAX_EMAILS_PER_HOUR = 50
    MAX_EMAILS_PER_DAY = 500
    DELAY_BETWEEN_EMAILS_SECONDS = 30
    
    def __init__(self):
        self._campaigns: Dict[str, OutreachCampaign] = {}
        self._email_queue: List[OutreachEmail] = []
        self._sent_today = 0
        self._sent_this_hour = 0
        self._last_reset_hour = datetime.utcnow().hour
        self._last_reset_day = datetime.utcnow().date()
    
    async def create_campaign(
        self,
        name: str,
        recipients: List[Dict[str, str]],
        subject_template: str,
        body_template: str,
        target_region: str = "US"
    ) -> OutreachCampaign:
        """
        Create a new outreach campaign.
        
        Args:
            name: Campaign name
            recipients: List of {email, name, ...} dicts
            subject_template: Email subject with {placeholders}
            body_template: Email body with {placeholders}
            target_region: Target region for tracking
        
        Returns:
            Created campaign
        """
        campaign_id = f"camp_{datetime.utcnow().timestamp()}"
        
        campaign = OutreachCampaign(
            id=campaign_id,
            name=name,
            target_region=target_region,
            total_recipients=len(recipients),
            created_at=datetime.utcnow()
        )
        
        self._campaigns[campaign_id] = campaign
        
        # Queue emails with staggered send times
        send_time = datetime.utcnow()
        for i, recipient in enumerate(recipients):
            # Personalize
            subject = self._personalize(subject_template, recipient)
            body = self._personalize(body_template, recipient)
            
            email = OutreachEmail(
                id=f"email_{campaign_id}_{i}",
                campaign_id=campaign_id,
                to_email=recipient["email"],
                to_name=recipient.get("name", ""),
                subject=subject,
                body_html=body,
                body_text=self._html_to_text(body),
                scheduled_at=send_time
            )
            
            self._email_queue.append(email)
            send_time += timedelta(seconds=self.DELAY_BETWEEN_EMAILS_SECONDS)
        
        logger.info(
            "Outreach campaign created",
            campaign_id=campaign_id,
            recipients=len(recipients)
        )
        
        return campaign
    
    def _personalize(self, template: str, data: Dict[str, str]) -> str:
        """Replace {placeholders} with actual values."""
        result = template
        for key, value in data.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def _html_to_text(self, html: str) -> str:
        """Simple HTML to text conversion."""
        import re
        text = re.sub(r'<br\s*/?>', '\n', html)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()
    
    async def send_email(self, email: OutreachEmail) -> bool:
        """
        Send a single email via configured provider.
        
        Uses:
        1. SendGrid (if SENDGRID_API_KEY set)
        2. Resend (if RESEND_API_KEY set)
        3. SMTP fallback
        """
        # Check rate limits
        self._check_rate_limits()
        
        if self._sent_today >= self.MAX_EMAILS_PER_DAY:
            logger.warning("Daily email limit reached")
            return False
        
        if self._sent_this_hour >= self.MAX_EMAILS_PER_HOUR:
            logger.warning("Hourly email limit reached")
            return False
        
        success = False
        
        # Try SendGrid first
        if hasattr(settings, 'sendgrid_api_key') and settings.sendgrid_api_key:
            success = await self._send_via_sendgrid(email)
        # Try Resend
        elif hasattr(settings, 'resend_api_key') and settings.resend_api_key:
            success = await self._send_via_resend(email)
        # Fallback to SMTP
        else:
            success = await self._send_via_smtp(email)
        
        if success:
            email.status = EmailStatus.SENT
            email.sent_at = datetime.utcnow()
            self._sent_today += 1
            self._sent_this_hour += 1
            
            # Update campaign stats
            if email.campaign_id in self._campaigns:
                self._campaigns[email.campaign_id].emails_sent += 1
        
        return success
    
    def _check_rate_limits(self):
        """Reset rate limit counters if needed."""
        now = datetime.utcnow()
        
        if now.hour != self._last_reset_hour:
            self._sent_this_hour = 0
            self._last_reset_hour = now.hour
        
        if now.date() != self._last_reset_day:
            self._sent_today = 0
            self._last_reset_day = now.date()
    
    async def _send_via_sendgrid(self, email: OutreachEmail) -> bool:
        """Send via SendGrid API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {settings.sendgrid_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "personalizations": [{"to": [{"email": email.to_email, "name": email.to_name}]}],
                        "from": {"email": "support@momentaic.com", "name": "MomentAIc Team"},
                        "subject": email.subject,
                        "content": [
                            {"type": "text/plain", "value": email.body_text},
                            {"type": "text/html", "value": email.body_html}
                        ]
                    }
                )
                return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return False
    
    async def _send_via_resend(self, email: OutreachEmail) -> bool:
        """Send via Resend API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.resend_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": "MomentAIc <support@momentaic.com>",
                        "to": [email.to_email],
                        "subject": email.subject,
                        "html": email.body_html,
                        "text": email.body_text
                    }
                )
                return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Resend error: {e}")
            return False
    
    async def _send_via_smtp(self, email: OutreachEmail) -> bool:
        """Send via SMTP (fallback)."""
        try:
            smtp_host = getattr(settings, 'smtp_host', 'smtp.gmail.com')
            smtp_port = getattr(settings, 'smtp_port', 587)
            smtp_user = getattr(settings, 'smtp_user', '')
            smtp_pass = getattr(settings, 'smtp_password', '')
            
            if not smtp_user or not smtp_pass:
                logger.warning("SMTP not configured")
                return False
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = email.subject
            msg["From"] = f"Tabare from MomentAIc <{smtp_user}>"
            msg["To"] = email.to_email
            
            msg.attach(MIMEText(email.body_text, "plain"))
            msg.attach(MIMEText(email.body_html, "html"))
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, email.to_email, msg.as_string())
            
            return True
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False
    
    async def process_queue(self):
        """Process the email queue (call periodically)."""
        now = datetime.utcnow()
        
        pending = [e for e in self._email_queue if e.status == EmailStatus.PENDING and e.scheduled_at <= now]
        
        for email in pending[:10]:  # Process 10 at a time
            await self.send_email(email)
            await asyncio.sleep(2)  # Small delay between sends
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics."""
        if campaign_id not in self._campaigns:
            return {}
        
        campaign = self._campaigns[campaign_id]
        return {
            "id": campaign.id,
            "name": campaign.name,
            "total": campaign.total_recipients,
            "sent": campaign.emails_sent,
            "opened": campaign.emails_opened,
            "replied": campaign.emails_replied,
            "open_rate": campaign.emails_opened / max(campaign.emails_sent, 1),
            "reply_rate": campaign.emails_replied / max(campaign.emails_sent, 1)
        }


# Singleton
outreach_service = SelfHostedOutreach()
