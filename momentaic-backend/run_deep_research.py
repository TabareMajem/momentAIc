
import asyncio
import sys
import os
import json
import structlog
from datetime import datetime

# Ensure app is in path
sys.path.append(os.getcwd())

from app.agents.kol_headhunter_agent import KOLHeadhunterAgent
from app.agents.ambassador_outreach_agent import AmbassadorOutreachAgent
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
# DEEP RESEARCH PROTOCOL
# =============================================================================

PERSONAS = {
    "Open Startup": [
        "SaaS MRR update 2024",
        "building in public revenue reveal",
        "open startup metrics",
        "how I grew my SaaS to $10k",
        "indie hacker revenue milestone",
        "bootstrapped SaaS journey",
        "#buildinpublic weekly update"
    ],
    "Tech Realist": [
        "VC math doesn't work for founders",
        "why I stopped fundraising",
        "profitability over unicorns",
        "sustainable startup growth",
        "bootstrapping vs venture capital 2025",
        "tech bubble 2024 critique",
        "dangers of raising venture capital"
    ],
    "Micro-SaaS": [
        "micro-saas idea validation",
        "vertical AI saas examples",
        "chrome extension business",
        "shopify app developer journey",
        "newsletter business model",
        "solo founder tech stack",
        "marketing for developers"
    ],
    "Lifestyle": [
        "solopreneur automation tools",
        "AI agency business model",
        "replace employees with AI",
        "autonomous business operations",
        "one-person business scaling",
        "digital nomad software engineer",
        "passive income via software"
    ]
}

async def run_batch(persona: str, keywords: list, batch_num: int):
    print(f"\n=== BATCH {batch_num}: {persona} ===")
    logger.info(f"Starting Batch {batch_num}", persona=persona)
    
    headhunter = KOLHeadhunterAgent()
    ambassador = AmbassadorOutreachAgent()
    
    # Scan for 25 targets
    hit_list = await headhunter.scan_region(
        region="Global",
        max_targets=25,
        custom_keywords=keywords
    )
    
    print(f"Found {len(hit_list.targets)} targets for {persona}")
    
    results = []
    
    async def process_target(target):
        try:
            print(f"[{persona}] Drafting outreach for: {target.name}")
            # Determine context based on persona
            context_map = {
                "Open Startup": "transparent builder",
                "Tech Realist": "independent thinker",
                "Micro-SaaS": "niche expert",
                "Lifestyle": "automation master"
            }
            user_context = context_map.get(persona, "founder")
            
            outreach = await ambassador.generate_outreach(
                candidate_name=target.name,
                platform=target.platform,
                startup_context={
                    "name": "MomentAIc",
                    "tagline": "The AI Operating System for Bootstrap Founders",
                    "description": "We help you scale without employees or equity dilution."
                },
                program_summary="Founding Ambassador: 40% lifetime comms + White-label access.",
                custom_instructions=f"Appeal to their '{user_context}' persona. Mention their specific content about '{keywords[0]}'. Keep it peer-to-peer."
            )
            
            t_dict = target.dict()
            t_dict["final_outreach"] = outreach.get("message")
            t_dict["persona_tag"] = persona
            return t_dict
            
        except Exception as e:
            logger.error(f"Failed to draft outreach for {target.name}", error=str(e))
            return None

    # Process all targets in parallel
    tasks = [process_target(t) for t in hit_list.targets]
    results = await asyncio.gather(*tasks)
    
    # Filter out None results
    results = [r for r in results if r is not None]
            
    return results

async def run_deep_research():
    start_time = datetime.now()
    all_targets = []
    
    # Execute batch per persona
    batch_num = 1
    for persona, keywords in PERSONAS.items():
        batch_results = await run_batch(persona, keywords, batch_num)
        all_targets.extend(batch_results)
        batch_num += 1
        
        # Wait a bit between batches to be nice to APIs
        await asyncio.sleep(2)
        
    # Save Master List
    filename = "deep_research_targets.json"
    with open(filename, "w") as f:
        json.dump(all_targets, f, indent=2)
        
    print(f"\n=== DEEP RESEARCH COMPLETE ===")
    print(f"Total Targets Identified: {len(all_targets)}")
    print(f"Saved to: {filename}")
    
    # Send Summary Email
    email_body = f"""
    <h2>Deep Research Campaign Report</h2>
    <p><b>Total KOLs Identified:</b> {len(all_targets)}</p>
    <p><b>Breakdown by Persona:</b></p>
    <ul>
    """
    
    for persona in PERSONAS.keys():
        count = len([t for t in all_targets if t["persona_tag"] == persona])
        email_body += f"<li>{persona}: {count} targets</li>"
        
    email_body += "</ul>"
    
    await email_service.send_email(
        to_email="support@momentaic.com",
        subject=f"[DEEP RESEARCH] {len(all_targets)} New KOL Targets Found",
        body="See HTML report.",
        html_body=email_body
    )
    print("Summary email sent.")

if __name__ == "__main__":
    asyncio.run(run_deep_research())
