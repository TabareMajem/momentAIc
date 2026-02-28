import asyncio
import structlog
from typing import Dict, Any

from app.agents.browser_agent import browser_agent
from app.agents.sdr_agent import SDRAgent
from scripts.trigger_symbiotask_campaign import SymbiotaskCampaignManager

logger = structlog.get_logger()

async def execute_active_inbox_monitoring():
    """
    Phase 9: Active Orchestration Loop
    
    This function utilizes Open Claw via the BrowserAgent to autonomously scrape 
    the DM inboxes (X and WhatsApp), read any replies from prospects, and 
    dispatch DeepSeek to generate dynamic JSON workflows or handle objections.
    """
    logger.info("initiating_active_inbox_monitoring_loop")
    sdr = SDRAgent()
    
    # 1. Scrape X (Twitter) Inbox
    x_inbox_result = await browser_agent.monitor_x_dms()
    if x_inbox_result.get("success"):
        unread_x_messages = x_inbox_result.get("inbox_data", [])
        logger.info("x_inbox_scraped", unread_count=len(unread_x_messages))
        
        for msg in unread_x_messages:
            logger.info("processing_x_reply", sender=msg['sender'])
            
            # DeepSeek intent analysis and JSON generation
            reply_action = await sdr.handle_social_reply(
                platform="X",
                prospect_handle=msg['sender'],
                message_history="[Previous 'Stress Test' Hook Sent]",
                latest_reply=msg['message']
            )
            
            if reply_action.get("success") and reply_action.get("action") in ["deliver_magnet", "handle_objection"]:
                logger.info("dispatching_autonomous_reply", 
                            action=reply_action['action'], 
                            target=msg['sender'])
                
                # Execute native DM reply
                # In full production, this would also explicitly attach the generated JSON file
                # Playwright/OpenClaw file uploads require specific DOM selectors for the attachment button.
                # For this MVP phase, we send the message natively pointing them to the link/text.
                await browser_agent.execute_x_dm(
                    handle=msg['sender'], 
                    message=reply_action['reply_text']
                )
    else:
        logger.error("failed_to_scrape_x_inbox", error=x_inbox_result.get("error"))

    # 2. Scrape WhatsApp Web Inbox
    wa_inbox_result = await browser_agent.monitor_whatsapp_messages()
    if wa_inbox_result.get("success"):
        unread_wa_messages = wa_inbox_result.get("inbox_data", [])
        logger.info("whatsapp_inbox_scraped", unread_count=len(unread_wa_messages))
        
        for msg in unread_wa_messages:
            logger.info("processing_wa_reply", sender=msg['sender'])
            
            reply_action = await sdr.handle_social_reply(
                platform="WhatsApp",
                prospect_handle=msg['sender'],
                message_history="[Previous 'Reliability Layer' Hook Sent]",
                latest_reply=msg['message']
            )
            
            if reply_action.get("success") and reply_action.get("action") in ["deliver_magnet", "handle_objection"]:
                logger.info("dispatching_autonomous_reply", 
                            action=reply_action['action'], 
                            target=msg['sender'])
                            
                await browser_agent.execute_whatsapp_dm(
                    phone_number=msg['sender'], 
                    message=reply_action['reply_text']
                )
    else:
         logger.error("failed_to_scrape_wa_inbox", error=wa_inbox_result.get("error"))
         
    # Ensure Playwright cleanup if running locally
    await browser_agent.close()
    logger.info("active_inbox_monitoring_loop_complete")

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Symbiotask Active Campaign Loop")
    parser.add_argument("--phase", choices=["all", "outbound", "orchestration"], default="all", help="Which phase of the loop to run")
    args = parser.parse_args()

    logger.info("=========================================")
    logger.info("Starting Symbiotask Active Campaign Agent")
    logger.info("=========================================")
    
    if args.phase in ["all", "outbound"]:
        # 1. First, process the Outbound Generation Engine (Phase 7/8 trigger script logic)
        # This generates new "Stress Test" hooks using the dummy CSV
        logger.info("Stage 1: Processing Outbound Generation (Domain Warmup Constrained)")
        manager = SymbiotaskCampaignManager()
        await manager.run_external_stress_test_campaign("scripts/dummy_targets.csv")
    
    if args.phase in ["all", "orchestration"]:
        # 2. Second, process the Active Orchestration Loop (Phase 9)
        # This reads inboxes for replies and uses DeepSeek to synthesize technical JSON responses
        logger.info("Stage 2: Processing Active Orchestration (Inbox Polling & Dynamic Generators)")
        await execute_active_inbox_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
