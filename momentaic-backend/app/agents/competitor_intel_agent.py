"""
Competitor Intelligence Agent
Tracks and analyzes competitors for strategic insights
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm, web_search
from app.models.conversation import AgentType

logger = structlog.get_logger()


class CompetitorIntelAgent:
    """
    Competitor Intelligence Agent - Tracks and analyzes competitors
    
    Capabilities:
    - Identify competitors in a market
    - Analyze competitor websites and positioning
    - Track pricing changes
    - Monitor feature launches
    - Generate competitive battle cards
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-2.0-flash", temperature=0.5)
    
    async def identify_competitors(
        self,
        startup_context: Dict[str, Any],
        num_competitors: int = 5
    ) -> Dict[str, Any]:
        """
        Identify key competitors based on startup context
        """
        if not self.llm:
            return {"error": "LLM not available", "competitors": []}
        
        industry = startup_context.get("industry", "Technology")
        description = startup_context.get("description", "")
        
        prompt = f"""You are a competitive intelligence analyst.

Based on this startup:
- Industry: {industry}
- Description: {description}

Identify the top {num_competitors} direct and indirect competitors.

For each competitor, provide:
1. Company Name
2. Website URL
3. Brief description (1 sentence)
4. Why they're a competitor
5. Their apparent target market

Format as a structured list."""

        try:
            # Try web search first for real data
            search_query = f"{industry} {description[:50]} competitors startups"
            search_results = web_search(search_query)
            
            enhanced_prompt = f"""{prompt}

Here are some search results for context:
{search_results}

Use this information to provide accurate, real competitor data."""

            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert competitive intelligence analyst. Be factual and specific."),
                HumanMessage(content=enhanced_prompt)
            ])
            
            return {
                "competitors": response.content,
                "agent": "competitor_intel",
                "search_performed": True
            }
            
        except Exception as e:
            logger.error("Competitor identification failed", error=str(e))
            return {"error": str(e), "competitors": []}
    
    async def analyze_competitor(
        self,
        competitor_name: str,
        competitor_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deep analysis of a specific competitor
        """
        if not self.llm:
            return {"error": "LLM not available"}
        
        try:
            # Search for competitor info
            search_results = web_search(f"{competitor_name} company product features pricing")
            
            prompt = f"""Analyze this competitor in detail:

Company: {competitor_name}
Website: {competitor_url or 'Unknown'}

Search Results:
{search_results}

Provide a comprehensive analysis including:
1. **Overview**: What they do, founding date, funding
2. **Target Market**: Who are their customers?
3. **Key Features**: What are their main product features?
4. **Pricing Model**: How do they charge? Price points?
5. **Strengths**: What do they do well?
6. **Weaknesses**: Where are they vulnerable?
7. **Positioning**: How do they position themselves?
8. **Recent News**: Any recent developments?

Be specific and factual. If information is unavailable, say so."""

            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert competitive intelligence analyst. Provide actionable insights."),
                HumanMessage(content=prompt)
            ])
            
            return {
                "analysis": response.content,
                "competitor": competitor_name,
                "agent": "competitor_intel"
            }
            
        except Exception as e:
            logger.error("Competitor analysis failed", error=str(e))
            return {"error": str(e)}
    
    async def generate_battle_card(
        self,
        startup_context: Dict[str, Any],
        competitor_name: str
    ) -> Dict[str, Any]:
        """
        Generate a sales battle card for competing against a specific competitor
        """
        if not self.llm:
            return {"error": "LLM not available"}
        
        try:
            # Get competitor intel
            competitor_analysis = await self.analyze_competitor(competitor_name)
            
            startup_name = startup_context.get("name", "Our Product")
            
            prompt = f"""Create a sales battle card for {startup_name} vs {competitor_name}.

Our Startup:
- Name: {startup_name}
- Industry: {startup_context.get('industry', 'Technology')}
- Description: {startup_context.get('description', '')}

Competitor Analysis:
{competitor_analysis.get('analysis', 'Limited data available')}

Generate a battle card with:

## Quick Facts
| Aspect | {startup_name} | {competitor_name} |
|--------|--------------|------------------|
| Target Market | | |
| Pricing | | |
| Key Differentiator | | |

## Talk Tracks

### When They Say...
(Common objections/comparisons and how to respond)

### Our Advantages
- Advantage 1
- Advantage 2
- Advantage 3

### Their Weaknesses to Exploit
- Weakness 1
- Weakness 2

### Red Flags (When NOT to compete)
- Situation where competitor wins

Make it practical and actionable for sales conversations."""

            response = await self.llm.ainvoke([
                SystemMessage(content="You are a sales enablement expert creating competitive battle cards."),
                HumanMessage(content=prompt)
            ])
            
            return {
                "battle_card": response.content,
                "competitor": competitor_name,
                "agent": "competitor_intel"
            }
            
        except Exception as e:
            logger.error("Battle card generation failed", error=str(e))
            return {"error": str(e)}
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process a competitive intelligence request
        """
        message_lower = message.lower()
        
        try:
            # Intent detection
            if "identify" in message_lower or "find" in message_lower or "who are" in message_lower:
                result = await self.identify_competitors(startup_context)
                return {
                    "response": f"**Competitor Analysis**\n\n{result.get('competitors', 'No data')}",
                    "agent": "competitor_intel"
                }
            
            if "battle card" in message_lower:
                # Extract competitor name from message
                # Simple extraction - in production use NER
                words = message.split()
                competitor = " ".join(words[-2:]) if len(words) > 2 else "competitor"
                result = await self.generate_battle_card(startup_context, competitor)
                return {
                    "response": result.get("battle_card", "Could not generate battle card"),
                    "agent": "competitor_intel"
                }
            
            if "analyze" in message_lower:
                # Extract competitor name
                words = message.replace("analyze", "").strip().split()
                competitor = " ".join(words) if words else "competitor"
                result = await self.analyze_competitor(competitor)
                return {
                    "response": result.get("analysis", "Could not analyze competitor"),
                    "agent": "competitor_intel"
                }
            
            # Default: provide overview
            return {
                "response": """I'm the **Competitor Intelligence Agent**. I can help you:

🔍 **Identify Competitors**: "Find my competitors"
📊 **Analyze a Competitor**: "Analyze [Company Name]"
⚔️ **Generate Battle Card**: "Create battle card for [Company Name]"

What would you like to know about your competitive landscape?""",
                "agent": "competitor_intel"
            }
            
        except Exception as e:
            logger.error("Competitor intel processing failed", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "competitor_intel", "error": True}


# Singleton
competitor_intel_agent = CompetitorIntelAgent()
