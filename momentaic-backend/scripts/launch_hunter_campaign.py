import asyncio
import sys
import os
from datetime import datetime

# Add app to path
sys.path.append(os.getcwd())

# Re-init LLM inside loop
from app.agents.base import get_llm
from app.agents.lead_scraper_agent import lead_scraper_agent
from app.agents.lead_researcher_agent import lead_researcher_agent
from app.agents.sdr_agent import sdr_agent
import structlog

# Configure simple logging
structlog.configure(
    processors=[structlog.processors.JSONRenderer()],
)

STARTUP_CONTEXT = {
    "name": "Yokaizen",
    "description": "AI-powered mental wellness companion for students, using anime archetypes to make self-care engaging.",
    "tagline": "The anime companion that listens.",
    "value_prop": "Reduces burnout and improves retention by giving students a safe, gamified space to decompress.",
    "offer": "Free pilot program for Juku students to reduce exam stress."
}

async def main():
    print("🏹 Hunter Swarm: Launching Outbound Campaign...")
    
    # Init Agents
    llm = get_llm("gemini-2.5-pro", temperature=0.7)
    lead_scraper_agent.llm = llm
    lead_researcher_agent.llm = llm
    sdr_agent.llm = llm
    
    # 1. Scrape Leads
    print("\n🔍 Step 1: Finding Juku Targets...")
    scrape_result = await lead_scraper_agent.find_juku_leads(
        region="Shibuya Tokyo",
        limit=3 # Small batch for demo
    )
    
    leads = scrape_result.get("leads", [])
    print(f"✅ Found {len(leads)} leads")
    
    campaign_output = f"# 🏹 Hunter Swarm Campaign Log - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    # 2. Process each lead
    for i, lead in enumerate(leads):
        print(f"\n⚙️ Processing Target #{i+1}: {lead.get('name')}")
        
        # Research
        print("   🧠 Researching pain points...")
        research = await lead_researcher_agent.research_company(
            company_name=lead.get("name"),
            industry="Education/Cram School"
        )
        
        # Generate Email
        print("   📧 Drafting cold email...")
        email_result = await sdr_agent.generate_cold_email(
            lead=lead,
            research=research,
            startup_context=STARTUP_CONTEXT,
            tone="empathetic but professional"
        )
        
        if email_result.get("success"):
            email = email_result.get("email", {})
            
            # Append to log
            campaign_output += f"## 🎯 Prospect: {lead.get('name')}\n"
            campaign_output += f"**Context**: {lead.get('category', 'Juku')}\n"
            campaign_output += f"**Pain Points Identified**: {research.get('analysis', {}).get('PAIN POINTS', 'N/A')}\n\n"
            campaign_output += "### 📤 Draft Email\n"
            campaign_output += f"**Subject**: {email.get('subject')}\n\n"
            campaign_output += f"{email.get('body')}\n\n"
            campaign_output += "---\n\n"
            
            print("   ✅ Email generated.")
        else:
            print(f"   ❌ Failed to generate email: {email_result.get('error')}")

    # Save artifact
    output_path = "/root/.gemini/antigravity/brain/c335a996-e223-4f3f-9917-6d3e8b0e0cc7/campaign_outreach_batch_1.md"
    with open(output_path, "w") as f:
        f.write(campaign_output)
        
    print(f"\n✅ Campaign execution complete. Results saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
