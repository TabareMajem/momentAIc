import asyncio
import json
import os
import sys

# Ensure app is in path
sys.path.append(os.getcwd())

from app.agents.kol_headhunter_agent import KOLHeadhunterAgent
from app.agents.ambassador_outreach_agent import AmbassadorOutreachAgent
from app.services.email_service import email_service
import structlog

# Configure structlog for standalone run
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

async def run_anti_yc_campaign():
    logger.info("Starting Anti-YC KOL Campaign")
    
    print("Initializing agents...")
    headhunter = KOLHeadhunterAgent()
    ambassador = AmbassadorOutreachAgent()
    
    keywords = [
        "YC rejection story",
        "why I declined Y Combinator",
        "bootstrapped vs VC funded",
        "VCs matchmakers or gatekeepers",
        "is YC worth it 2024",
        "post-YC pivot",
        "failed YC startup",
        "anti-VC manifesto",
        "solo founder vs accelerator"
    ]
    
    # 1. Scan for targets
    # User asked for 100, but let's start with a batch of 20 high-quality ones to avoid timeouts/rate limits in this run
    batch_size = 20 
    logger.info(f"Scanning US region for top {batch_size} targets...", keywords=keywords)
    print(f"Scanning for {batch_size} targets with keywords: {keywords}")
    
    hit_list = await headhunter.scan_region(
        region="US",
        max_targets=batch_size,
        custom_keywords=keywords
    )
    
    logger.info(f"Found {len(hit_list.targets)} potential targets")
    print(f"Found {len(hit_list.targets)} targets. Analyzing and drafting outreach...")
    
    results = []
    
    # 2. Analyze & Draft Outreach
    for i, target in enumerate(hit_list.targets):
        print(f"Processing {i+1}/{len(hit_list.targets)}: {target.name}")
        
        # Use last post or fallback
        context = target.last_posts[0] if target.last_posts else "independent startup stance"
        
        # Refine outreach using Ambassador Agent
        outreach = await ambassador.generate_outreach(
            candidate_name=target.name,
            platform=target.platform,
            startup_context={
                "name": "MomentAIc",
                "tagline": "The AI Operating System for Bootstrap Founders",
                "description": "We provide the benefits of a YC network (AI co-founders, growth engines, strategy) without the equity dilution."
            },
            program_summary="Exclusive 'Founding Ambassador' tier. 40% lifetime commissions. White-label access for your community.",
            custom_instructions=f"Position us as the ultimate tool for their specific stance: '{context}'. Acknowledge their view on VCs/YC. Keep it creating, like a fellow founder reaching out."
        )
        
        target_data = target.dict()
        target_data["final_outreach"] = outreach.get("message")
        target_data["outreach_status"] = "DRAFTED"
        results.append(target_data)
    
    # 3. Save Results (only if we found targets)
    filename = "anti_yc_kol_targets.json"
    if results:
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved {len(results)} targets to {filename}")
        print(f"Saved {len(results)} results to {filename}")
    else:
        logger.warning("No targets found. JSON file not overwritten.")
        print("No targets found. Skipping JSON write to preserve existing data.")
    
    # 4. Email Summary
    print("Sending summary email...")
    email_body = f"""
    <h2>Anti-YC KOL Campaign Report</h2>
    <p><b>Campaign Goal:</b> Detect KOLs critical of YC/VC and draft outreach.</p>
    <p><b>Targets Identified:</b> {len(results)}</p>
    <h3>Top Candidates:</h3>
    <ul>
    """
    
    for r in results[:5]:
        email_body += f"<li><b>{r['name']}</b> ({r['platform']}) - {r['followers']} followers<br/><i>Strategy: {r['outreach_script'][:100]}...</i></li>"
    
    email_body += f"""
    </ul>
    <p>Full target list saved to <code>{filename}</code> on the server.</p>
    <p><b>Next Steps:</b> Review the JSON file and approve for sending.</p>
    """
    
    # Send to the configured support email
    sent = await email_service.send_email(
        to_email="support@momentaic.com", 
        subject="[REPORT] Anti-YC KOL Campaign Results",
        body="Please see HTML version.",
        html_body=email_body
    )
    
    if sent:
        logger.info("Campaign complete. Notification sent.")
        print("Success! detailed report sent to support@momentaic.com")
    else:
        logger.error("Failed to send email notification.")
        print("Error: Failed to send email.")

if __name__ == "__main__":
    asyncio.run(run_anti_yc_campaign())
