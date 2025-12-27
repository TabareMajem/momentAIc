
import os
import sys
import asyncio
from typing import Dict, Any

# Mock required env vars to bypass Pydantic validation errors if .env is incomplete
# We do this BEFORE importing app.core.config
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://mock:mock@localhost/mockdb"
if "SECRET_KEY" not in os.environ:
    os.environ["SECRET_KEY"] = "mock_secret_key_for_testing_only_12345"
if "JWT_SECRET_KEY" not in os.environ:
    os.environ["JWT_SECRET_KEY"] = "mock_jwt_secret_key_for_testing_only_67890"

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.agents.marketing_agent import MarketingAgent
from app.agents.tech_lead_agent import TechLeadAgent
from app.agents.supervisor import SupervisorAgent

async def test_agent_class(name: str, agent_cls: Any, message: str):
    print(f"\nTesting {name}...")
    try:
        # Instantiate inside the loop
        agent = agent_cls()
        
        # Create dummy context
        context = {
            "name": "TestStartup",
            "industry": "AI",
            "description": "An AI platform for testing.",
            "stage": "MVP"
        }
        
        if name == "Supervisor":
             response = await agent.route(message, context, "user_test", "startup_test")
        else:
             response = await agent.process(message, context, "user_test")
        
        print(f"Result: {response}")
        
        if response.get("error") and response.get("response") == "AI Service Unavailable":
             print(f"❌ STATUS: FAIL - AI Service Unavailable (Missing Keys?)")
        elif response.get("error"):
             print(f"❌ STATUS: FAIL - Error: {response.get('response')}")
        else:
             print(f"✅ STATUS: SUCCESS - Real AI Response Received")
             
    except Exception as e:
        print(f"❌ STATUS: CRASH - {str(e)}")

async def main():
    print("=== LIVE AGENT VERIFICATION ===")
    print(f"Google API Key Configured: {'Yes' if settings.google_api_key else 'No'}")
    
    await test_agent_class("Marketing Agent", MarketingAgent, "Create a tagline for an AI coffee machine.")
    await test_agent_class("Tech Lead Agent", TechLeadAgent, "What stack should I use for a high-frequency trading bot?")
    await test_agent_class("Supervisor", SupervisorAgent, "I need help with my marketing strategy.")

if __name__ == "__main__":
    asyncio.run(main())
