
import asyncio
import sys
import os
import structlog

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.growth import growth_agent

logger = structlog.get_logger()

async def test_viral_campaign():
    print("🚀 Testing Viral Campaign Generation via GrowthSuperAgent...")
    
    # Mock Context
    startup_context = {
        "name": "Yokaizen",
        "description": "AI-powered mental wellness app for Gen Z using anime avatars.",
        "industry": "Mental Health / Consumer App",
        "target_audience": "Gen Z, Anime fans, Lonely men",
        "tone": "Empathetic but gamified"
    }
    
    target = {
        "type": "exit_survey",
        "platform": "tiktok",
        "variations": 1,
        "user_data": {"churn_reason": "Too expensive"}
    }
    
    user_id = "test_user_123"
    
    try:
        result = await growth_agent.run(
            mission="viral_campaign",
            target=target,
            startup_context=startup_context,
            user_id=user_id
        )
        
        print("\n✅ Result Recieved:")
        content = result.get("content", {})
        assets = content.get("assets", [])
        
        if not assets:
            print("❌ No assets generated!")
        else:
            for i, asset in enumerate(assets):
                print(f"\n--- Asset {i+1} ---")
                print(f"Title: {asset.get('title')}")
                print(f"Hook: {asset.get('hook')}")
                print(f"Body Preview: {asset.get('script', asset.get('body', ''))[:100]}...")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_viral_campaign())
