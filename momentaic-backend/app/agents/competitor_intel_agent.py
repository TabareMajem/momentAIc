"""
Competitor Intelligence Agent
Tracks and analyzes competitors for strategic insights
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import structlog

from app.agents.base import BaseAgent, web_search

logger = structlog.get_logger()

class CompetitorInfo(BaseModel):
    name: str = Field(description="Company Name")
    url: str = Field(description="Website URL")
    description: str = Field(description="Brief description (1 sentence)")
    reason: str = Field(description="Why they are a competitor")
    target_market: str = Field(description="Their apparent target market")

class CompetitorListResponse(BaseModel):
    competitors: List[CompetitorInfo] = Field(description="List of identified competitors")

class CompetitorAnalysisResponse(BaseModel):
    overview: str = Field(description="What they do, founding date, funding")
    target_market: str = Field(description="Who are their customers?")
    key_features: str = Field(description="What are their main product features?")
    pricing_model: str = Field(description="How do they charge? Price points?")
    strengths: str = Field(description="What do they do well?")
    weaknesses: str = Field(description="Where are they vulnerable?")
    positioning: str = Field(description="How do they position themselves?")
    recent_news: str = Field(description="Any recent developments?")

class BattleCardResponse(BaseModel):
    quick_facts: Dict[str, str] = Field(description="Key comparison points")
    when_they_say: str = Field(description="Common objections and how to respond")
    our_advantages: List[str] = Field(description="Our advantages over them")
    their_weaknesses: List[str] = Field(description="Their weaknesses to exploit")
    red_flags: List[str] = Field(description="Situations where the competitor wins")

class CompetitorAlert(BaseModel):
    has_news: bool = Field(description="Is there any SIGNIFICANT news?")
    alert_summary: str = Field(description="1-sentence summary of the alert if there is news, else empty string")

class CompetitorIntelAgent(BaseAgent):
    """
    Competitor Intelligence Agent - Tracks and analyzes competitors
    
    Capabilities:
    - Identify competitors in a market
    - Analyze competitor websites and positioning
    - Track pricing changes
    - Monitor feature launches
    - Generate competitive battle cards
    """
    
    # Uses BaseAgent inheritance
    
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
            search_results = await web_search.ainvoke(search_query)
            
            enhanced_prompt = f"""{prompt}

Here are some search results for context:
{search_results}

Use this information to provide accurate, real competitor data."""

            response = await self.structured_llm_call(
                prompt=enhanced_prompt,
                response_model=CompetitorListResponse,
                model_name="gemini-1.5-flash",
                temperature=0.4
            )
            
            # Format nicely for the output
            formatted = "\n".join([f"- **{c.name}** ({c.url}): {c.description}" for c in response.competitors])
            
            return {
                "competitors": formatted,
                "agent": "competitor_intel",
                "search_performed": True
            }
            
        except Exception as e:
            logger.error("Competitor identification failed", error=str(e))
            return {"error": str(e), "competitors": []}
    
    async def auto_discover(
        self,
        startup_name: str,
        description: str,
        industry: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Quick competitor discovery for onboarding flow.
        Returns structured list of competitors with name, url, description.
        """
        if not self.llm:
            return []
        
        try:
            # Search for competitors
            search_query = f"{industry} {description[:100]} alternatives competitors startups"
            search_results = await web_search.ainvoke(search_query)
            
            prompt = f"""Find {limit} competitors for a startup in {industry}.

Startup description: "{description}"

Search Results for context:
{search_results}

Return ONLY a JSON array with this exact format:
[
  {{"name": "Company Name", "url": "https://company.com", "description": "One sentence about them"}}
]

Be specific. Name REAL companies. If you can't find real ones, make educated guesses based on the industry."""

            response = await self.structured_llm_call(
                prompt=prompt,
                response_model=CompetitorListResponse,
                model_name="gemini-1.5-flash",
                temperature=0.3
            )
            
            return [{"name": c.name, "url": c.url, "description": c.description} for c in response.competitors[:limit]]
            
        except Exception as e:
            logger.error("Auto discover failed", error=str(e))
            return []

    
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
            response = await self.structured_llm_call(
                prompt=prompt,
                response_model=CompetitorAnalysisResponse,
                model_name="gemini-1.5-flash",
                temperature=0.3
            )
            
            formatted_analysis = f"""
### 📊 Overview
{response.overview}

### 🎯 Target Market
{response.target_market}

### ⚙️ Key Features
{response.key_features}

### 💰 Pricing Model
{response.pricing_model}

### 💪 Strengths
{response.strengths}

### ⚖️ Weaknesses
{response.weaknesses}

### 🗺️ Positioning
{response.positioning}

### 📰 Recent News
{response.recent_news}
"""
            
            return {
                "analysis": formatted_analysis,
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

            response = await self.structured_llm_call(
                prompt=prompt,
                response_model=BattleCardResponse,
                model_name="gemini-1.5-flash",
                temperature=0.4
            )
            
            formatted_battle_card = f"""
## Quick Facts
{chr(10).join(f"- **{k}**: {v}" for k,v in response.quick_facts.items())}

## Talk Tracks

### When They Say...
{response.when_they_say}

### Our Advantages
{chr(10).join(f"- {adv}" for adv in response.our_advantages)}

### Their Weaknesses to Exploit
{chr(10).join(f"- {weakness}" for weakness in response.their_weaknesses)}

### Red Flags (When NOT to compete)
{chr(10).join(f"- {flag}" for flag in response.red_flags)}
"""
            
            return {
                "battle_card": formatted_battle_card.strip(),
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


    async def monitor_market(
        self,
        startup_context: Dict[str, Any],
        known_competitors: List[str]
    ) -> Dict[str, Any]:
        """
        Autonomous monitoring: Discovery or Surveillance
        """
        if not self.llm:
            return {"error": "LLM invalid"}

        # 1. Discovery Mode (If no competitors known)
        if not known_competitors:
            logger.info("CompetitorIntel: Starting auto-discovery")
            
            industry = startup_context.get("industry", "Technology")
            description = startup_context.get("description", "")
            
            try:
                search_query = f"{industry} {description[:100]} alternatives competitors startups"
                search_results = await web_search.ainvoke(search_query)
                
                prompt = f"""Find 3 competitors for a startup in {industry}.

Startup description: "{description}"

Search Results for context:
{search_results}"""
                
                response = await self.structured_llm_call(
                    prompt=prompt,
                    response_model=CompetitorListResponse,
                    model_name="gemini-1.5-flash",
                    temperature=0.3
                )
                new_competitors = [c.name for c in response.competitors]
                summary = "\n".join([f"- {c.name}: {c.description}" for c in response.competitors])
                
            except Exception as e:
                logger.error("Competitor discovery failed", error=str(e))
                new_competitors = []
                summary = "Failed to discover competitors"

            return {
                "mode": "discovery",
                "new_competitors": new_competitors,
                "summary": summary
            }

        # 2. Surveillance Mode (If competitors exist)
        logger.info("CompetitorIntel: Surveillance run", targets=known_competitors)
        updates = []
        
        for comp in known_competitors[:3]: # Limit to top 3 to save time/tokens
            try:
                # Search for recent news
                query = f"{comp} company news details pricing changes features last month"
                search_results = await web_search.ainvoke(query)
                
                # Analyze if meaningful
                analysis_prompt = f"""
                Is there any SIGNIFICANT news in these search results for competitor "{comp}"?
                Focus on: Pricing changes, Major feature launches, Funding, or Pivots.
                
                Search Results:
                {search_results}
                """
                
                resp = await self.structured_llm_call(
                    prompt=analysis_prompt,
                    response_model=CompetitorAlert,
                    model_name="gemini-1.5-flash",
                    temperature=0.1
                )
                
                if resp.has_news and resp.alert_summary.strip():
                    updates.append(f"⚠️ {comp}: {resp.alert_summary}")
                    
            except Exception as e:
                logger.error(f"Failed to scan {comp}", error=str(e))
                
        return {
            "mode": "surveillance",
            "updates": updates,
            "checked_count": len(known_competitors)
        }

# Singleton instance (for backward compatibility if needed, but AgentRegistry preferred)
competitor_intel_agent = CompetitorIntelAgent()
