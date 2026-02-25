import os
import aiohttp
import structlog
from datetime import datetime, UTC
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.astroturf import AstroTurfMention, MentionStatus
from app.models.startup import Startup
from app.agents.base import get_llm

logger = structlog.get_logger(__name__)

class AstroTurfService:
    async def _fetch_hn_stories(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Simulate scraping HackerNews for specific keywords in Top Stories."""
        results = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://hacker-news.firebaseio.com/v0/topstories.json") as resp:
                    top_ids = await resp.json()
                    
                for story_id in top_ids[:20]:  # Scan top 20
                    async with session.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json") as item_resp:
                        item = await item_resp.json()
                        if not item or "title" not in item:
                            continue
                        
                        text_to_search = item.get("title", "") + " " + item.get("text", "")
                        if any(kw.lower() in text_to_search.lower() for kw in keywords):
                            results.append({
                                "platform": "hackernews",
                                "author": item.get("by", "unknown"),
                                "content": item.get("title", ""),
                                "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}")
                            })
        except Exception as e:
            logger.error("HN Fetch Error", error=str(e))
        return results

    async def draft_reply(self, startup: Startup, post_content: str) -> str:
        """Use LLM to draft a non-salesy, high-context reply."""
        prompt = f"""
        You are a GTM community manager for {startup.name}, a startup doing: {startup.description}.
        A user posted this online: "{post_content}"
        
        Draft a highly contextual, "non-salesy" reply that organically seeds the startup as a solution or relevant point without sounding like a marketer.
        Max 2-3 sentences. Sound like a helpful engineer.
        """
        try:
            llm = get_llm("gemini-2.5-pro")
            if llm:
                response = await llm.ainvoke(prompt)
                return response.content
            return "Hey, I had a similar problem a while back. Ended up using a tool called " + startup.name + " to solve it. Might be worth checking out."
        except Exception as e:
            logger.error("AstroTurf Draft Error", error=str(e))
            return "Hey, I had a similar problem a while back. Ended up using a tool called " + startup.name + " to solve it. Might be worth checking out."

    async def scan_and_draft(self, db: AsyncSession, startup_id: str):
        """Main cron job to scrape and formulate drafts."""
        startup = await db.get(Startup, startup_id)
        if not startup:
            return

        keywords = [startup.industry] if startup.industry else ["software", "saas", "tech"]
        mentions = await self._fetch_hn_stories(keywords)

        for m in mentions:
            # Check if exists
            stmt = select(AstroTurfMention).where(
                AstroTurfMention.url == m["url"],
                AstroTurfMention.startup_id == startup_id
            )
            existing = (await db.execute(stmt)).scalars().first()
            if existing:
                continue

            draft = await self.draft_reply(startup, m["content"])
            
            new_mention = AstroTurfMention(
                startup_id=startup.id,
                platform=m["platform"],
                author=m["author"],
                content=m["content"],
                url=m["url"],
                generated_reply=draft,
                status=MentionStatus.DRAFTED
            )
            db.add(new_mention)
        
        await db.commit()

astroturf_service = AstroTurfService()
