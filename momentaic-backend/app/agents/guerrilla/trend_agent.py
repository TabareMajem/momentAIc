"""
Trend Surfer Agent ("The Surfer")
Identifies viral trends and generates product-aligned "hot takes".
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog
import datetime

from app.agents.base import get_llm, web_search
from app.models.conversation import AgentType

logger = structlog.get_logger()

class TrendSurferAgent:
    """
    Trend Surfer Agent
    - Scans for global/tech trends
    - Identifies "jackable" topics
    - Generates controversial/insightful takes connecting trend to product
    """
    
    @property
    def llm(self):
        return get_llm("gemini-flash", temperature=0.8)
    
    async def surf_trends(
        self,
        startup_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find trends and generate content.
        """
        if not self.llm:
            return []

        trends = []
        industry = startup_context.get("industry", "Technology")
        
        try:
            # 1. Search for trends
            query = f"trending topics {industry} tech news today viral twitter trends"
            search_results = await web_search.ainvoke(query)
            
            # 2. Analyze for relevance
            prompt = f"""
            Identify 3 viral trends or hot topics from these search results:
            {search_results}
            
            My Startup:
            Name: {startup_context.get('name')}
            Mission: {startup_context.get('description')}
            
            For each trend, explain WHY it matters to my startup (the "Bridge").
            
            Return JSON list:
            [
                {{
                    "topic": "Trend Name",
                    "context": "Why it's trending",
                    "angle": "How to connect it to us"
                }}
            ]
            """
            
            analysis_response = await self.llm.ainvoke([
                SystemMessage(content="You are a viral marketing expert."),
                HumanMessage(content=prompt)
            ])
            
            import json
            import re
            try:
                content = analysis_response.content
                match = re.search(r'\[.*\]', content, re.DOTALL)
                trend_topics = json.loads(match.group(0)) if match else []
            except:
                trend_topics = []
            
            # 3. Generate Hot Takes
            for topic in trend_topics:
                draft_prompt = f"""
                Write a "Hot Take" tweet (under 280 chars) connecting this trend to my product.
                
                Trend: {topic.get('topic')}
                Context: {topic.get('context')}
                Angle: {topic.get('angle')}
                
                My Product: {startup_context.get('name')}
                
                Style: Controversial, insightful, or counter-intuitive.
                Start with a hook.
                """
                
                draft_resp = await self.llm.ainvoke(draft_prompt)
                
                trends.append({
                    "platform": "twitter/linkedin",
                    "type": "trend_jack",
                    "topic": topic.get('topic'),
                    "insight": topic.get('angle'),
                    "draft": draft_resp.content,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                    
        except Exception as e:
            logger.error("Trend surf failed", error=str(e))
            
        return trends

# Singleton
trend_agent = TrendSurferAgent()
