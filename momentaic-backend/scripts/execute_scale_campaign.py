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
    print("🏹 Hunter Swarm: Launching SCALED Outbound Campaign (100+ Leads)...")
    
    # Init Agents
    llm = get_llm("gemini-2.5-pro", temperature=0.7)
    lead_scraper_agent.llm = llm
    lead_researcher_agent.llm = llm
    sdr_agent.llm = llm
    
    # 1. Scrape Leads
    print("\n🔍 Step 1: Finding Juku Targets (Batch 1)...")
    
    # Run multiple scrapes in parallel if needed, but for now we trust the limit
    # We will target different major wards in Tokyo to ensure volume
    regions = ["Shibuya", "Shinjuku", "Minato", "Koto", "Setagaya"]
    all_leads = []
    
    for region in regions:
        print(f"   Searching {region}...")
        scrape_result = await lead_scraper_agent.find_juku_leads(
            region=f"{region} Tokyo",
            limit=25 # 25 per region * 5 regions = 125 potential leads
        )
        leads = scrape_result.get("leads", [])
        print(f"   Found {len(leads)} in {region}")
        all_leads.extend(leads)
        
    print(f"\n✅ Total Leads Found: {len(all_leads)}")
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    campaign_output = f"# 🏹 Hunter Swarm Scaled Campaign Log - {timestamp}\n\n"
    
    # 2. Process each lead
    for i, lead in enumerate(all_leads):
        if i >= 105: break # Hard cap safely above 100
        
        print(f"\n⚙️ Processing Target #{i+1}: {lead.get('name')}")
        
        # Research
        research = await lead_researcher_agent.research_company(
            company_name=lead.get('name'),
            industry="Education/Cram School"
        )
        
        # Generate Email
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
            campaign_output += f"**Context**: {lead.get('category', 'Juku')} | {lead.get('location', 'Tokyo')}\n"
            campaign_output += f"**Research**: {research.get('summary', 'N/A')}\n"
            campaign_output += "### 📤 Draft Email\n"
            campaign_output += f"**Subject**: {email.get('subject')}\n\n"
            campaign_output += f"{email.get('body')}\n\n"
            campaign_output += "---\n\n"
            
            # Flush to file incrementally in case of crash
            output_path = f"/root/.gemini/antigravity/brain/c335a996-e223-4f3f-9917-6d3e8b0e0cc7/campaign_scaled_run_{timestamp}.md"
            with open(output_path, "w") as f:
                f.write(campaign_output)
                
            print("   ✅ Email generated.")
        else:
            print(f"   ❌ Failed to generate email: {email_result.get('error')}")

    print(f"\n✅ Campaign execution complete. Results saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
