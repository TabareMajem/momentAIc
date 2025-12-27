"""
Growth Hacker Agent
AI-powered growth expert for startups
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import structlog

from app.agents.base import (
    AgentState,
    get_llm,
    get_agent_config,
    web_search,
    get_trending_topics,
)
from app.models.conversation import AgentType

logger = structlog.get_logger()


class GrowthHackerAgent:
    """
    Growth Hacker Agent - Expert in startup growth strategies
    
    Capabilities:
    - Growth experiment design
    - Acquisition channel analysis
    - Conversion funnel optimization
    - Retention strategies
    - Viral loop identification
    - A/B testing recommendations
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.GROWTH_HACKER)
        self.llm = get_llm("gemini-pro", temperature=0.7)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process a growth-related question or request
        """
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        try:
            context_section = self._build_context(startup_context)
            
            prompt = f"""{context_section}

User Request: {message}

As the Growth Hacker, provide:
1. Direct, actionable advice
2. Specific tactics they can implement today
3. Metrics to track
4. Expected timeline and effort
5. Examples from similar startups

Focus on high-impact, low-cost growth tactics suitable for their stage."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": AgentType.GROWTH_HACKER.value,
                "tools_used": [],
            }
            
        except Exception as e:
            logger.error("Growth Hacker agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    async def design_experiment(
        self,
        goal: str,
        current_metrics: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Design a growth experiment
        """
        constraints = constraints or {"budget": 0, "time": "1 week"}
        
        if not self.llm:
            return {"experiment_design": "AI Service Unavailable", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        prompt = f"""Design a growth experiment:

Goal: {goal}

Current Metrics:
- DAU: {current_metrics.get('dau', 0):,}
- WAU: {current_metrics.get('wau', 0):,}
- Conversion Rate: {current_metrics.get('conversion_rate', 0)}%
- Churn: {current_metrics.get('churn', 0)}%

Constraints:
- Budget: ${constraints.get('budget', 0)}
- Time: {constraints.get('time', '1 week')}
- Team Size: {constraints.get('team_size', 1)}

Provide:
1. Experiment hypothesis
2. Specific tactics to test
3. Control vs variant setup
4. Success metrics
5. Statistical significance requirements
6. Implementation steps
7. Rollback plan"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "experiment_design": response.content,
                "agent": AgentType.GROWTH_HACKER.value,
            }
        except Exception as e:
            logger.error("Experiment design failed", error=str(e))
            return {"experiment_design": f"Error: {str(e)}", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    async def analyze_funnel(
        self,
        funnel_data: Dict[str, Any],
        industry: str = "SaaS",
    ) -> Dict[str, Any]:
        """
        Analyze conversion funnel and identify leaks
        """
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "biggest_leak": "No Data", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        prompt = f"""Analyze this {industry} conversion funnel:

Funnel Steps:
- Visitors: {funnel_data.get('visitors', 0):,}
- Signups: {funnel_data.get('signups', 0):,} ({self._calc_rate(funnel_data.get('signups', 0), funnel_data.get('visitors', 1))}%)
- Activated: {funnel_data.get('activated', 0):,} ({self._calc_rate(funnel_data.get('activated', 0), funnel_data.get('signups', 1))}%)
- Retained (D7): {funnel_data.get('d7_retained', 0):,}
- Paid: {funnel_data.get('paid', 0):,}

Provide:
1. Biggest leak identification
2. Industry benchmark comparison
3. Top 3 optimization opportunities
4. Quick wins (implement in <1 day)
5. Strategic improvements (1-4 weeks)
6. Metrics to track improvements"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "biggest_leak": self._identify_biggest_leak(funnel_data),
                "agent": AgentType.GROWTH_HACKER.value,
            }
        except Exception as e:
            logger.error("Funnel analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "biggest_leak": "Error", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    async def acquisition_channels(
        self,
        startup_context: Dict[str, Any],
        budget: int = 0,
    ) -> Dict[str, Any]:
        """
        Recommend acquisition channels
        """
        if not self.llm:
            return {"recommendations": "AI Service Unavailable", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        prompt = f"""Recommend acquisition channels:

Startup:
- Industry: {startup_context.get('industry', 'Technology')}
- Target Customer: {startup_context.get('target_customer', 'B2B SMBs')}
- Price Point: ${startup_context.get('price_point', 50)}/month
- Current Stage: {startup_context.get('stage', 'MVP')}

Budget: ${budget:,}/month

Provide:
1. Top 5 recommended channels (ranked)
2. Expected CAC for each
3. Time to results
4. Effort required
5. Playbook for #1 channel
6. Channels to avoid at this stage"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "recommendations": response.content,
                "agent": AgentType.GROWTH_HACKER.value,
            }
        except Exception as e:
            logger.error("Channel analysis failed", error=str(e))
            return {"recommendations": f"Error: {str(e)}", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    async def viral_loop_design(
        self,
        product_type: str,
        current_k_factor: float = 0,
    ) -> Dict[str, Any]:
        """
        Design viral growth loops
        """
        if not self.llm:
            return {"viral_strategy": "AI Service Unavailable", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        prompt = f"""Design viral growth loops for:

Product Type: {product_type}
Current K-factor: {current_k_factor}
Target K-factor: 1.0+

Provide:
1. Natural viral mechanics in your product
2. Incentive-based referral program design
3. Network effects to leverage
4. Viral content opportunities
5. Sharing friction reduction tactics
6. K-factor improvement roadmap"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "viral_strategy": response.content,
                "agent": AgentType.GROWTH_HACKER.value,
            }
        except Exception as e:
            logger.error("Viral loop design failed", error=str(e))
            return {"viral_strategy": f"Error: {str(e)}", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    async def retention_strategy(
        self,
        cohort_data: Dict[str, Any],
        product_type: str,
    ) -> Dict[str, Any]:
        """
        Design retention improvement strategy
        """
        if not self.llm:
            return {"retention_plan": "AI Service Unavailable", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        prompt = f"""Design retention strategy:

Product: {product_type}

Retention Data:
- D1: {cohort_data.get('d1', 0)}%
- D7: {cohort_data.get('d7', 0)}%
- D30: {cohort_data.get('d30', 0)}%
- Monthly Churn: {cohort_data.get('monthly_churn', 0)}%

Provide:
1. Retention curve analysis
2. Critical drop-off points
3. Engagement triggers to implement
4. Re-engagement campaign ideas
5. Onboarding optimization
6. 90-day retention roadmap"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "retention_plan": response.content,
                "agent": AgentType.GROWTH_HACKER.value,
            }
        except Exception as e:
            logger.error("Retention strategy failed", error=str(e))
            return {"retention_plan": f"Error: {str(e)}", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    def _build_context(self, startup_context: Dict[str, Any]) -> str:
        """Build startup context"""
        return f"""Startup Context:
- Name: {startup_context.get('name', 'Unknown')}
- Industry: {startup_context.get('industry', 'Technology')}
- Stage: {startup_context.get('stage', 'MVP')}
- MRR: ${startup_context.get('metrics', {}).get('mrr', 0):,}
- DAU: {startup_context.get('metrics', {}).get('dau', 0):,}"""
    
    def _calc_rate(self, numerator: int, denominator: int) -> str:
        """Calculate percentage rate"""
        if denominator == 0:
            return "0"
        return f"{(numerator / denominator) * 100:.1f}"
    
    def _identify_biggest_leak(self, funnel: Dict[str, Any]) -> str:
        """Identify biggest conversion drop"""
        steps = [
            ("visitor→signup", funnel.get('signups', 0) / max(funnel.get('visitors', 1), 1)),
            ("signup→activated", funnel.get('activated', 0) / max(funnel.get('signups', 1), 1)),
            ("activated→retained", funnel.get('d7_retained', 0) / max(funnel.get('activated', 1), 1)),
            ("retained→paid", funnel.get('paid', 0) / max(funnel.get('d7_retained', 1), 1)),
        ]
        return min(steps, key=lambda x: x[1])[0]
    


# Singleton instance
growth_hacker_agent = GrowthHackerAgent()
