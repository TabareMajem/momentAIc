
"""
Browser Worker (The "Hands")
Handles headless browser automation for tasks that lack public APIs or require "Human" simulation.
Uses Playwright for robustness.
"""
import asyncio
import structlog
from typing import Dict, Any, Optional
import os

logger = structlog.get_logger()

# Try to import playwright, but handle environment where it might not be installed yet
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Browser Worker will be disabled.")

class BrowserWorker:
    """
    Persistent browser session manager.
    Can log in, maintain cookies, and execute UI actions.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    async def start(self):
        """Initialize browser session"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not installed.")
            
        logger.info("BrowserWorker: Starting Browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()
        logger.info("BrowserWorker: Browser Ready.")

    async def close(self):
        """Cleanup resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("BrowserWorker: Stopped.")

    async def login_twitter(self, username: str, password: str) -> bool:
        """
        Attempt to log in to X.com via UI.
        Fallback for when API tokens expire.
        """
        if not self.page:
            await self.start()
            
        logger.info(f"BrowserWorker: Attempting Twitter Login for {username}...")
        try:
            await self.page.goto("https://twitter.com/i/flow/login")
            
            # Username
            await self.page.wait_for_selector("input[autocomplete='username']")
            await self.page.fill("input[autocomplete='username']", username)
            await self.page.click("text=Next")
            
            # Password
            await self.page.wait_for_selector("input[name='password']")
            await self.page.fill("input[name='password']", password)
            await self.page.click("div[data-testid='LoginForm_Login_Button']")
            
            # Verification check (look for home)
            try:
                await self.page.wait_for_selector("div[data-testid='primaryColumn']", timeout=10000)
                logger.info("BrowserWorker: Twitter Login SUCCESS.")
                
                # Save cookies for future use
                cookies = await self.context.cookies()
                # storage_logic.save_cookies("twitter", cookies)
                
                return True
            except Exception:
                logger.error("BrowserWorker: Login Check Failed (Could include 2FA challenge)")
                return False
                
        except Exception as e:
            logger.error(f"BrowserWorker: Login Failed: {e}")
            await self.page.screenshot(path="login_fail.png")
            return False

    async def post_tweet(self, text: str) -> bool:
        """Post a tweet via UI"""
        if not self.page:
            return False
            
        logger.info("BrowserWorker: Posting Tweet via UI...")
        try:
            await self.page.goto("https://twitter.com/compose/tweet")
            await self.page.wait_for_selector("div[data-testid='tweetTextarea_0']")
            await self.page.fill("div[data-testid='tweetTextarea_0']", text)
            await self.page.click("div[data-testid='tweetButton']")
            
            logger.info("BrowserWorker: Tweet Posted.")
            return True
        except Exception as e:
            logger.error(f"BrowserWorker: Post Failed: {e}")
            return False

    async def check_notifications(self) -> Dict[str, Any]:
        """
        Check Twitter notifications tab for replies/mentions.
        """
        if not self.page:
            try:
                await self.start()
            except Exception as e:
                logger.error(f"BrowserWorker: Start failed: {e}")
                return {"success": False, "notifications": []}

        # If not logged in, we can't check. (Assumes session cookies exist or manual login already happened)
        # Note: In a real run, we'd check for login state first.
        
        logger.info("BrowserWorker: Checking Twitter Notifications...")
        try:
            await self.page.goto("https://twitter.com/notifications")
            try:
                # Wait for notification cells
                await self.page.wait_for_selector("div[data-testid='cellInnerDiv']", timeout=5000)
                
                # Extract text from first 3 notifications
                notifications = await self.page.evaluate('''() => {
                    const nodes = document.querySelectorAll("div[data-testid='cellInnerDiv']");
                    return Array.from(nodes).slice(0,3).map(n => n.innerText);
                }''')
                
                logger.info(f"BrowserWorker: Found {len(notifications)} notifications.")
                return {"success": True, "notifications": notifications}
                
            except Exception:
                 # Timeout means no notifications loaded or login screen blocking
                 logger.warning("BrowserWorker: No notifications found (or login screen).")
                 return {"success": False, "notifications": []}

        except Exception as e:
            logger.error(f"BrowserWorker: Notification Check Failed: {e}")
            return {"success": False, "error": str(e)}

browser_worker = BrowserWorker()
