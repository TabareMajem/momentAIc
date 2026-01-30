
"""
Listening Engine (The "Ears")
Periodically polls various channels (Email, Social) for replies and engagement.
"""
import asyncio
import structlog
from app.integrations.gmail import gmail_integration
from app.services.browser_worker import browser_worker

logger = structlog.get_logger()

class ListeningEngine:
    """
    Orchestrates the feedback loop.
    Checks for signals and creates 'Lead Events' if engagement is found.
    """
    
    async def run_cycle(self):
        logger.info("👂 Listening Engine: Starting Cycle...")
        
        # 1. Check Email Replies (IMAP)
        logger.info("   Checking Inbox...")
        try:
            # Syncs 'emails' data type which triggers IMAP check
            result = await gmail_integration.sync_data(data_types=["emails"])
            if result.success and result.data.get("emails"):
                emails = result.data.get("emails")
                logger.info(f"   📬 FOUND {len(emails)} NEW EMAILS!")
                for email in emails:
                    print(f"      - From: {email['sender']} | Subj: {email['subject']}")
                    # TODO: Trigger 'ReplyReceived' event in LangGraph
            else:
                logger.info("   Inbox clear.")
        except Exception as e:
             logger.error(f"   Email Check Failed: {e}")

        # 2. Check Social Notifications (Browser)
        # Only run if browser is active/headless
        # logger.info("   Checking Social Notifications...")
        # await browser_worker.check_notifications()

        logger.info("👂 Cycle Complete.")

listening_engine = ListeningEngine()

if __name__ == "__main__":
    # Test Run
    asyncio.run(listening_engine.run_cycle())
