import asyncio
import sys
import os
from unittest.mock import MagicMock
import structlog

# Add project root to path BEFORE imports
sys.path.append("/root/momentaic/momentaic-backend")

# Set mock env vars
os.environ["CLAY_API_KEY"] = "mock_key"
os.environ["ATTIO_API_KEY"] = "mock_key"
os.environ["INSTANTLY_API_KEY"] = "mock_key"

from app.integrations.clay import ClayIntegration
from app.integrations.attio import AttioIntegration
from app.integrations.instantly import InstantlyIntegration
from app.agents.lead_researcher_agent import lead_researcher_agent

logger = structlog.get_logger()

async def test_full_pipeline():
    print("\n--- Testing Full GTM Pipeline (Clay -> Attio -> Instantly) ---")
    
    from unittest.mock import patch
    
    # Patch the names in the local scope of lead_researcher_agent
    with patch("app.agents.lead_researcher_agent.company_research") as mock_cr, \
         patch("app.agents.lead_researcher_agent.web_search") as mock_ws, \
         patch("app.agents.lead_researcher_agent.LeadResearcherAgent.shadow_research", new_callable=MagicMock) as mock_shadow:
         
        # Configure mocks to behave like ASYNC tools
        # We need to mock 'ainvoke' which is a coroutine
        async def mock_tool_return(*args, **kwargs):
            return "Mock Tool Result"
            
        mock_cr.ainvoke.side_effect = mock_tool_return
        mock_cr.name = "company_research"
        
        mock_ws.ainvoke.side_effect = mock_tool_return
        mock_ws.name = "web_search"
        
        # Configure async shadow research mock
        async def async_shadow(*args, **kwargs):
            return {"summary": "Mock Shadow Insights"}
        mock_shadow.side_effect = async_shadow
        
        # We need to access the singleton instance
        from app.agents.lead_researcher_agent import lead_researcher_agent
        
        # Patch LLM on the instance
        lead_researcher_agent.llm = MagicMock()
        async def mock_ainvoke(*args, **kwargs):
            return MagicMock(content="Mock Analysis Content") 
        lead_researcher_agent.llm.ainvoke = mock_ainvoke

        # 2. Run Researcher (Should Trigger Clay + Attio)
        print("Running Lead Researcher for 'stripe.com'...")
        result = await lead_researcher_agent.research_company(
            company_name="Stripe",
            company_website="https://stripe.com"
        )
        
        print(f"Research Success: {result['success']}")
        
        # Verify Clay
        if result.get("success"):
            clay_data = result.get("raw_research", {}).get("clay_enrichment")
            if clay_data:
                print(f"✅ Clay Enrichment: Success ({clay_data.get('name')})")
            else:
                print("❌ Clay Enrichment: Failed (No data)")
                
            # Check logs/output for Attio sync confirmation (inferred from success)
            # Or we can verify by checking if the method completed without error
            print("✅ Agent Execution: Completed without error")
        else:
            print(f"❌ Agent Execution: Failed with error: {result.get('error')}")

        # 3. Verify Direct Integration Calls (Simulation)
        
        # Attio Check
        attio = AttioIntegration()
        attio_res = await attio.sync_company({"name": "Stripe", "domain": "stripe.com"})
        if attio_res["success"] and "mock_company" in attio_res["record_id"]:
             print(f"✅ Attio Direct Sync: Success (ID: {attio_res['record_id']})")
        else:
             print("❌ Attio Direct Sync: Failed")
             
        # Instantly Check (Add Lead)
        instantly = InstantlyIntegration()
        inst_res = await instantly.add_lead_to_campaign({
            "campaign_id": "test_camp_1",
            "email": "patrick@stripe.com",
            "first_name": "Patrick"
        })
        if inst_res["success"] and "mock_lead" in inst_res["lead_id"]:
            print(f"✅ Instantly Direct Add: Success (ID: {inst_res['lead_id']})")
        else:
            print("❌ Instantly Direct Add: Failed")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
