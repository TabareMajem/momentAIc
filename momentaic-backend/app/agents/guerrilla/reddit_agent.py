"""
Reddit Sleeper Agent ("The Listener")
Monitors subreddits for high-intent discussions and drafts value-first comments.
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog
import datetime

from app.agents.base import get_llm, web_search
from app.models.conversation import AgentType

logger = structlog.get_logger()

class RedditSleeperAgent:
    """
    Reddit Sleeper Agent
    - Scans for keywords (e.g., "alternative to X", "how to Y")
    - Analyses sentiment and intent
    - Drafts helpful, non-spammy comments
    """
    
    @property
    def llm(self):
        return get_llm("gemini-flash", temperature=0.7)
    
    async def scan_and_draft(
        self,
        keywords: List[str],
        startup_context: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scan for opportunities and draft responses.
        Uses web_search as a proxy for Reddit API for now.
        """
        if not self.llm:
            return []

        opportunities = []
        
        for keyword in keywords:
            try:
                # 1. Search for recent Reddit threads
                query = f"site:reddit.com {keyword} after:{datetime.date.today() - datetime.timedelta(days=7)}"
                search_results = await web_search.ainvoke(query)
                
                # 2. Analyze results for high intent
                prompt = f"""
                Analyze these search results from Reddit:
                {search_results}
                
                Find threads where users are:
                1. Complaining about a competitor
                2. Asking for a solution that {startup_context.get('name')} provides
                3. Looking for alternatives
                
                Return a JSON list of objects:
                [
                    {{
                        "title": "Thread Title",
                        "url": "Thread URL",
                        "user_pain": "Summary of their problem",
                        "relevance_score": 1-10
                    }}
                ]
                """
                
                analysis_response = await self.llm.ainvoke([
                    SystemMessage(content="You are a growth hacker finding high-intent leads on Reddit."),
                    HumanMessage(content=prompt)
                ])
                
                import json
                import re
                try:
                    content = analysis_response.content
                    match = re.search(r'\[.*\]', content, re.DOTALL)
                    threads = json.loads(match.group(0)) if match else []
                except:
                    threads = []
                
                # 3. Draft Responses for high relevance threads
                for thread in threads:
                    if thread.get('relevance_score', 0) >= 7:
                        draft_prompt = f"""
                        Draft a helpful Reddit comment for this thread:
                        
                        Thread: {thread.get('title')}
                        User Pain: {thread.get('user_pain')}
                        
                        My Startup:
                        Name: {startup_context.get('name')}
                        Value Prop: {startup_context.get('description')}
                        
                        Rules:
                        1. Be helpful FIRST. Answer their question.
                        2. Mention my product naturally as a solution ("I built X to solve this").
                        3. NO corporate speak. Sound like a dev/founder.
                        4. Under 100 words.
                        """
                        
                        draft_resp = await self.llm.ainvoke(draft_prompt)
                        
                        opportunities.append({
                            "platform": "reddit",
                            "type": "comment",
                            "title": thread.get('title'),
                            "url": thread.get('url'),
                            "insight": f"Pain: {thread.get('user_pain')}",
                            "draft": draft_resp.content,
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                        
            except Exception as e:
                logger.error(f"Reddit scan failed for {keyword}", error=str(e))
                continue
                
        return opportunities

# Singleton
reddit_agent = RedditSleeperAgent()
