"""
News Service
Fetches trending topics using Serper (Google Search API) or falls back to Gemini.
"""

import httpx
import structlog
from typing import List, Dict, Any
from app.core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime

logger = structlog.get_logger()

class NewsService:
    def __init__(self):
        self.serper_api_key = settings.serper_api_key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_api_key,
            temperature=0.3
        ) if settings.google_api_key else None

    async def fetch_trending_topics(self, category: str = "technology", count: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch top news headlines.
        """
        logger.info("fetching_news", category=category)
        
        # Try Serper first
        if self.serper_api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://google.serper.dev/news",
                        headers={
                            "X-API-KEY": self.serper_api_key,
                            "Content-Type": "application/json"
                        },
                        json={
                            "q": f"top {category} news today",
                            "num": 10,
                            "tbs": "qdr:d" # Past 24 hours
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        news_items = data.get("news", [])[:count]
                        logger.info("news_fetched_from_serper", count=len(news_items))
                        return [
                            {
                                "title": item.get("title"),
                                "snippet": item.get("snippet"),
                                "source": item.get("source"),
                                "link": item.get("link"),
                                "date": item.get("date")
                            }
                            for item in news_items
                        ]
            except Exception as e:
                logger.error("serper_failed", error=str(e))

        # Fallback to Gemini Knowledge
        logger.info("using_gemini_fallback")
        if not self.llm:
            return [{"title": "AI Override: No News Service Available", "snippet": "Configure keys."}]

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a news aggregator. List the top {count} trending {category} news stories from the last 24 hours. Return ONLY valid JSON."),
            ("user", "List news.")
        ])
        
        # Simple extraction via LLM (simulated real-time often works with Gemini 2.0 due to freshness)
        result = await self.llm.ainvoke(f"List top {count} {category} news headlines for Today, {datetime.utcnow().strftime('%Y-%m-%d')}.")
        
        # Return structured dummy data based on LLM text if parsing needed, 
        # but for now we'll just return the text wrapped
        return [{
            "title": f"Gemini Insight: {category}", 
            "snippet": result.content, 
            "source": "Gemini AI"
        }]

news_service = NewsService()
