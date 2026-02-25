
import asyncio
import os
import structlog
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright


import sys

# Configure logging to write to stderr (so stdout is kept clean for MCP)
structlog.configure(
    processors=[structlog.processors.JSONRenderer()],
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
)
logger = structlog.get_logger()

# Create an MCP server
mcp = FastMCP("Browser Agent")

@mcp.tool()
async def browse_page(url: str) -> str:
    """
    Visit a URL and return its text content (markdown friendly).
    This runs in a headless browser, handling JS rendering.
    """
    logger.info("Browsing page", url=url)
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            
            # Extract content (simplified)
            content = await page.evaluate("() => document.body.innerText")
            title = await page.title()
            
            await browser.close()
            return f"# {title}\n\n{content}"
            
    except Exception as e:
        logger.error("Browser failed", error=str(e))
        return f"Error browsing {url}: {str(e)}"

@mcp.tool()
async def search_google_serp(query: str) -> str:
    """
    Search Google and return top results (Titles + URLs).
    Use this for finding information.
    """
    # Note: In production we use Serper API, but let's implement a fallback scraping tool here
    # to demonstrate MCP capabilities.
    logger.info("Searching Google", query=query)
    search_url = f"https://www.google.com/search?q={query}"
    return await browse_page(search_url)

if __name__ == "__main__":
    # Run the server via stdio
    mcp.run()
