
import asyncio
import structlog
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.kol_headhunter_agent import KOLHeadhunterAgent

logger = structlog.get_logger()

async def test_kol_tools():
    print("Initializing KOL Headhunter...")
    agent = KOLHeadhunterAgent()
    
    # helper to find tool by name
    def get_tool(name):
        for tool in agent._tools:
            if tool.name == name:
                return tool
        return None

    youtube_tool = get_tool("search_youtube_creators")
    twitter_tool = get_tool("search_twitter_creators")
    
    if not youtube_tool:
        print("❌ YouTube tool not found")
        return

    print("\n--- Testing YouTube Search (Real) ---")
    try:
        results = await youtube_tool.ainvoke({
            "keywords": "AI automation",
            "region": "US",
            "max_results": 3
        })
        
        # DEBUG: Check browser state directly
        from app.agents.browser_agent import browser_agent
        if not results:
             print("⚠️ No results found. Debugging page state...")
             if browser_agent._page:
                 title = await browser_agent._page.title()
                 content = await browser_agent._page.inner_text("body")
                 print(f"Current Page Title: {title}")
                 print(f"Current Page Content Preview: {content[:500]}")
        
        print(f"✅ Found {len(results)} creators:")
        for r in results:
            print(f"  - {r.get('channel_name')} ({r.get('link')})")
            print(f"    Desc: {r.get('description')[:50]}...")
            print(f"    Source: {r.get('source')}")
    except Exception as e:
        print(f"❌ YouTube search failed: {e}")

    print("\n--- Testing Twitter Search (Real) ---")
    try:
        results = await twitter_tool.ainvoke({
            "keywords": "SaaS founder",
            "region": "US",
            "max_results": 3
        })
        print(f"✅ Found {len(results)} creators:")
        for r in results:
            print(f"  - {r.get('handle')} ({r.get('link')})")
            print(f"    Bio: {r.get('bio')[:50]}...")
    except Exception as e:
        print(f"❌ Twitter search failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_kol_tools())
