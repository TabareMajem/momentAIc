
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.browser_worker import BrowserWorker, PLAYWRIGHT_AVAILABLE

async def test_browser():
    print("🤖 Testing Browser Worker...")
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright module not found.")
        return

    worker = BrowserWorker(headless=True)
    try:
        await worker.start()
        print("✅ Browser Launched.")
        
        await worker.page.goto("https://example.com")
        title = await worker.page.title()
        print(f"✅ Page Title: {title}")
        
        await worker.close()
        print("✅ Browser Closed.")
    except Exception as e:
        print(f"❌ Browser Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_browser())
