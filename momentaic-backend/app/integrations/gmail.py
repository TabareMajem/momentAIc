
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

        
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email actions"""
        if action == "send_email":
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
            # 2. Construct Message
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
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

gmail_integration = GmailIntegration()
