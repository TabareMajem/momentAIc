
import asyncio
import sys
import os
import structlog
from types import SimpleNamespace
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.sales_agent import sales_agent
from app.models.growth import LeadStatus

logger = structlog.get_logger()

# Mock Lead Object (duck typing)
class MockLead:
    def __init__(self):
        self.id = "lead_123"
        self.startup_id = "startup_456"
        self.company_name = "Acme Corp"
        self.contact_name = "Wile E. Coyote"
        self.contact_title = "Chief Genius"
        self.contact_linkedin = "linkedin.com/in/wile"
        self.company_industry = "Logistics"
        self.company_website = "https://acme.com"
        self.company_size = "1-10"
        self.contact_email = "wile@acme.com"
        self.status = LeadStatus.NEW
        self.research_data = {"recent_news": "Failed to catch roadrunner again."}
        self.outreach_messages = []

async def test_sales_outreach():
    print("🚀 Testing Sales Outreach Generation...")
    
    lead = MockLead()
    
    startup_context = {
        "name": "Roadrunner Protection Services",
        "description": "Security systems for fast birds.",
        "tagline": "Beep Beep Security",
        "industry": "Security"
    }
    
    user_id = "test_user_123"
    
    try:
        # Note: sales_agent.run usually triggers the whole hunting flow or just research?
        # Let's check sales_agent.py run method.
        # It triggers the whole graph.
        
        result = await sales_agent.run(
            lead=lead,
            startup_context=startup_context,
            user_id=user_id
        )
        
        print("\n✅ Result Recieved:")
        messages = result.get("messages", [])
        for m in messages:
            print(f"- {m.content}")
            
        generated_draft = result.get("draft", {})
        if generated_draft:
            print(f"\n💌 Draft:\nSubject: {generated_draft.get('subject')}\nBody:\n{generated_draft.get('body')}")
        else:
            # Maybe it's in a different key?
            print(f"\n⚠️ keys in result: {result.keys()}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sales_outreach())
