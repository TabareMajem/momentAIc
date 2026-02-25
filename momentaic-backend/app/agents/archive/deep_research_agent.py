"""
Deep Research Agent
Conducts in-depth research by reading multiple sources and synthesizing comprehensive reports.
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog
import asyncio

from app.agents.base import get_llm, web_search, read_url_content

logger = structlog.get_logger()

class DeepResearchAgent:
    """
    Deep Research Agent - Generates "State of the Union" reports
    """
    
    @property
    def llm(self):
        # Use a model with large context window for synthesis
        # 1.5-pro was 404ing, switching to flash which has 1M context too
        return get_llm("gemini-flash", temperature=0.4)

    async def research_topic(
        self,
        topic: str,
        depth: int = 3 # Number of sources to read
    ) -> Dict[str, Any]:
        """
        Conduct deep research on a topic using the Refined Search-Read-Synthesize loop.
        """
        logger.info(f"DeepResearch: Starting research on '{topic}'")
        
        try:
            # Phase 1: Scout (Search)
            search_query = f"{topic} deep dive analysis report pdf whitepaper 2024 2025"
            logger.info("DeepResearch: Phase 1 - Scouting", query=search_query)
            search_results = await web_search.ainvoke(search_query)
            
            # Extract URLs from search results (naive parsing or ask LLM)
            # For robustness, we ask LLM to pick the best URLs to read
            pick_url_prompt = f"""
            I am researching: "{topic}".
            
            Here are search results:
            {search_results}
            
            Identify the top {depth} most promising URLs to read for a deep technical/market report.
            Return ONLY a JSON list of valid URL strings. ex: ["http://...", "http://..."]
            """
            
            urls = []
            try:
                msg = await self.llm.ainvoke([HumanMessage(content=pick_url_prompt)])
                import json
                import re
                match = re.search(r'\[.*\]', msg.content, re.DOTALL)
                if match:
                    urls = json.loads(match.group(0))
            except Exception as e:
                logger.warning("DeepResearch: URL parsing failed", error=str(e))
            
            if not urls:
                # Fallback: regex find urls in search result text
                import re
                urls = re.findall(r'https?://[^\s\)]+', search_results)[:depth]

            logger.info("DeepResearch: Selected URLs", count=len(urls), urls=urls)

            # Phase 2: Read (Parallel)
            logger.info("DeepResearch: Phase 2 - Reading")
            knowledge_base = []
            
            # Limit parallelism to avoid browser overload
            for i, url in enumerate(urls[:depth]):
                try:
                    content = await read_url_content.ainvoke(url)
                    if "Failed to read" not in content:
                        knowledge_base.append(content)
                except Exception as e:
                    logger.error(f"Failed to read {url}", error=str(e))
                await asyncio.sleep(1) # Polite delay
            
            if not knowledge_base:
                return {"error": "Could not read any sources", "report": "Research failed - no sources accessible."}

            # Phase 3: Synthesize
            logger.info("DeepResearch: Phase 3 - Synthesizing", sources=len(knowledge_base))
            full_context = "\n\n".join(knowledge_base)
            
            report_prompt = f"""
            You are a Senior Market Research Analyst.
            
            Topic: {topic}
            
            Task: Write a comprehensive "State of the Union" report based ONLY on the provided source materials. 
            Do not hallucinate facts not present in the sources.
            
            Format: Markdown
            
            Structure:
            1. **Executive Summary** (TL;DR)
            2. **Key Trends & Drivers**
            3. **Market Landscape / Technical Deep Dive**
            4. **Challenges & Risks**
            5. **Future Outlook**
            6. **Sources Cited**
            
            Source Materials:
            {full_context}
            """
            
            report_response = await self.llm.ainvoke([
                SystemMessage(content="You produce high-quality, dense, and factual research reports."),
                HumanMessage(content=report_prompt)
            ])
            
            return {
                "topic": topic,
                "report": report_response.content,
                "sources_read": len(knowledge_base),
                "agent": "deep_research"
            }

        except Exception as e:
            logger.error("Deep research failed", error=str(e))
            return {"error": str(e), "report": f"Research failed due to error: {str(e)}"}

# Singleton
deep_research_agent = DeepResearchAgent()
