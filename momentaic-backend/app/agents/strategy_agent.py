"""
Strategy & Vision Agent
AI-powered strategic advisor for big-picture thinking
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm, web_search

logger = structlog.get_logger()


class StrategyAgent:
    """
    Strategy Agent - Expert in strategic planning and vision
    
    Capabilities:
    - Mission/Vision refinement
    - Strategic planning
    - Market sizing (TAM/SAM/SOM)
    - Business model analysis
    - Pivot evaluation
    - Exit strategy
    - Board preparation
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-pro", temperature=0.6)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a strategy question"""
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": "strategy", "error": True}
        
        try:
            # Deep Context Injection
            from app.agents.base import build_system_prompt
            from app.models.conversation import AgentType
            
            # Dynamically build prompt with full startup context
            system_prompt = build_system_prompt(AgentType.STRATEGY, startup_context)
            
            prompt = f"""User Request: {message}

As Strategy Advisor, provide:
1. Big-picture perspective
2. Strategic frameworks
3. Trade-off analysis
4. Long-term implications
5. Actionable next steps"""

            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": "strategy",
                "tools_used": [],
            }
        except Exception as e:
            logger.error("Strategy agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "strategy", "error": True}
    
    async def market_sizing(
        self,
        market: str,
        geography: str = "Global",
    ) -> Dict[str, Any]:
        """Calculate TAM/SAM/SOM"""
        if not self.llm:
            return {"market_analysis": "AI Service Unavailable", "agent": "strategy", "error": True}
        
        prompt = f"""Calculate market size:

Market: {market}
Geography: {geography}

Provide:
1. TAM (Total Addressable Market)
2. SAM (Serviceable Addressable Market)
3. SOM (Serviceable Obtainable Market)
4. Methodology and assumptions
5. Growth projections
6. Data sources"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "market_analysis": response.content,
                "agent": "strategy",
            }
        except Exception as e:
            logger.error("Market sizing failed", error=str(e))
            return {"market_analysis": f"Error: {str(e)}", "agent": "strategy", "error": True}
    
    async def analyze_pivot(
        self,
        current_model: str,
        proposed_pivot: str,
        reason: str,
    ) -> Dict[str, Any]:
        """Analyze pivot decision"""
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "agent": "strategy", "error": True}
        
        prompt = f"""Analyze pivot decision:

Current Model: {current_model}
Proposed Pivot: {proposed_pivot}
Reason: {reason}

Provide:
1. Pivot assessment (go/no-go)
2. What you'd gain
3. What you'd lose
4. Execution risks
5. Alternative options
6. If pivoting, key milestones"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "agent": "strategy",
            }
        except Exception as e:
            logger.error("Pivot analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "agent": "strategy", "error": True}
    
    async def business_model_canvas(
        self,
        product: str,
        description: str,
    ) -> Dict[str, Any]:
        """Generate Business Model Canvas"""
        if not self.llm:
            return {"canvas": "AI Service Unavailable", "agent": "strategy", "error": True}
        
        prompt = f"""Create Business Model Canvas:

Product: {product}
Description: {description}

Fill in all 9 blocks:
1. Customer Segments
2. Value Propositions
3. Channels
4. Customer Relationships
5. Revenue Streams
6. Key Resources
7. Key Activities
8. Key Partnerships
9. Cost Structure"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "canvas": response.content,
                "agent": "strategy",
            }
        except Exception as e:
            logger.error("Canvas generation failed", error=str(e))
            return {"canvas": f"Error: {str(e)}", "agent": "strategy", "error": True}
    
    async def prepare_board_deck(
        self,
        period: str,
        highlights: List[str],
        challenges: List[str],
    ) -> Dict[str, Any]:
        """Prepare board meeting content"""
        if not self.llm:
            return {"board_prep": "AI Service Unavailable", "agent": "strategy", "error": True}
        
        prompt = f"""Prepare board meeting for: {period}

Highlights:
{chr(10).join(f'- {h}' for h in highlights)}

Challenges:
{chr(10).join(f'- {c}' for c in challenges)}

Provide:
1. Executive summary
2. Key metrics update
3. Wins and lessons learned
4. Strategic decisions needed
5. Ask from the board
6. Next quarter priorities"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "board_prep": response.content,
                "agent": "strategy",
            }
        except Exception as e:
            logger.error("Board prep failed", error=str(e))
            return {"board_prep": f"Error: {str(e)}", "agent": "strategy", "error": True}
    
    async def exit_strategy(
        self,
        company_stage: str,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze exit options"""
        if not self.llm:
            return {"exit_analysis": "AI Service Unavailable", "agent": "strategy", "error": True}
        
        prompt = f"""Analyze exit options:

Stage: {company_stage}
ARR: ${metrics.get('arr', 0):,}
Growth: {metrics.get('growth_rate', 0)}%
Team Size: {metrics.get('team_size', 0)}

Provide:
1. Exit options (IPO, M&A, etc.)
2. Likely acquirers
3. Valuation range
4. Timeline to exit
5. What to optimize for
6. Deal-killers to avoid"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "exit_analysis": response.content,
                "agent": "strategy",
            }
        except Exception as e:
            logger.error("Exit strategy failed", error=str(e))
            return {"exit_analysis": f"Error: {str(e)}", "agent": "strategy", "error": True}
    
    def _get_system_prompt(self) -> str:
        # NOTE: This is the fallback prompt. 
        # The actual prompt used in process() is dynamic via build_system_prompt(AgentType.STRATEGY, ctx)
        return """You are the Strategy & Vision agent.
Think long-term but provide actionable steps.
Challenge assumptions and provide honest assessment.
Help founders see the bigger picture."""
    
    def _build_context(self, ctx: Dict[str, Any]) -> str:
        # Legacy method kept for compatibility, but logic moved to base.py
        return f"""Startup Context:
- Name: {ctx.get('name', 'Unknown')}
- Industry: {ctx.get('industry', 'Technology')}
- Stage: {ctx.get('stage', 'MVP')}
- Description: {ctx.get('description', '')}"""

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for strategic opportunities:
        - Market landscape changes
        - Competitive shifts
        - Strategic pivots to consider
        """
        actions = []
        industry = startup_context.get("industry", "Technology")
        
        # 1. Weekly market intelligence sweep
        actions.append({
            "action": "market_intelligence",
            "name": "market_sweep",
            "description": f"Scan for strategic shifts in {industry} landscape.",
            "priority": "medium",
            "agent": "StrategyAgent",
        })
        
        # 2. Monthly strategy review
        actions.append({
            "action": "strategy_review",
            "name": "strategy_review",
            "description": "Generate monthly strategic positioning assessment.",
            "priority": "low",
            "agent": "StrategyAgent",
        })
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Execute a proactive strategy action using REAL web search and LLM analysis.
        """
        action_type = action.get("action", action.get("name", "unknown"))
        
        try:
            if action_type == "market_intelligence":
                # Real web search for market shifts
                industry = startup_context.get("industry", "Technology")
                search_results = await web_search.ainvoke(f"{industry} market trends 2025 funding landscape shifts")
                
                if self.llm:
                    prompt = f"""Analyze these market signals for a {industry} startup:

{str(search_results)[:2000]}

Provide:
1. Top 3 strategic implications
2. Emerging threats
3. New opportunities
4. Recommended strategic adjustments"""
                    response = await self.llm.ainvoke(prompt)
                    return f"Market intelligence brief generated: {response.content[:200]}"
                return f"Market data collected: {str(search_results)[:200]}"
            
            elif action_type == "strategy_review":
                # Generate strategic positioning assessment
                if self.llm:
                    prompt = f"""Strategic positioning assessment for {startup_context.get('name', 'startup')}.
Industry: {startup_context.get('industry', 'Technology')}
Stage: {startup_context.get('stage', 'MVP')}
Description: {startup_context.get('description', '')}

Generate:
1. Current market position analysis
2. Competitive advantages
3. Strategic vulnerabilities
4. Top 3 strategic priorities for next quarter"""
                    response = await self.llm.ainvoke(prompt)
                    return f"Strategy review generated: {response.content[:200]}"
                return "LLM not available"
            
            else:
                return f"Unknown action type: {action_type}"
                
        except Exception as e:
            logger.error("Strategy autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"


# Singleton
strategy_agent = StrategyAgent()
