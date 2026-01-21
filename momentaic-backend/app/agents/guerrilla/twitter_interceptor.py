"""
Twitter Interceptor Agent ("The Shark")
Monitors competitor mentions for negative sentiment and drafts intercept replies.
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog
import datetime

from app.agents.base import get_llm, web_search
from app.models.conversation import AgentType

logger = structlog.get_logger()

class TwitterInterceptorAgent:
    """
    Twitter Interceptor Agent
    - Monitors @Competitor mentions
    - Detects negative sentiment (churn risk)
    - Drafts tactical replies
    """
    
    @property
    def llm(self):
        return get_llm("gemini-flash", temperature=0.6)
    
    async def hunt_competitors(
        self,
        competitors: List[str],
        startup_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find tweets complaining about competitors.
        """
        if not self.llm:
            return []

        intercepts = []
        
        for competitor in competitors:
            try:
                # 1. Search for negative tweets
                # Refined queries to catch complaints
                query = f"site:twitter.com OR site:x.com @{competitor} (sucks OR broken OR expensive OR switch OR down OR hate) -filter:retweets"
                search_results = await web_search.ainvoke(query)
                
                # 2. Analyze sentiment and opportunity
                prompt = f"""
                Analyze these tweets about competitor "{competitor}":
                {search_results}
                
                Identify tweets where a user is:
                1. Frustrated with the service
                2. Looking to switch
                3. Complaining about price or downtime
                
                Return a JSON list:
                [
                    {{
                        "handle": "User handle (if visible)",
                        "tweet_text": "The complaint content",
                        "url": "Tweet URL",
                        "complaint_type": "price/downtime/features"
                    }}
                ]
                """
                
                analysis_response = await self.llm.ainvoke([
                    SystemMessage(content="You are a social listening expert. Find dissatisfied users."),
                    HumanMessage(content=prompt)
                ])
                
                import json
                import re
                try:
                    content = analysis_response.content
                    match = re.search(r'\[.*\]', content, re.DOTALL)
                    tweets = json.loads(match.group(0)) if match else []
                except:
                    tweets = []
                
                # 3. Draft Intercepts
                for tweet in tweets:
                    draft_prompt = f"""
                    Draft a reply to this tweet:
                    
                    Complaint: "{tweet.get('tweet_text')}"
                    Competitor: {competitor}
                    Complaint Type: {tweet.get('complaint_type')}
                    
                    My Startup: {startup_context.get('name')}
                    Description: {startup_context.get('description')}
                    
                    Goal: Empathize and subtly pitch us as the better alternative.
                    Tone: Friendly, helpful, not aggressive. "Hey, sorry to hear that. You might like..."
                    Max 280 chars.
                    """
                    
                    draft_resp = await self.llm.ainvoke(draft_prompt)
                    
                    intercepts.append({
                        "platform": "twitter",
                        "type": "reply",
                        "url": tweet.get('url'),
                        "insight": f"Complaint: {tweet.get('complaint_type')} about {competitor}",
                        "draft": draft_resp.content,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                        
            except Exception as e:
                logger.error(f"Twitter intercept failed for {competitor}", error=str(e))
                continue
                
        return intercepts

# Singleton
twitter_interceptor = TwitterInterceptorAgent()
