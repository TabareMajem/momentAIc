"""
Email Service
Send emails via SMTP or SendGrid
"""

from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import structlog
from jinja2 import Environment, PackageLoader, select_autoescape

from app.core.config import settings

logger = structlog.get_logger()

# Jinja2 template environment
try:
    jinja_env = Environment(
        loader=PackageLoader("app", "templates/email"),
        autoescape=select_autoescape(["html", "xml"]),
    )
except Exception:
    jinja_env = None


class EmailService:
    """
    Email sending service with template support.
    """
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email or settings.smtp_user or "noreply@momentaic.com"
        self.from_name = settings.smtp_from_name or "MomentAIc"
    
    @property
    def is_configured(self) -> bool:
        """Check if email is configured"""
        return bool(self.smtp_host and self.smtp_user)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
    ) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            cc: Optional CC recipients
            bcc: Optional BCC recipients
            reply_to: Optional reply-to address
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.warning("Email not configured, skipping send")
            return False
        
        try:
            # Create message
            if html_body:
                message = MIMEMultipart("alternative")
                message.attach(MIMEText(body, "plain"))
                message.attach(MIMEText(html_body, "html"))
            else:
                message = MIMEText(body, "plain")
            
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            if cc:
                message["Cc"] = ", ".join(cc)
            if reply_to:
                message["Reply-To"] = reply_to
            
            # Collect all recipients
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Send via SMTP
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True,
            )
            
            logger.info("Email sent", to=to_email, subject=subject)
            return True
            
        except Exception as e:
            logger.error("Email send failed", to=to_email, error=str(e))
            return False
    
    async def send_template_email(
        self,
        to_email: str,
        template_name: str,
        subject: str,
        context: Dict[str, Any],
        **kwargs,
    ) -> bool:
        """
        Send an email using a Jinja2 template.
        
        Args:
            to_email: Recipient email
            template_name: Name of the template file
            subject: Email subject
            context: Template context variables
            **kwargs: Additional arguments for send_email
        """
        if not jinja_env:
            logger.warning("Jinja2 templates not available")
            return await self.send_email(
                to_email=to_email,
                subject=subject,
                body=str(context),
                **kwargs,
            )
        
        try:
            # Render HTML template
            html_template = jinja_env.get_template(f"{template_name}.html")
            html_body = html_template.render(**context)
            
            # Try to render text template
            try:
                text_template = jinja_env.get_template(f"{template_name}.txt")
                text_body = text_template.render(**context)
            except Exception:
                # Generate plain text from HTML
                import re
                text_body = re.sub(r'<[^>]+>', '', html_body)
            
            return await self.send_email(
                to_email=to_email,
                subject=subject,
                body=text_body,
                html_body=html_body,
                **kwargs,
            )
            
        except Exception as e:
            logger.error("Template email failed", template=template_name, error=str(e))
            return False
    
    async def send_welcome_email(self, to_email: str, full_name: str) -> bool:
        """Send welcome email to new user"""
        return await self.send_template_email(
            to_email=to_email,
            template_name="welcome",
            subject=f"Welcome to {self.from_name}!",
            context={
                "name": full_name,
                "app_name": self.from_name,
            },
        )
    
    async def send_verification_email(
        self, to_email: str, full_name: str, verification_link: str
    ) -> bool:
        """Send email verification link"""
        return await self.send_template_email(
            to_email=to_email,
            template_name="verify_email",
            subject="Verify your email address",
            context={
                "name": full_name,
                "verification_link": verification_link,
                "app_name": self.from_name,
            },
        )
    
    async def send_password_reset_email(
        self, to_email: str, full_name: str, reset_link: str
    ) -> bool:
        """Send password reset link"""
        return await self.send_template_email(
            to_email=to_email,
            template_name="password_reset",
            subject="Reset your password",
            context={
                "name": full_name,
                "reset_link": reset_link,
                "app_name": self.from_name,
            },
        )
    
    async def send_credit_low_warning(
        self, to_email: str, full_name: str, current_balance: int
    ) -> bool:
        """Send low credit balance warning"""
        return await self.send_template_email(
            to_email=to_email,
            template_name="low_credits",
            subject="Low credit balance warning",
            context={
                "name": full_name,
                "balance": current_balance,
                "app_name": self.from_name,
            },
        )
    
    async def send_workflow_completed(
        self,
        to_email: str,
        full_name: str,
        workflow_name: str,
        status: str,
        outputs: Dict[str, Any] = None,
    ) -> bool:
        """Send workflow completion notification"""
        return await self.send_template_email(
            to_email=to_email,
            template_name="workflow_completed",
            subject=f"Workflow '{workflow_name}' {status}",
            context={
                "name": full_name,
                "workflow_name": workflow_name,
                "status": status,
                "outputs": outputs or {},
                "app_name": self.from_name,
            },
        )
    
    async def send_approval_request(
        self,
        to_email: str,
        full_name: str,
        workflow_name: str,
        node_label: str,
        content: Dict[str, Any],
        approval_link: str,
    ) -> bool:
        """Send human-in-the-loop approval request"""
        return await self.send_template_email(
            to_email=to_email,
            template_name="approval_request",
            subject=f"Approval needed: {workflow_name}",
            context={
                "name": full_name,
                "workflow_name": workflow_name,
                "node_label": node_label,
                "content": content,
                "approval_link": approval_link,
                "app_name": self.from_name,
            },
        )


# Lazy singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service singleton (lazy initialization)"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


# For backward compatibility - lazy property
class _LazyEmailService:
    _instance = None
    
    def __getattr__(self, name):
        if self._instance is None:
            self._instance = EmailService()
        return getattr(self._instance, name)

email_service = _LazyEmailService()
