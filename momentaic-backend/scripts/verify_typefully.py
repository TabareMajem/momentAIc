import asyncio
import sys
import os
import structlog
from unittest.mock import MagicMock

# Add project root to path BEFORE imports
sys.path.append("/root/momentaic/momentaic-backend")

# Set mock env var
os.environ["TYPEFULLY_API_KEY"] = "mock_key"

from app.integrations.typefully import TypefullyIntegration

logger = structlog.get_logger()

async def test_typefully_direct():
    print("\n--- Testing TypefullyIntegration Direct ---")
    typefully = TypefullyIntegration()
    
    # Test Create Draft
    print("Creating draft thread...")
    draft = await typefully.execute_action("create_draft", {
        "content": "Just launched our new AI Agent swarm! \n\n1/ It handles research, outreach, and content.\n2/ Fully autonomous.\n\n#AI #Startup"
    })
    print(f"Draft Result: {draft}")
    
    assert draft["success"] == True
    assert draft["status"] == "draft"
    assert "mock_draft" in draft["draft_id"]
    
    # Test Schedule
    print("\nScheduling thread for next Monday...")
    scheduled = await typefully.execute_action("schedule_thread", {
        "content": "Scheduling this for the future! 🚀",
        "date": "2026-02-02T09:00:00Z"
    })
    print(f"Schedule Result: {scheduled}")
    
    assert scheduled["success"] == True
    assert scheduled["status"] == "scheduled"
    assert "mock_thread" in scheduled["thread_id"]
    
    print("\n✅ Typefully Integration Verification: SUCCESS")

if __name__ == "__main__":
    asyncio.run(test_typefully_direct())
