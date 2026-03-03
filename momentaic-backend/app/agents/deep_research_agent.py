"""
Deep Research Agent
Conducts in-depth research by reading multiple sources and synthesizing comprehensive reports.
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import structlog
import asyncio

from app.agents.base import BaseAgent, web_search, read_url_content

logger = structlog.get_logger()

class UrlListResponse(BaseModel):
    urls: List[str] = Field(description="A list of promising URLs to read for a deep technical/market report")

class DeepResearchAgent(BaseAgent):
    """
    Deep Research Agent - Generates "State of the Union" reports
    """
    # Uses BaseAgent inheritance

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
            
            try:
                response = await self.structured_llm_call(
                    prompt=pick_url_prompt,
                    response_model=UrlListResponse,
                    model_name="gemini-1.5-flash",
                    temperature=0.4
                )
                urls = response.urls
            except Exception as e:
                logger.warning("DeepResearch: URL parsing failed", error=str(e))
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
            
            try:
                report_response = await self.llm.ainvoke([
                    SystemMessage(content="You produce high-quality, dense, and factual research reports."),
                    HumanMessage(content=report_prompt)
                ])
                report_content = report_response.content
            except Exception as e:
                # Fallback if synthesis model fails (e.g. rate limit, context size limit)
                logger.error("Synthesis LLM call failed", error=str(e))
                report_content = f"Failed to synthesize report due to error: {str(e)}"
            
            return {
                "topic": topic,
                "report": report_content,
                "sources_read": len(knowledge_base),
                "agent": "deep_research"
            }

        except Exception as e:
            logger.error("Deep research failed", error=str(e))
            return {"error": str(e), "report": f"Research failed due to error: {str(e)}"}

# Singleton instance (for backward compatibility if needed, but AgentRegistry preferred)

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for industry developments, academic papers, and market shifts.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} industry developments, academic papers, and market shifts 2025")
        
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
                                "source": "DeepResearchAgent",
                                "analysis": response.content[:1500],
                                "agent": "deep_research_agent",
                            }
                        )
                    actions.append({"name": "research_topic_found", "industry": industry})
                except Exception as e:
                    logger.error(f"DeepResearchAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Conducts deep multi-source research and generates comprehensive analytical reports.
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
            
            prompt = f"""You are the Deep multi-source research and synthesis agent for a {industry} startup.

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
                        "agent": "deep_research_agent",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("DeepResearchAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

deep_research_agent = DeepResearchAgent()
