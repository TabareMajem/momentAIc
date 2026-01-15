"""
Instant Analysis Service
Provides the "WOW" 60-second onboarding experience by chaining multiple agents
"""

from typing import Dict, Any, AsyncGenerator
import asyncio
import json
import structlog

from app.agents.growth_hacker_agent import growth_hacker_agent
from app.agents.competitor_intel_agent import competitor_intel_agent
from app.agents.base import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

logger = structlog.get_logger()


class InstantAnalysisService:
    """
    Chains multiple agents to deliver immediate value during onboarding:
    1. GrowthHacker: Analyze startup description → Industry, Stage, Insight
    2. CompetitorIntel: Auto-discover competitors
    3. Synthesize: Generate "AI CEO Report"
    """
    
    def __init__(self):
        self._llm = None
    
    @property
    def llm(self):
        if self._llm is None:
            self._llm = get_llm("gemini-2.0-flash", temperature=0.7)
        return self._llm
    
    async def stream_analysis(
        self,
        description: str,
        user_id: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream SSE events for live progress during onboarding.
        
        Yields JSON strings formatted for SSE:
        {"event": "progress", "data": {"step": "analyzing", "message": "..."}}
        {"event": "competitor", "data": {"name": "...", "url": "..."}}
        {"event": "insight", "data": {"industry": "...", ...}}
        {"event": "complete", "data": {...full report...}}
        """
        report = {
            "industry": None,
            "stage": None,
            "summary": None,
            "insight": None,
            "competitors": [],
            "follow_up_question": None,
            "viral_hook": None,
        }
        
        try:
            # Step 1: Analyze startup
            yield self._sse_event("progress", {
                "step": "analyzing",
                "message": "🔍 Analyzing your startup concept...",
                "percent": 10
            })
            
            await asyncio.sleep(0.3)  # Small delay for UX
            
            # [REALITY UPGRADE] Auto-detect URL
            url_input = ""
            desc_input = description
            
            # Simple heuristic: if it looks like a URL, treat it as one
            if description.strip().lower().startswith("http"):
                url_input = description.strip()
                desc_input = "" # Let the scraper do the work
                
            # Use GrowthHacker's wizard analysis
            wizard_result = await growth_hacker_agent.analyze_startup_wizard(
                url=url_input,
                description=desc_input
            )
            
            if "error" not in wizard_result:
                report["industry"] = wizard_result.get("industry", "Technology")
                report["stage"] = wizard_result.get("current_stage", "idea")
                report["insight"] = wizard_result.get("biggest_opportunity", "Focus on customer discovery")
                report["viral_hook"] = wizard_result.get("viral_post_hook", "")
            
            yield self._sse_event("progress", {
                "step": "industry_detected",
                "message": f"📊 Industry: {report['industry']}",
                "percent": 30
            })
            
            await asyncio.sleep(0.2)
            
            # Step 2: Find competitors
            yield self._sse_event("progress", {
                "step": "finding_competitors",
                "message": "🏢 Discovering competitors...",
                "percent": 50
            })
            
            # Use CompetitorIntel to find competitors
            try:
                competitors_result = await competitor_intel_agent.auto_discover(
                    startup_name="",
                    description=description,
                    industry=report["industry"] or "Technology"
                )
                
                if competitors_result and isinstance(competitors_result, list):
                    for comp in competitors_result[:3]:
                        competitor_data = {
                            "name": comp.get("name", "Unknown"),
                            "url": comp.get("url", ""),
                            "description": comp.get("description", "")
                        }
                        report["competitors"].append(competitor_data)
                        
                        yield self._sse_event("competitor", competitor_data)
                        await asyncio.sleep(0.2)
                        
            except Exception as e:
                logger.warning("Competitor discovery failed", error=str(e))
                # Fallback: Use LLM to guess competitors
                report["competitors"] = await self._llm_guess_competitors(description, report["industry"])
                for comp in report["competitors"]:
                    yield self._sse_event("competitor", comp)
            
            yield self._sse_event("progress", {
                "step": "competitors_found",
                "message": f"✅ Found {len(report['competitors'])} competitors",
                "percent": 70
            })
            
            # Step 3: Generate AI CEO insight
            yield self._sse_event("progress", {
                "step": "generating_insight",
                "message": "💡 Generating strategic insight...",
                "percent": 85
            })
            
            # Use LLM for the summary and follow-up
            ceo_report = await self._generate_ceo_summary(description, report)
            report["summary"] = ceo_report.get("summary", "")
            report["follow_up_question"] = ceo_report.get("follow_up_question", "")
            
            if not report["insight"]:
                report["insight"] = ceo_report.get("insight", "")
            
            yield self._sse_event("insight", {
                "industry": report["industry"],
                "stage": report["stage"],
                "summary": report["summary"],
                "insight": report["insight"],
                "follow_up_question": report["follow_up_question"]
            })
            
            await asyncio.sleep(0.1)
            
            # Step 4: Complete
            yield self._sse_event("complete", {
                "report": report,
                "percent": 100
            })
            
        except Exception as e:
            logger.error("Instant analysis failed", error=str(e))
            yield self._sse_event("error", {
                "message": f"Analysis failed: {str(e)}"
            })
    
    async def analyze(self, description: str) -> Dict[str, Any]:
        """
        Non-streaming version for API calls that don't need SSE.
        """
        result = {}
        async for event_str in self.stream_analysis(description):
            event = json.loads(event_str.replace("data: ", ""))
            if event.get("event") == "complete":
                result = event.get("data", {}).get("report", {})
        return result
    
    async def _llm_guess_competitors(self, description: str, industry: str) -> list:
        """Fallback: Use LLM to guess competitors when web search fails."""
        if not self.llm:
            return [{"name": "Competitor 1", "url": "", "description": "Unknown"}]
        
        try:
            prompt = f"""Given this startup idea: "{description}"
In the {industry} industry.

Name 2-3 likely competitors or similar companies. Return JSON array:
[{{"name": "Company Name", "url": "https://...", "description": "One sentence"}}]

Be specific and name REAL companies if possible."""
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            import re
            content = response.content
            # Extract JSON from response
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []
        except Exception as e:
            logger.warning("LLM competitor guess failed", error=str(e))
            return []
    
    async def _generate_ceo_summary(self, description: str, partial_report: dict) -> dict:
        """Generate the AI CEO summary and follow-up question."""
        if not self.llm:
            return {
                "summary": f"Building a solution in {partial_report.get('industry', 'tech')}",
                "insight": "Focus on talking to 10 potential customers this week.",
                "follow_up_question": "What's your unfair advantage?"
            }
        
        try:
            prompt = f"""You are an AI CEO advisor. Analyze this startup:

Description: "{description}"
Industry: {partial_report.get('industry', 'Unknown')}
Stage: {partial_report.get('stage', 'idea')}
Known Competitors: {', '.join([c.get('name', '') for c in partial_report.get('competitors', [])])}

Provide:
1. A 1-sentence summary of what they're building (prove you understand)
2. ONE killer insight (non-obvious, specific, actionable)
3. The ONE question that would determine if this succeeds or fails

Return JSON:
{{"summary": "...", "insight": "...", "follow_up_question": "..."}}"""

            response = await self.llm.ainvoke([
                SystemMessage(content="You are a brilliant startup advisor. Be specific and provocative."),
                HumanMessage(content=prompt)
            ])
            
            import re
            content = response.content
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            
            return json.loads(content)
        except Exception as e:
            logger.warning("CEO summary generation failed", error=str(e))
            return {
                "summary": "An innovative startup in a competitive market.",
                "insight": "Your first 10 customers will define your entire product direction.",
                "follow_up_question": "Who is your ideal customer and why would they pay you?"
            }
    
    def _sse_event(self, event_type: str, data: dict) -> str:
        """Format as SSE event string."""
        return f"data: {json.dumps({'event': event_type, 'data': data})}\n\n"


# Singleton
instant_analysis_service = InstantAnalysisService()
