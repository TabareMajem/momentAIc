
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# GLOBAL KEY INJECTION
os.environ["GOOGLE_API_KEY"] = "AIzaSyCNcZLz38mZ6E4SBcMdoQ4ksJHv58gZy_Y"

async def expand_full_pipeline():
    print("🎯 PIPELINE EXPANSION - Running Lookalikes on All Seeds...")
    
    from app.agents.marketing_agent import marketing_agent
    
    seeds = [
        {"name": "Bilawal Sidhu", "industry": "AI Video"},
        {"name": "Don Allen Stevenson III", "industry": "VFX/AI"},
        {"name": "Ole Lehmann", "industry": "AI Solopreneur"},
        {"name": "Zain Kahn", "industry": "AI Newsletter"},
    ]
    
    all_lookalikes = []
    
    for seed in seeds:
        print(f"\n[Hunter] Expanding from: {seed['name']}...")
        try:
            results = await marketing_agent.find_lookalikes(seed)
            print(f"   ✅ Found {len(results)} lookalikes.")
            for r in results:
                print(f"      - {r.get('name')} ({r.get('title')})")
                all_lookalikes.append(r)
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Rate limit pause
        await asyncio.sleep(2)
    
    print(f"\n🚀 TOTAL NEW LEADS: {len(all_lookalikes)}")
    print("Pipeline expanded. Ready for enrichment phase.")

if __name__ == "__main__":
    asyncio.run(expand_full_pipeline())
