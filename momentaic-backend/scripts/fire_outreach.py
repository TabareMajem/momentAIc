
import asyncio
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# GLOBAL KEY INJECTION (Must happen before app imports)
os.environ["GOOGLE_API_KEY"] = "AIzaSyCNcZLz38mZ6E4SBcMdoQ4ksJHv58gZy_Y"

async def fire_outreach():
    print("🔥 INITIATING REAL-WORLD OUTREACH...")
    
    # Imports can now be safely here or top level, but let's keep here for loop safety
    from app.agents.marketing_agent import marketing_agent
    from app.agents.ambassador_agent import ambassador_agent
    from app.integrations.gmail import gmail_integration

    # 0. Check Credentials First
    if not os.environ.get("GMAIL_USER") and not getattr(gmail_integration, 'config', {}):
        # We rely on the integration to warn, but let's be explicit
        print("⚠️  WARNING: GMAIL_USER/PASSWORD not found in env. This might fail.")

    # 1. Target: Bilawal Sidhu (Symbiotask)
    bilawal_lead = {
        "contact_name": "Bilawal Sidhu",
        "email": "bilawal.sidhu@example.com", # In real life, this would be enriched
        "company_name": "AI Video",
        "interest": "High"
    }
    
    print(f"\n[Hunter] Targeting: {bilawal_lead['contact_name']}...")
    # Mocking a generated campaign
    subject = "AI Video + Collaborative Workflow?"
    body = "Hi Bilawal,\n\nSaw your latest video on AI gen. Have you tried Symbiotask for managing the render pipeline?\n\n- The AI"
    
    result = await marketing_agent.execute_outreach(bilawal_lead, subject, body)
    if result.get("success"):
        print(f"✅ EMAIL SENT to {result['recipient']}")
    else:
        print(f"❌ SEND FAILED: {result.get('error')} (Did you add GMAIL_USER/PASS?)")

    # 2. Target: Ole Lehmann (Ambassador)
    ole_prospect = {
        "contact_name": "Ole Lehmann",
        "contact_email": "ole@theaisolopreneur.com", # Mock
        "company_name": "The AI Solopreneur",
        "audience_size": 100000
    }
    
    print(f"\n[Ambassador] Generating Proposal for: {ole_prospect['contact_name']}...")
    # Generate fresh proposal text
    proposal = await ambassador_agent.generate_partnership_proposal(ole_prospect)
    proposal_text = proposal['proposal_draft']
    print(f"   Draft Value: ${proposal['projected_revenue']:,.2f}/mo")
    
    print("   Sending Proposal via Gmail...")
    result_amb = await ambassador_agent.send_proposal(ole_prospect, proposal_text)
    
    if result_amb.get("success"):
        print(f"✅ PROPOSAL SENT to {ole_prospect['contact_email']}")
    else:
        print(f"❌ SEND FAILED: {result_amb.get('error')}")

if __name__ == "__main__":
    # Inject API Key for Agents to Work (Generation)
    # os.environ["GOOGLE_API_KEY"] = "..." # Handled by container
    asyncio.run(fire_outreach())
