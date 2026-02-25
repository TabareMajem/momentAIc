
import asyncio
from app.services.email_service import email_service

async def test_send():
    print("Testing email send...")
    success = await email_service.send_email(
        to_email="support@momentaic.com", # Send to self
        subject="Test Email from MomentAIc (Port 587)",
        body="This is a test email using Port 587 and STARTTLS. If you see this, configuration is correct.",
    )
    if success:
        print("Email sent successfully!")
    else:
        print("Email send FAILED.")

if __name__ == "__main__":
    asyncio.run(test_send())
