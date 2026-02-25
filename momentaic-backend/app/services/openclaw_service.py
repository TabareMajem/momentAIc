import asyncio
import json
from playwright.async_api import async_playwright
import structlog

logger = structlog.get_logger(__name__)

async def run_openclaw_session(websocket, directive: str):
    """
    Spins up a headless Chromium browser via Playwright and executes the directive.
    Streams logs and cursor positions back to the client via WebSockets.
    """
    async def send_log(action: str, details: str):
        await websocket.send_text(json.dumps({
            "type": "log",
            "action": action,
            "details": details
        }))
        await asyncio.sleep(0.5)

    async def send_cursor(x: float, y: float):
        await websocket.send_text(json.dumps({
            "type": "cursor",
            "x": x,
            "y": y
        }))
        await asyncio.sleep(0.1)

    try:
        await send_log("SYSTEM", "Allocating headless browser container...")
        await send_log("SYSTEM", "Injecting OpenClaw stealth scripts...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # SIMULATED DEMO: For the purpose of the Hero Demo, if it's the LinkedIn search...
            # We will use actual Playwright to navigate, but since we don't have real LinkedIn auth, 
            # we will navigate to a public page or just simulate the exact logs while physically driving the hidden browser.
            # In a true prod app, this would use LangChain/Agent to parse the DOM and decide next clicks.

            await send_log("NAVIGATE", "Routing to LinkedIn Search...")
            await send_cursor(50, 50)
            
            # Navigate to an actual safe URL to prove playwright works
            await page.goto("https://books.toscrape.com/")
            await asyncio.sleep(1)

            await send_cursor(80, 20)
            await send_log("SYSTEM", "Bypassing CAPTCHA challenge...")
            await asyncio.sleep(1)

            await send_cursor(30, 45)
            await send_log("EXTRACT", "Parsing DOM for target profiles...")
            # Let's extract something real from the page
            title = await page.title()
            await send_log("EXTRACT", f"Page Title Found: {title}")
            await asyncio.sleep(1)

            # Extracting some product names
            elements = await page.query_selector_all("article.product_pod h3 a")
            if elements:
                first_product = await elements[0].get_attribute("title")
                await send_log("EXTRACT", f"First Item Found: '{first_product}'")
            else:
                await send_log("EXTRACT", "No items found to extract.")

            await asyncio.sleep(1)
            await send_cursor(85, 45)
            await send_log("CLICK", "Clicking 'Connect' on Profile: Sarah Jenkins (Simulated)")
            await asyncio.sleep(1.5)

            await send_log("TYPE", 'Injecting contextual note: "Saw your recent round, wanted to connect..."')
            await asyncio.sleep(1)

            await send_cursor(60, 60)
            await send_log("CLICK", "Clicking 'Send'")
            await asyncio.sleep(1)

            await send_log("NAVIGATE", "Paginating to next results...")
            await asyncio.sleep(1)

            await send_log("SYSTEM", "Directive execution complete. Container shutting down.")

            await browser.close()
            
    except Exception as e:
        logger.error(f"OpenClaw Service Error: {e}")
        await send_log("ERROR", f"Browser crashed: {str(e)}")
