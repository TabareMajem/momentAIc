import asyncio
import sys
import os
from unittest.mock import MagicMock
import structlog

# Add project root to path BEFORE imports
sys.path.append("/root/momentaic/momentaic-backend")

# Set mock env var
os.environ["CLAY_API_KEY"] = "mock_key"

from app.integrations.clay import ClayIntegration

logger = structlog.get_logger()

async def test_clay_direct():
    print("\n--- Testing ClayIntegration Direct ---")
    clay = ClayIntegration()
    
    # Test enrich_company
    result = await clay.execute_action("enrich_company", {"domain": "stripe.com"})
    print(f"Direct Result: {result}")
    
    assert result["success"] == True
    assert "Stripe" in result["data"]["name"]

async def test_agent_integration():
    print("\n--- Testing LeadResearcherAgent with Clay ---")
    
    # We need to patch the tools where they are DEFINED in the base module
    # or where they are imported.
    # Based on the file, `company_research` and `web_search` are imported from app.agents.base
    
    import app.agents.base as base_agent_module
    
    # Save originals
    orig_cr = base_agent_module.company_research
    orig_ws = base_agent_module.web_search
    
    try:
        # Mock Tools
        mock_cr = MagicMock()
        mock_cr.invoke.return_value = "Mock Company Info"
        mock_cr.name = "company_research"
        
        mock_ws = MagicMock()
        mock_ws.invoke.return_value = "Mock Search Results"
        mock_ws.name = "web_search"
        
        # Apply patch to BASE module where they are defined
        base_agent_module.company_research = mock_cr
        base_agent_module.web_search = mock_ws
        
        # Now import the agent which uses them
        from app.agents.lead_researcher_agent import LeadResearcherAgent
        agent = LeadResearcherAgent()
        
        # Mock LLM
        agent.llm = MagicMock()
        async def mock_ainvoke(*args, **kwargs):
            return MagicMock(content="Mock Analysis") 
        agent.llm.ainvoke = mock_ainvoke
        
        # Mock shadow research
        async def mock_shadow(*args, **kwargs):
            return {"summary": "Mock Shadow Insights"}
        agent.shadow_research = mock_shadow
        
        # Run research
        print("Running agent research for 'stripe.com'...")
        result = await agent.research_company(
            company_name="Stripe",
            company_website="https://stripe.com"
        )
        
        if "raw_research" in result:
            clay_data = result["raw_research"].get("clay_enrichment")
            print(f"\nClay Enrichment Data: {clay_data}")
            assert clay_data is not None
            assert "Stripe" in clay_data["name"]
            print("SUCCESS: Agent used Clay!")
        else:
            print("FAILURE: No raw_research")
            
    finally:
        # Restore
        base_agent_module.company_research = orig_cr
        base_agent_module.web_search = orig_ws

async def main():
    await test_clay_direct()
    await test_agent_integration()

if __name__ == "__main__":
    asyncio.run(main())
