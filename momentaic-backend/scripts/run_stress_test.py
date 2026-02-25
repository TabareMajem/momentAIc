
import asyncio
import structlog
from app.agents.kol_headhunter_agent import KOLHeadhunterAgent

logger = structlog.get_logger()

# Top 5 Targets from GTM Plan (Workflow Architects)
TARGETS = [
    {"name": "Harish Malhi", "handle": "@HarishMalhi", "role": "Founder Goodspeed", "platform": "LinkedIn"},
    {"name": "Aleksandar Blazhev", "handle": "@alexblazhev", "role": "Product Hunt Reviewer", "platform": "Product Hunt"},
    {"name": "David Ondrej", "handle": "@DavidOndrej", "role": "Vectal AI Founder", "platform": "Twitter"},
    {"name": "Arjen", "handle": "Arjen (n8n)", "role": "n8n Community Expert", "platform": "n8n Forums"},
    {"name": "Tom", "handle": "Tom (Quivvy)", "role": "Make.com Partner", "platform": "LinkedIn"},
]

STRESS_TEST_SCRIPT = """
Hey {name}, I saw your recent workflow on {platform} regarding automation.
At Symbiotask, we just built a new "Nolan Mode" Video Agent that combines GenAI with n8n-style pipelines.
I suspect it might break if you throw sophisticated logic at it.
Want to try to "break it"? If you find edges, we'll fix it and credit you as a Founding Architect.
Let me know if you want a stress-test access code.
"""

async def run_stress_test():
    print("🚀 STARTING GTM STRESS TEST: OPERATION BREAKPOINT")
    print("-" * 50)
    
    agent = KOLHeadhunterAgent()
    
    results = []
    
    for target in TARGETS:
        print(f"\n🎯 Targeting: {target['name']} ({target['role']})")
        
        # 1. Simulate "Finding" the contact
        # In real life, agent would scrape. Here we mock the 'find' success.
        print(f"   > Scraper: Contact found at {target['handle']}")
        
        # 2. Draft the Message
        draft = STRESS_TEST_SCRIPT.format(
            name=target['name'].split()[0],
            platform=target['platform']
        )
        
        # 3. Log the "Outreach"
        print(f"   > KOLHeadhunter: Drafting outreach...")
        print(f"   > MSG: {draft.strip()}")
        print(f"   > STATUS: READY_TO_SEND")
        
        results.append({
            "target": target['name'],
            "status": "DRAFTED",
            "message_preview": draft[:50] + "..."
        })
        
        # Simulate slight delay
        await asyncio.sleep(0.5)

    print("\n" + "=" * 50)
    print(f"✅ STRESS TEST BATCH COMPLETE: {len(results)} INVITES PREPARED")
    print("Waiting for user approval to hit SEND (simulated).")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
