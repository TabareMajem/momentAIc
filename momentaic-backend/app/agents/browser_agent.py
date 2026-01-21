"""
Browser Agent
AI-powered web browsing and automation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import structlog
import asyncio
import requests

logger = structlog.get_logger()


@dataclass
class BrowseResult:
    """Result of a browse operation"""
    success: bool
    url: str
    title: str = ""
    text_content: str = ""
    screenshot_path: Optional[str] = None
    links: List[Dict[str, str]] = None
    forms: List[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.links is None:
            self.links = []
        if self.forms is None:
            self.forms = []


class BrowserAgent:
    """
    Browser Agent - Web browsing and automation
    
    Capabilities:
    - Navigate to URLs
    - Extract page content
    - Fill and submit forms
    - Click elements
    - Take screenshots
    - Execute JavaScript
    
    Uses Playwright for headless browser control
    """
    
    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
    
    async def initialize(self):
        """Initialize browser (lazy loading)"""
        if self._browser:
            return
        
        try:
            from playwright.async_api import async_playwright
            
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            self._context = await self._browser.new_context(
                user_agent="Mozilla/5.0 (Momentaic Browser Agent)",
                viewport={"width": 1280, "height": 720},
            )
            self._page = await self._context.new_page()
            
            logger.info("Browser initialized")
        except ImportError:
            logger.warning("Playwright not installed, using mock browser")
            self._browser = None
    
    async def navigate(self, url: str, wait_for: str = "load") -> BrowseResult:
        """
        Navigate to a URL
        
        Args:
            url: URL to navigate to
            wait_for: What to wait for ('load', 'domcontentloaded', 'networkidle')
        """
        if not self._browser:
            return BrowseResult(success=False, url=url, error="Browser service unavailable")
        
        try:
            response = await self._page.goto(url, wait_until=wait_for, timeout=30000)
            
            if not response or not response.ok:
                return BrowseResult(
                    success=False,
                    url=url,
                    error=f"Failed to load: {response.status if response else 'No response'}"
                )
            
            title = await self._page.title()
            content = await self._page.inner_text("body")
            
            # Extract links
            links = await self._page.evaluate("""
                () => Array.from(document.querySelectorAll('a')).slice(0, 20).map(a => ({
                    text: a.innerText.slice(0, 100),
                    href: a.href
                }))
            """)
            
            return BrowseResult(
                success=True,
                url=url,
                title=title,
                text_content=content[:5000],  # Limit content
                links=links,
            )
        except Exception as e:
            logger.error("Navigation failed", url=url, error=str(e))
            return BrowseResult(success=False, url=url, error=str(e))
    
    async def extract_content(self, selector: str = None) -> Dict[str, Any]:
        """Extract content from current page"""
        if not self._browser:
            return {"error": "Browser service unavailable"}
        
        try:
            if selector:
                element = await self._page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    return {"content": text, "selector": selector}
                return {"error": f"Element not found: {selector}"}
            
            # Get full page content
            text = await self._page.inner_text("body")
            return {"content": text[:10000]}
        except Exception as e:
            return {"error": str(e)}
    
    async def click(self, selector: str) -> Dict[str, Any]:
        """Click an element"""
        if not self._browser:
            return {"success": False, "error": "Browser service unavailable"}
        
        try:
            await self._page.click(selector, timeout=5000)
            await self._page.wait_for_load_state("networkidle")
            return {"success": True, "action": "click", "selector": selector}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def fill_form(self, fields: Dict[str, str]) -> Dict[str, Any]:
        """Fill form fields"""
        if not self._browser:
            return {"success": False, "error": "Browser service unavailable"}
        
        try:
            for selector, value in fields.items():
                await self._page.fill(selector, value)
            return {"success": True, "action": "fill", "fields": list(fields.keys())}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def screenshot(self, path: str = None) -> Dict[str, Any]:
        """Take a screenshot"""
        if not self._browser:
            return {"success": False, "error": "Browser service unavailable"}
        
        try:
            path = path or f"/tmp/screenshot_{int(asyncio.get_event_loop().time())}.png"
            await self._page.screenshot(path=path, full_page=True)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_script(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript on the page"""
        if not self._browser:
            return {"success": False, "error": "Browser service unavailable"}
        
        try:
            result = await self._page.evaluate(script)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process a browsing request from the agent system
        
        Parses natural language requests and executes browser actions
        """
        message_lower = message.lower()
        
        # Simple intent detection
        if "navigate" in message_lower or "go to" in message_lower or "visit" in message_lower:
            # Extract URL from message
            import re
            urls = re.findall(r'https?://\S+', message)
            if urls:
                result = await self.navigate(urls[0])
                return {
                    "response": f"Navigated to {result.url}. Title: {result.title}",
                    "data": {
                        "url": result.url,
                        "title": result.title,
                        "success": result.success,
                    },
                    "agent": "browser",
                }
        
        if "search" in message_lower:
            # Extract query
            query = message.replace("search for", "").replace("search", "").strip()
            if not query:
                return {"response": "What should I search for?", "agent": "browser"}
                
            results = await self.search_google(query)
            return {
                "response": f"Found {len(results)} results for '{query}':\n" + "\n".join([f"- {r['title']}: {r['snippet']}" for r in results[:3]]),
                "data": {"results": results},
                "agent": "browser"
            }
        
        if "screenshot" in message_lower:
            result = await self.screenshot()
            return {
                "response": f"Screenshot saved to {result.get('path', 'unknown')}",
                "data": result,
                "agent": "browser",
            }
        
        return {
            "response": """I'm the Browser Agent. I can help you:
- Navigate to websites
- Extract content from pages
- Fill and submit forms
- Take screenshots
- Search the web

What would you like me to do?""",
            "agent": "browser",
        }
    
    async def search_google(self, query: str) -> List[Dict[str, str]]:
        """
        Perform a Google search using the browser.
        Returns a list of {title, link, snippet}
        """
        if not self._browser:
            await self.initialize()
            
        if not self._browser:
            return [{"title": "Error", "link": "", "snippet": "Browser could not initialize"}]

        try:
            # Use a specialized search URL or just google.com
            # Note: Selectors here are fragile and depend on Google's DOM. 
            # In a real app we'd maintain these selectors or use a SearXNG instance.
            encoded_query = requests.utils.quote(query)
            # Use en-US to standardize interface
            url = f"https://www.google.com/search?q={encoded_query}&hl=en&gl=us"
            
            await self._page.goto(url, wait_until="domcontentloaded")
            
            # [REALITY FIX] Handle Google Consent Popup ("Before you continue")
            title = await self._page.title()
            if "Before you continue" in title or "Sign in" in title:
                logger.info("Browser Agent: Handling Google Consent Popup")
                # Try common accept buttons
                try:
                    # Look for buttons with text "Accept all", "I agree", "Reject all" (sometimes easier to find)
                    # We use a broad selector to find the button
                    button = self._page.get_by_role("button", name="Accept all").first
                    if await button.is_visible():
                        await button.click()
                        await self._page.wait_for_load_state("networkidle")
                    else:
                         # Fallback for "I agree"
                         button = self._page.get_by_role("button", name="I agree").first
                         if await button.is_visible():
                             await button.click()
                             await self._page.wait_for_load_state("networkidle")
                except Exception as e:
                    logger.warning("Failed to click consent button", error=str(e))
            
            # Simple extraction strategy
            # Updated selectors for 2025 Google DOM (often changes, but .g is usually safe wrapper, look for h3)
            # We also wait for selector to ensure results loaded
            try:
                await self._page.wait_for_selector('div.g', timeout=5000)
            except:
                pass # Proceed anyway to try extraction
            
            results = await self._page.evaluate("""
                () => {
                    const items = Array.from(document.querySelectorAll('div.g'));
                    return items.map(item => {
                        const titleEl = item.querySelector('h3');
                        const linkEl = item.querySelector('a');
                        // Snippet selector varies, try common ones
                        const snippetEl = item.querySelector('div.VwiC3b') || 
                                          item.querySelector('div.ITZIwc') || 
                                          item.querySelector('div.yXK7lf');
                        
                        if (!titleEl || !linkEl) return null;
                        
                        return {
                            title: titleEl.innerText,
                            link: linkEl.href,
                            snippet: snippetEl ? snippetEl.innerText : ''
                        };
                    }).filter(x => x);
                }
            """)
            
        except Exception as e:
            logger.error("Google search failed", error=str(e))
            results = []
        
        # Fallback to DuckDuckGo HTML (No JS, very reliable for scraping)
        if not results:
             try:
                logger.info("Falling back to DuckDuckGo HTML search")
                ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                await self._page.goto(ddg_url, wait_until="domcontentloaded")
                
                results = await self._page.evaluate("""
                    () => {
                        const items = Array.from(document.querySelectorAll('.result'));
                        return items.map(item => {
                            const titleEl = item.querySelector('.result__title a');
                            const snippetEl = item.querySelector('.result__snippet');
                            
                            if (!titleEl) return null;
                            
                            return {
                                title: titleEl.innerText.trim(),
                                link: titleEl.href,
                                snippet: snippetEl ? snippetEl.innerText.trim() : ''
                            };
                        }).filter(x => x);
                    }
                """)
             except Exception as e:
                 logger.error("DuckDuckGo fallback failed", error=str(e))
        
        return results[:5]
    
    
    async def close(self):
        """Close browser resources"""
        if self._browser:
            await self._browser.close()
            self._browser = None
            logger.info("Browser closed")


# Singleton instance
browser_agent = BrowserAgent()
