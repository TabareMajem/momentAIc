import asyncio
import structlog
from typing import List, Dict, Any

from app.agents.browser_agent import browser_agent

logger = structlog.get_logger()

class DataHarvesterAgent:
    """
    Phase 10: The Data Harvester
    
    This agent is responsible for autonomously building our database of highly
    qualified technical leads (Developers, No-Code Architects, Agency Directors)
    without relying on purchased lists. It performs "Intelligence Scraping" 
    on platforms like GitHub and X.
    """
    def __init__(self):
        self.browser = browser_agent
        
    async def scrape_github_stars(self, repo_name: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Navigates to a GitHub repository's stargazers page and extracts the profiles
        of developers who starred it (indicating interest in that tech stack).
        """
        url = f"https://github.com/{repo_name}/stargazers"
        logger.info("harvester_scraping_github_stars", repo=repo_name)
        
        # Ensure Playwright is booted locally for DOM parsing
        await self.browser.initialize(force_local=True)
        page = self.browser._page
        
        try:
            await page.goto(url, wait_until="networkidle")
            
            # Simple DOM extraction for GitHub stargazers
            # In a full production proxy setup, this would handle pagination.
            profiles = await page.evaluate('''() => {
                const users = [];
                const items = document.querySelectorAll('ol > li');
                for (let i = 0; i < items.length; i++) {
                    const link = items[i].querySelector('h3 a');
                    if (link) {
                        const handle = link.innerText.trim();
                        users.push({
                            "platform": "github",
                            "handle": handle,
                            "profile_url": "https://github.com/" + handle,
                            "inferred_stack": "n8n/automation" // Defaulting context based on repo
                        });
                    }
                }
                return users;
            }''')
            
            # Mock processing to fit max_results
            scraped = profiles[:max_results] if profiles else []
            
            # If DOM scraping failed due to UI changes, return an empty list
            if not scraped:
                logger.warning("github_dom_scrape_empty")
                scraped = []
            
            logger.info("harvester_github_scrape_complete", count=len(scraped))
            return {"success": True, "data": scraped}
            
        except Exception as e:
            logger.error("github_scrape_failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def scrape_x_followers(self, handle: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Navigates to an X (Twitter) profile's followers page to find technical leads.
        """
        url = f"https://x.com/{handle}/followers"
        logger.info("harvester_scraping_x_followers", target_handle=handle)
        
        await self.browser.initialize(force_local=True)
        page = self.browser._page
        
        try:
           # NOTE: X is heavily gated. Without session cookies injected, this redirects to Login.
           # The Session Manager built in Phase 10 Priority 2 will handle this bypass.
           await page.goto(url, wait_until="networkidle")
           
           # Extractor logic (Wait for timeline to render)
           try:
               await page.wait_for_selector('[data-testid="UserCell"]', timeout=5000)
               profiles = await page.evaluate('''() => {
                   const users = [];
                   const cells = document.querySelectorAll('[data-testid="UserCell"]');
                   for (let i = 0; i < cells.length; i++) {
                       const link = cells[i].querySelector('a[role="link"]');
                       if (link) {
                           const href = link.getAttribute('href');
                           const handle = href.replace('/', '');
                           users.push({
                               "platform": "x",
                               "handle": handle,
                               "profile_url": "https://x.com/" + handle
                           });
                       }
                   }
                   return users;
               }''')
           except Exception as dom_e:
               logger.warning("x_dom_scrape_failed_likely_login_wall", error=str(dom_e))
               profiles = []
               
           scraped = profiles[:max_results] if profiles else []
           logger.info("harvester_x_scrape_complete", count=len(scraped))
           
           return {"success": True, "data": scraped}
           
        except Exception as e:
            logger.error("x_scrape_failed", error=str(e))
            return {"success": False, "error": str(e)}


    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for new data sources and enrichment opportunities.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} new data sources and enrichment opportunities 2025")
        
        if results:
            from app.agents.base import get_llm
            llm = get_llm("gemini-pro", temperature=0.3)
            if llm:
                from langchain_core.messages import HumanMessage
                prompt = f"""Analyze these results for a {industry} startup:
{str(results)[:2000]}

Identify the top 3 actionable insights. Be concise."""
                try:
                    response = await llm.ainvoke([HumanMessage(content=prompt)])
                    from app.agents.base import BaseAgent
                    if hasattr(self, 'publish_to_bus'):
                        await self.publish_to_bus(
                            topic="intelligence_gathered",
                            data={
                                "source": "DataHarvesterAgent",
                                "analysis": response.content[:1500],
                                "agent": "data_harvester",
                            }
                        )
                    actions.append({"name": "data_source_found", "industry": industry})
                except Exception as e:
                    logger.error(f"DataHarvesterAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Scrapes and structures data from web sources for lead enrichment and market research.
        """
        action_type = action.get("action", action.get("name", "unknown"))

        try:
            from app.agents.base import get_llm, web_search
            from langchain_core.messages import HumanMessage
            
            industry = startup_context.get("industry", "Technology")
            llm = get_llm("gemini-pro", temperature=0.5)
            
            if not llm:
                return "LLM not available"
            
            search_results = await web_search(f"{industry} {action_type} best practices 2025")
            
            prompt = f"""You are the Web scraping and data collection agent for a {industry} startup.

Based on this context:
- Action requested: {action_type}
- Industry: {industry}
- Research: {str(search_results)[:1500]}

Generate a concrete, actionable deliverable. No fluff. Be specific and executable."""
            
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            if hasattr(self, 'publish_to_bus'):
                await self.publish_to_bus(
                    topic="deliverable_generated",
                    data={
                        "type": action_type,
                        "content": response.content[:2000],
                        "agent": "data_harvester",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("DataHarvesterAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

data_harvester = DataHarvesterAgent()
