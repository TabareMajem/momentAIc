"""
Viral Content Agent
Autonomously scrapes trends via OpenClaw and generates viral hooks for the founder to approve.
"""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
import structlog
import os
import json
from openai import AsyncOpenAI

from app.core.config import settings
from app.agents.base import get_llm, BaseAgent

logger = structlog.get_logger()

class ViralContentAgent(BaseAgent):
    """
    Viral Content Agent - The Trend Surfer
    Proactively scrapes competitor/industry timelines to draft counter-narrative content.
    Requires Human-in-the-Loop approval before posting.
    """
    
    def __init__(self):
        self.name = "Viral Content Agent"
        self.llm = get_llm("gemini-pro", temperature=0.8)
        
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = "dummy_key_to_prevent_import_crash"
        self.openai_client = AsyncOpenAI(api_key=api_key)

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use OpenClaw to scrape industry trends and draft 3 counter-narrative tweets.
        Queues them in the ActionItem database for founder approval.
        """
        actions = []
        logger.info(f"Agent {self.name} starting proactive trend sweep")
        
        competitors = startup_context.get("competitors", [])
        industry = startup_context.get("industry", "SaaS")
        
        from app.agents.browser_agent import BrowserAgent
        browser = BrowserAgent()
        await browser.initialize()
        
        trend_context = "No live trends found."
        
        # 1. Scrape inspiration
        if competitors:
            target = competitors[0]
            # Heuristic: search Twitter for the competitor
            twitter_url = f"https://twitter.com/search?q={target}&src=typed_query"
            logger.info(f"Scraping competitor mentions: {twitter_url}")
            res = await browser.navigate(twitter_url)
            if res.success and res.text_content:
                trend_context = res.text_content[:3000]
        else:
            # Scrape general industry news if no competitor
            news_url = f"https://news.ycombinator.com/item?id=latest"
            res = await browser.navigate(news_url)
            if res.success and res.text_content:
                trend_context = res.text_content[:3000]
                
        # 2. Generate 3 hooks
        if self.llm:
            prompt = f"""You are the Viral Content Agent for a {industry} startup.
            Review this raw scrape of recent industry chatter/competitor mentions:
            {trend_context}
            
            Identify 3 distinct, slightly controversial or highly valuable counter-narrative "hooks" (tweets) that position our startup as the better solution.
            
            Return ONLY a JSON array of objects with keys: "hook" (the tweet text), and "rationale" (why it works)."""
            
            try:
                raw_response = await self.llm.ainvoke([HumanMessage(content=prompt)])
                content = raw_response.content.replace('```json', '').replace('```', '').strip()
                hooks = json.loads(content)
                
                # 3. Queue as ActionItems for the founder
                from app.models.action_item import ActionPriority
                from app.services.agent_memory_service import agent_memory_service # We'll just publish to bus for now and let the system handle DB saving
                
                for idx, item in enumerate(hooks[:3]):
                    hook_text = item.get("hook", "")
                    if hook_text:
                        # Publish as a pending action
                        await self.publish_to_bus(
                            topic="action_item_proposed",
                            data={
                                "action_type": "tweet",
                                "title": f"Draft Tweet: {hook_text[:30]}...",
                                "description": item.get("rationale", "Viral hook based on daily sweep."),
                                "payload": {"content": hook_text},
                                "priority": ActionPriority.medium.value if idx > 0 else ActionPriority.high.value
                            }
                        )
                        actions.append({"name": "drafted_tweet", "hook": hook_text[:20]})
                        
            except Exception as e:
                logger.error("Failed to parse hooks", error=str(e))
                
        return actions

    async def generate_viral_campaign(self, topic: str, generate_video: bool = False) -> List[Dict[str, str]]:
        """Legacy manual generation method (kept for backward compatibility)"""
        if not self.llm:
            raise Exception("AI Service Unavailable")
            
        system_prompt = "You are a world-class viral growth hacker. Generate 3 viral hooks and Image prompts for DALL-E as a JSON array of objects with 'hook' and 'image_prompt' keys."
        user_prompt = f"Topic: {topic}\n\nGenerate 3 viral hooks and image prompts."
        
        try:
            response = await self.llm.ainvoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            content = response.content.replace('```json', '').replace('```', '').strip()
            campaigns = json.loads(content)
            
            results = []
            for campaign in campaigns:
                hook = campaign.get("hook", "")
                if not hook: continue
                # We mock DALL-E here for speed since the focus is autonomy
                results.append({"hook": hook, "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&q=80&w=800"})
                
            return results
        except Exception as e:
            logger.error("Viral generation failed", error=str(e))
            raise e

# Singleton instance
viral_content_agent = ViralContentAgent()
