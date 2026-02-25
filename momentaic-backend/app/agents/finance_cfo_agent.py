"""
Finance CFO Agent
LangGraph-based financial advisor and fundraising expert
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import structlog
import re

from app.agents.base import (
    AgentState,
    get_llm,
    get_agent_config,
    web_search,
    BaseAgent,
)
from app.models.conversation import AgentType
from app.services.deliverable_service import deliverable_service
from app.services.live_data_service import live_data_service

logger = structlog.get_logger()


class FinanceCFOAgent(BaseAgent):
    """
    Finance CFO Agent - Expert in startup finance and fundraising
    
    Capabilities:
    - Financial metrics analysis (MRR, ARR, burn rate, runway)
    - Unit economics calculation
    - Fundraising strategy and pitch advice
    - Financial projections
    - Investor readiness assessment
    - Benchmarking against industry standards
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.FINANCE_CFO)
        self.llm = get_llm("gemini-pro", temperature=0.3)  # Lower temp for precision
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process a financial question or request
        """
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": AgentType.FINANCE_CFO.value, "error": True}
        
        try:
            # Build financial context
            metrics = startup_context.get('metrics', {})
            context_section = self._build_context(startup_context, metrics)
            
            prompt = f"""{context_section}

User Request: {message}

As the Finance CFO, provide:
1. Direct answer with specific numbers where possible
2. Financial implications
3. Key metrics to track
4. Actionable recommendations
5. Risk considerations

Be precise with calculations and always explain the business impact."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": AgentType.FINANCE_CFO.value,
                "tools_used": [],
            }
            
        except Exception as e:
            logger.error("Finance CFO agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": AgentType.FINANCE_CFO.value, "error": True}
    
    async def analyze_metrics(
        self,
        metrics: Dict[str, Any],
        industry: str = "SaaS",
    ) -> Dict[str, Any]:
        """
        Analyze startup financial metrics
        """
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "health_score": 0, "calculated_metrics": {}, "agent": AgentType.FINANCE_CFO.value, "error": True}
        
        prompt = f"""Analyze these startup metrics for a {industry} company:

Current Metrics:
- MRR: ${metrics.get('mrr', 0):,}
- ARR: ${metrics.get('mrr', 0) * 12:,}
- Burn Rate: ${metrics.get('burn_rate', 0):,}/month
- Runway: {metrics.get('runway_months', 0)} months
- DAU: {metrics.get('dau', 0):,}
- CAC: ${metrics.get('cac', 0)}
- LTV: ${metrics.get('ltv', 0)}
- Churn: {metrics.get('churn', 0)}%

Provide:
1. Health assessment (1-10 score)
2. Key strengths
3. Areas of concern
4. Benchmark comparison
5. Top 3 priorities
6. 90-day improvement targets"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            health_score = self._calculate_health_score(metrics)
            
            return {
                "analysis": response.content,
                "health_score": health_score,
                "calculated_metrics": self._calculate_derived_metrics(metrics),
                "agent": AgentType.FINANCE_CFO.value,
            }
        except Exception as e:
            logger.error("Metrics analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "health_score": 0, "calculated_metrics": {}, "agent": AgentType.FINANCE_CFO.value, "error": True}
    
    async def fundraising_readiness(
        self,
        metrics: Dict[str, Any],
        target_raise: int,
        stage: str = "Seed",
    ) -> Dict[str, Any]:
        """
        Assess fundraising readiness
        """
        if not self.llm:
            return {"assessment": "AI Service Unavailable", "readiness_score": 0, "agent": AgentType.FINANCE_CFO.value, "error": True}
        
        prompt = f"""Assess fundraising readiness:

Target Raise: ${target_raise:,}
Stage: {stage}

Current Metrics:
- MRR: ${metrics.get('mrr', 0):,}
- Growth Rate: {metrics.get('growth_rate', 0)}% MoM
- Runway: {metrics.get('runway_months', 0)} months
- Team Size: {metrics.get('team_size', 1)}

Provide:
1. Readiness score (1-100)
2. Implied valuation range
3. What investors will ask about
4. Gaps to address before raising
5. Recommended fundraising timeline
6. Alternative funding options to consider"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "assessment": response.content,
                "readiness_score": self._calculate_readiness_score(metrics, target_raise),
                "agent": AgentType.FINANCE_CFO.value,
            }
        except Exception as e:
            logger.error("Fundraising assessment failed", error=str(e))
            return {"assessment": f"Error: {str(e)}", "readiness_score": 0, "agent": AgentType.FINANCE_CFO.value, "error": True}
    
    async def create_projection(
        self,
        current_metrics: Dict[str, Any],
        months: int = 12,
        scenario: str = "base",  # base, optimistic, pessimistic
    ) -> Dict[str, Any]:
        """
        Create financial projections
        """
        if not self.llm:
            return {"narrative": "AI Service Unavailable", "projections": [], "agent": AgentType.FINANCE_CFO.value, "error": True}
        
        prompt = f"""Create {months}-month financial projection ({scenario} case):

Starting Point:
- MRR: ${current_metrics.get('mrr', 0):,}
- Burn Rate: ${current_metrics.get('burn_rate', 0):,}/month
- Growth Rate: {current_metrics.get('growth_rate', 10)}% MoM

Provide:
1. Month-by-month MRR projection
2. Break-even point (if applicable)
3. Total cash needed
4. Key assumptions
5. Sensitivity analysis
6. Major milestones to hit"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            projections = self._calculate_projections(current_metrics, months, scenario)
            
            return {
                "narrative": response.content,
                "projections": projections,
                "agent": AgentType.FINANCE_CFO.value,
            }
        except Exception as e:
            logger.error("Projection failed", error=str(e))
            return {"narrative": f"Error: {str(e)}", "projections": [], "agent": AgentType.FINANCE_CFO.value, "error": True}
    
    async def generate_financial_model_file(
        self,
        company_name: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a downloadable financial model (CSV) with LIVE benchmarks.
        """
        try:
            # 1. Fetch live market data
            multiples = await live_data_service.get_saas_multiples()
            
            # Inject into metrics for the CSV
            metrics["valuation_multiple"] = multiples["median_arr_multiple"]
            metrics["valuation_note"] = f"Based on live SaaS index: {multiples['median_arr_multiple']}x ARR"
            
            # 2. Generate the file via service
            result = await deliverable_service.generate_financial_model_csv(metrics, company_name)
            
            return {
                "file_url": result["url"],
                "file_type": result["type"],
                "title": f"{result['title']} (Live Data)",
                "agent": AgentType.FINANCE_CFO.value,
                "benchmarks": multiples
            }
        except Exception as e:
            logger.error("Financial model generation failed", error=str(e))
            return {"error": str(e), "agent": AgentType.FINANCE_CFO.value}

    def _build_context(self, startup_context: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Build financial context"""
        return f"""Startup Financial Context:
- Name: {startup_context.get('name', 'Unknown')}
- Industry: {startup_context.get('industry', 'Technology')}
- Stage: {startup_context.get('stage', 'MVP')}
- MRR: ${metrics.get('mrr', 0):,}
- Burn Rate: ${metrics.get('burn_rate', 0):,}/month
- Runway: {metrics.get('runway_months', 'Unknown')} months"""
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate overall financial health score (1-100)"""
        score = 50  # Base score
        
        # Runway bonus
        runway = metrics.get('runway_months', 0)
        if runway >= 18:
            score += 20
        elif runway >= 12:
            score += 10
        elif runway < 6:
            score -= 20
        
        # Growth bonus
        growth = metrics.get('growth_rate', 0)
        if growth >= 20:
            score += 15
        elif growth >= 10:
            score += 10
        elif growth < 0:
            score -= 15
        
        # Unit economics
        ltv = metrics.get('ltv', 0)
        cac = metrics.get('cac', 1)
        if cac > 0 and ltv / cac >= 3:
            score += 15
        
        return max(0, min(100, score))
    
    def _calculate_derived_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived financial metrics"""
        mrr = metrics.get('mrr', 0)
        burn = metrics.get('burn_rate', 0)
        cac = metrics.get('cac', 0)
        ltv = metrics.get('ltv', 0)
        
        return {
            "arr": mrr * 12,
            "ltv_cac_ratio": round(ltv / cac, 2) if cac > 0 else None,
            "months_to_profitability": round(burn / (mrr * 0.8)) if mrr > 0 else None,
            "gross_burn": burn,
            "net_burn": burn - mrr,
        }
    
    def _calculate_readiness_score(self, metrics: Dict[str, Any], target: int) -> int:
        """Calculate fundraising readiness score"""
        score = 0
        
        mrr = metrics.get('mrr', 0)
        growth = metrics.get('growth_rate', 0)
        
        # MRR relative to raise
        if mrr * 100 >= target:  # 100x multiple
            score += 30
        elif mrr * 50 >= target:
            score += 20
        else:
            score += 10
        
        # Growth rate
        if growth >= 20:
            score += 30
        elif growth >= 10:
            score += 20
        else:
            score += 10
        
        # Team
        if metrics.get('team_size', 1) >= 3:
            score += 20
        else:
            score += 10
        
        # Runway
        if metrics.get('runway_months', 0) >= 6:
            score += 20
        else:
            score += 5
        
        return min(100, score)
    
    def _calculate_projections(
        self, metrics: Dict[str, Any], months: int, scenario: str
    ) -> List[Dict[str, Any]]:
        """Calculate month-by-month projections"""
        mrr = metrics.get('mrr', 0)
        growth_rates = {
            "pessimistic": 0.05,
            "base": 0.10,
            "optimistic": 0.20,
        }
        growth = growth_rates.get(scenario, 0.10)
        
        projections = []
        current_mrr = mrr
        
        for month in range(1, months + 1):
            current_mrr = current_mrr * (1 + growth)
            projections.append({
                "month": month,
                "mrr": round(current_mrr, 2),
                "arr": round(current_mrr * 12, 2),
            })
        
        return projections
    


# Singleton instance
finance_cfo_agent = FinanceCFOAgent()
