
import asyncio
import sys
import os
import json
import structlog
from datetime import datetime

# Ensure app is in path
sys.path.append(os.getcwd())

from app.agents.vc_headhunter_agent import VCHeadhunterAgent
from app.services.email_service import email_service

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

# =============================================================================
# VC OUTREACH PROTOCOL
# =============================================================================

VC_PERSONAS = {
    "AI Native": [
        "active AI investors 2025",
        "VCs investing in AI agents",
        "seed funds for generative AI",
        "partners at Sequoia AI",
        "a16z AI investment thesis"
    ],
    "Creator Economy": [
        "VCs for creator economy tools",
        "investors in solopreneur tech",
        "future of work venture capital",
        "seed investors SaaS tools",
        "angel investors for bootstrap founders"
    ]
}

async def run_vc_batch(persona: str, keywords: list, batch_num: int):
    print(f"\n=== VC BATCH {batch_num}: {persona} ===")
    logger.info(f"Starting VC Batch {batch_num}", persona=persona)
    
    headhunter = VCHeadhunterAgent()
    
    # Scan for 25 targets
    deal_flow = await headhunter.scan_for_investors(
        max_targets=25,
        custom_keywords=keywords
    )
    
    print(f"Found {len(deal_flow.targets)} investors for {persona}")
    
    results = []
    
    # Process targets (already have cold_pitch from agent)
    for i, target in enumerate(deal_flow.targets):
        print(f"[{persona}] Identified: {target.name} ({target.firm})")
        t_dict = target.dict()
        t_dict["persona_tag"] = persona
        results.append(t_dict)
            
    return results

async def run_vc_campaign():
    start_time = datetime.now()
    all_targets = []
    
    # Execute batch per persona
    batch_num = 1
    for persona, keywords in VC_PERSONAS.items():
        batch_results = await run_vc_batch(persona, keywords, batch_num)
        all_targets.extend(batch_results)
        batch_num += 1
        
        # Wait a bit between batches
        await asyncio.sleep(2)
        
    # Save Master List
    filename = "vc_deal_flow.json"
    with open(filename, "w") as f:
        json.dump(all_targets, f, indent=2)
        
    print(f"\n=== VC OUTREACH COMPLETE ===")
    print(f"Total Investors Identified: {len(all_targets)}")
    print(f"Saved to: {filename}")
    
    # Send Summary Email
    email_body = f"""
    <h2>VC Outreach Campaign Report</h2>
    <p><b>Total Investors Identified:</b> {len(all_targets)}</p>
    <p><b>Breakdown by Focus:</b></p>
    <ul>
    """
    
    for persona in VC_PERSONAS.keys():
        count = len([t for t in all_targets if t["persona_tag"] == persona])
        email_body += f"<li>{persona}: {count} targets</li>"
        
    email_body += "</ul>"
    
    # Add top 3 examples
    email_body += "<h3>Top Opportunities:</h3><ul>"
    for t in all_targets[:3]:
        email_body += f"<li><b>{t['name']}</b> ({t['firm']})<br/><i>Strategy: {t['cold_pitch'][:100]}...</i></li>"
    email_body += "</ul>"
    
    await email_service.send_email(
        to_email="support@momentaic.com",
        subject=f"[DEAL FLOW] {len(all_targets)} Investors Identified",
        body="See HTML report.",
        html_body=email_body
    )
    print("Summary email sent.")

if __name__ == "__main__":
    asyncio.run(run_vc_campaign())
