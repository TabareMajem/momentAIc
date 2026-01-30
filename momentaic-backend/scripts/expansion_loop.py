
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Force API Key from Env (ensure this is passed by docker exec)
os.environ["GOOGLE_API_KEY"] = "AIzaSyCNcZLz38mZ6E4SBcMdoQ4ksJHv58gZy_Y" # Handled by container env

async def run_expansion():
    print("🚀 EXECUTING DYNAMIC GTM LOOP...")
    
    # Import INSIDE the loop to fix 'Initialize... with running event loop' error
    from app.agents.marketing_agent import marketing_agent
    from app.agents.ambassador_agent import ambassador_agent
    
    # 1. Test Hunter 2.0 (Lookalike)
    print("\n[Hunter 2.0] Finding Lookalikes for seed: Bilawal Sidhu...")
    try:
        results = await marketing_agent.find_lookalikes({"name": "Bilawal Sidhu", "industry": "AI Video"})
        print(f"✅ Found {len(results)} new potential targets:")
        for r in results:
            print(f"   - {r.get('name')} ({r.get('title')})")
    except Exception as e:
        print(f"❌ Hunter Failed: {e}")

    # 2. Test Ambassador Agent (Revenue Proposal)
    print("\n[Ambassador] Drafting Revenue Deal for: Ole Lehmann...")
    try:
        proposal = await ambassador_agent.generate_partnership_proposal({
            "contact_name": "Ole Lehmann",
            "company_name": "The AI Solopreneur",
            "audience_size": 100000
        })
        print(f"✅ Proposal Generated. Value: ${proposal['projected_revenue']:,.2f}/mo")
        print(f"--- PREVIEW ---\n{proposal['proposal_draft'][:200]}...\n---")
    except Exception as e:
        print(f"❌ Ambassador Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_expansion())
