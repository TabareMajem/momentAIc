
"""
Gmail/SMTP Integration
Enables agents to actually SEND emails via SMTP.
"""
from typing import Dict, Any, List, Optional
import structlog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.integrations.base import BaseIntegration, IntegrationCredentials, SyncResult
from app.core.config import settings

logger = structlog.get_logger()

class GmailIntegration(BaseIntegration):
    """
    Gmail Integration via SMTP (Sending) and IMAP (Listening - TODO).
    """
    provider = "gmail"
    display_name = "Gmail"
    description = "Send and receive emails via Google Workspace"
    oauth_required = False # Using App Passwords for V1 simplicity
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        return "" # Not used for SMTP

    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        return IntegrationCredentials(access_token="smtp_only")

    async def refresh_tokens(self) -> IntegrationCredentials:
        return self.credentials

    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        """
        Sync emails (Read Inbox).
        """
        if data_types and "emails" in data_types:
            emails = self.check_unread_emails()
            return SyncResult(success=True, records_synced=len(emails), data={"emails": emails})
        return SyncResult(success=True, records_synced=0)

    def check_unread_emails(self) -> List[Dict[str, Any]]:
        """
        Connect to IMAP and fetch unseen emails.
        """
        import imaplib
        import email
        from email.header import decode_header

        username = getattr(settings, "GMAIL_USER", None)
        password = getattr(settings, "GMAIL_APP_PASSWORD", None)
        
        if not username or not password:
            logger.warning("GmailIntegration: Cannot check mail. Missing credentials.")
            return []

        found_emails = []
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(username, password)
            mail.select("inbox")

            # Search for Unseen
            status, messages = mail.search(None, "UNSEEN")
            if status != "OK":
                return []
            
            email_ids = messages[0].split()
            # Fetch last 5 max to avoid overload
            for e_id in email_ids[-5:]:
                res, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        
                        sender = msg.get("From")
                        found_emails.append({
                            "id": e_id.decode(),
                            "subject": subject,
                            "sender": sender,
                            "snippet": str(msg.get_payload())[:100]
                        })
            
            mail.close()
            mail.logout()
            logger.info(f"GmailIntegration: Found {len(found_emails)} unread emails.")
            return found_emails

        except Exception as e:
            logger.error(f"Gmail IMAP failed: {e}")
            return []

    async def listen_for_replies(self, db=None) -> List[Dict[str, Any]]:
        """
        Async IMAP listener: checks for new emails that look like replies
        to outbound SDR emails, and publishes ReplyReceived events.
        Called by the APScheduler every 5 minutes.
        """
        import asyncio
        
        # Run synchronous IMAP check in thread pool
        loop = asyncio.get_event_loop()
        emails = await loop.run_in_executor(None, self.check_unread_emails)
        
        if not emails:
            return []
        
        replies = []
        for email_data in emails:
            subject = email_data.get("subject", "")
            sender = email_data.get("sender", "")
            
            # Detect replies (Re: prefix or In-Reply-To header match)
            is_reply = subject.lower().startswith("re:") or "in-reply-to" in str(email_data)
            
            if is_reply:
                reply_event = {
                    "type": "reply_received",
                    "sender": sender,
                    "subject": subject,
                    "snippet": email_data.get("snippet", ""),
                    "email_id": email_data.get("id"),
                }
                replies.append(reply_event)
                
                # Publish to message bus for SDR agent to pick up
                if db:
                    try:
                        from app.services.message_bus import MessageBus
                        bus = MessageBus(db)
                        await bus.publish(
                            startup_id="system",
                            from_agent="gmail_listener",
                            topic="email.reply_received",
                            message_type="EVENT",
                            payload=reply_event,
                            priority="high",
                        )
                        logger.info("Reply event published", sender=sender, subject=subject)
                    except Exception as e:
                        logger.warning("Failed to publish reply event", error=str(e))
        
        logger.info(f"GmailIntegration: Processed {len(emails)} emails, {len(replies)} replies detected")
        return replies

        
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email actions"""
        if action == "send_email":
            priority = params.get("priority", "urgent")
            
            if priority in ("normal", "low"):
                recipient = params.get("to")
                try:
                    import json
                    from app.core.redis_client import redis_client
                    queue_key = f"email_digest_queue:{recipient}"
                    await redis_client.rpush(queue_key, json.dumps({
                        "subject": params.get("subject"),
                        "body": params.get("body"),
                        "html_body": params.get("html_body"),
                        "agent_name": params.get("agent_name", "Autonomous Agent")
                    }))
                    logger.info(f"GmailIntegration: Email queued for digest for {recipient}")
                    return {"success": True, "status": "queued", "recipient": recipient}
                except Exception as e:
                    logger.error(f"GmailIntegration: Queue failed, sending sync", error=str(e))
                    return self._send_email(params)
            else:
                return self._send_email(params)
        return {"success": False, "error": f"Unknown action: {action}"}

    def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an email via SMTP.
        Requires GMAIL_USER and GMAIL_APP_PASSWORD in env or credentials.
        """
        # 1. Get Credentials (Env fallback)
        username = getattr(settings, "GMAIL_USER", None)
        password = getattr(settings, "GMAIL_APP_PASSWORD", None)
        
        # Override if passed in params (for testing)
        username = params.get("sender_email", username)
        
        if not username or not password:
            return {"success": False, "error": "Missing GMAIL_USER or GMAIL_APP_PASSWORD"}

        recipient = params.get("to")
        subject = params.get("subject")
        body = params.get("body")
        
        if not recipient or not body:
             return {"success": False, "error": "Missing recipient or body"}

        try:
            # 2. Construct Message (Alternative allows both Plain and HTML)
            msg = MIMEMultipart('alternative')
            msg['From'] = username
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Add Plain Text Fallback
            msg.attach(MIMEText(body, 'plain'))
            
            # Add Premium HTML Version
            html_body = params.get("html_body")
            if not html_body:
                agent_name = params.get("agent_name", "Autonomous Agent")
                action_buttons = params.get("action_buttons")
                severity = params.get("severity") or params.get("priority", "info")
                html_body = self._build_html_template(subject, body, agent_name, action_buttons, severity)
                
            msg.attach(MIMEText(html_body, 'html'))
            
            # 3. Connect & Send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
                
            logger.info(f"GmailIntegration: Email sent to {recipient}")
            return {"success": True, "recipient": recipient}
            
        except Exception as e:
            logger.error("Gmail send failed", error=str(e))
            return {"success": False, "error": str(e)}

    def _build_html_template(self, title: str, content: str, agent_name: str, action_buttons: str = None, severity: str = "info") -> str:
        """Wraps plain text content into a premium, dark-mode branded HTML template with dynamic severity styling."""
        import re
        
        # Convert newlines to breaks
        html_content = content.replace('\n', '<br>')
        
        # Super simple markdown conversion for bolding/italics/lists
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #ffffff;">\1</strong>', html_content)
        html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
        html_content = re.sub(r'#{1,3}\s(.*?)<br>', r'<h3 style="color: #ffffff; margin-top: 16px; margin-bottom: 8px;">\1</h3>', html_content)
        
        # Convert bullet points
        html_content = html_content.replace('<br>- ', '<br>&bull; ')
        
        # Severity Themes mapping
        gradients = {
            "info": "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
            "normal": "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
            "low": "linear-gradient(135deg, #64748b 0%, #475569 100%)",       # Slate
            "success": "linear-gradient(135deg, #10b981 0%, #059669 100%)",   # Emerald
            "warning": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",   # Amber
            "medium": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",    # Amber
            "critical": "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)",  # Red
            "urgent": "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)",    # Red
            "high": "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)",      # Red
        }
        header_gradient = gradients.get(severity.lower(), gradients["info"])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #000000; margin: 0; padding: 40px 20px; }}
                .wrapper {{ width: 100%; table-layout: fixed; background-color: #000000; padding-bottom: 40px; }}
                .main-container {{ max-width: 600px; margin: 0 auto; background-color: #111111; border-radius: 12px; border: 1px solid #222222; overflow: hidden; }}
                .header {{ background: {header_gradient}; padding: 24px 32px; text-align: left; }}
                .header h1 {{ margin: 0; color: #ffffff; font-size: 20px; font-weight: 700; letter-spacing: -0.5px; }}
                .content-box {{ padding: 32px; font-size: 15px; line-height: 1.6; color: #a1a1aa; }}
                .badge {{ display: inline-block; background-color: rgba(139, 92, 246, 0.15); color: #c4b5fd; padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.5px; border: 1px solid rgba(139, 92, 246, 0.3); }}
                .content-title {{ color: #ffffff; margin-top: 0; font-size: 24px; font-weight: 600; letter-spacing: -0.5px; margin-bottom: 24px; }}
                .code-block {{ background-color: #000000; border: 1px solid #222222; border-radius: 8px; padding: 16px; margin: 20px 0; font-family: monospace; font-size: 13px; color: #d4d4d8; overflow-x: auto; }}
                .btn-container {{ margin-top: 32px; padding-top: 24px; border-top: 1px solid #222222; }}
                .btn {{ display: inline-block; background-color: #ffffff; color: #000000 !important; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: 600; font-size: 14px; transition: opacity 0.2s; }}
                .footer {{ padding: 24px; text-align: center; font-size: 12px; color: #52525b; }}
            </style>
        </head>
        <body>
            <center class="wrapper">
                <div class="main-container">
                    <div class="header">
                        <h1>MomentAIc OS</h1>
                    </div>
                    <div class="content-box">
                        <span class="badge">{agent_name}</span>
                        <h2 class="content-title">{title}</h2>
                        <div>{html_content}</div>
                        
                        {
                            f'<div class="btn-container" style="display: flex; gap: 12px;">{action_buttons}</div>'
                            if action_buttons 
                            else '<div class="btn-container"><a href="https://momentaic.com/dashboard" class="btn">View & Execute in Dashboard &rarr;</a></div>'
                        }
                    </div>
                </div>
                <div class="footer">
                    Sent autonomously by your Synthetic Co-Founders.<br>
                    You can manage agent permissions in your Vault settings.
                </div>
            </center>
        </body>
        </html>
        """

gmail_integration = GmailIntegration()
