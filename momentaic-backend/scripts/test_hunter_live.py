import asyncio
import sys
import os

# Add app to path
sys.path.append(os.getcwd())

from app.agents.lead_scraper_agent import lead_scraper_agent
import structlog

# Configure simple logging
structlog.configure(
    processors=[structlog.processors.JSONRenderer()],
)

async def main():
    print("🏹 Hunter Swarm: Starting Live Test...")
    print("🎯 Target: Juku (Cram Schools) in Tokyo")
    
    # Re-initialize LLM inside the event loop to avoid "no running event loop" error
    from app.agents.base import get_llm
    lead_scraper_agent.llm = get_llm("gemini-2.5-pro", temperature=0.3)
    
    # Run the scraper
    try:
        result = await lead_scraper_agent.find_juku_leads(
            region="Tokyo",
            limit=5 
        )
        
        if result.get("success"):
            print(f"\n✅ SUCCESS: Found {len(result.get('leads', []))} leads\n")
            print("-" * 50)
            for i, lead in enumerate(result.get("leads", [])):
                print(f"🏢 Lead #{i+1}")
                print(f"Name: {lead.get('name')}")
                print(f"Address: {lead.get('address', 'N/A')}")
                print(f"Website: {lead.get('website', 'N/A')}")
                print(f"Context: {lead.get('category', 'Education')}")
                print("-" * 50)
        else:
            print(f"\n❌ FAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
