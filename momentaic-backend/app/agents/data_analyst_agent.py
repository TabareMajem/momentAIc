"""
Data Analyst Agent
AI-powered business intelligence and analytics
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm, get_agent_config
from app.models.conversation import AgentType

logger = structlog.get_logger()


class DataAnalystAgent:
    """
    Data Analyst Agent - Expert in metrics and business intelligence
    
    Capabilities:
    - Metrics interpretation
    - Cohort analysis
    - A/B test analysis
    - Dashboard recommendations
    - Trend identification
    - Anomaly detection
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-pro", temperature=0.4)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a data analytics question"""
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": "data_analyst", "error": True}
        
        
        try:
            context = self._build_context(startup_context)
            prompt = f"""{context}

User Request: {message}

As Data Analyst, provide:
1. Data-driven analysis
2. Key insights
3. Visualization recommendations
4. Statistical considerations
5. Actionable next steps"""

            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": "data_analyst",
                "tools_used": [],
            }
        except Exception as e:
            logger.error("Data Analyst agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "data_analyst", "error": True}
    
    async def analyze_ab_test(
        self,
        test_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze A/B test results"""
        stats = self._calculate_significance(test_data)
        
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "stats": stats, "agent": "data_analyst", "error": True}
        
        prompt = f"""Analyze A/B test results:

Test: {test_data.get('name', 'Unnamed')}
Duration: {test_data.get('duration_days', 0)} days

Control:
- Visitors: {test_data.get('control_visitors', 0):,}
- Conversions: {test_data.get('control_conversions', 0):,}
- Rate: {stats['control_rate']:.2%}

Variant:
- Visitors: {test_data.get('variant_visitors', 0):,}
- Conversions: {test_data.get('variant_conversions', 0):,}
- Rate: {stats['variant_rate']:.2%}

Calculated:
- Lift: {stats['lift']:.1%}
- Significant: {stats['significant']}

Provide:
1. Winner determination
2. Confidence in results
3. Business impact
4. Recommendations
5. What to test next"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "stats": stats,
                "agent": "data_analyst",
            }
        except Exception as e:
            logger.error("A/B analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "stats": stats, "agent": "data_analyst", "error": True}
    
    async def analyze_cohorts(
        self,
        cohort_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze cohort retention data"""
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "agent": "data_analyst", "error": True}
        
        prompt = f"""Analyze cohort retention:

Cohorts: {cohort_data.get('cohort_count', 0)}
Period: {cohort_data.get('period', 'weekly')}

Retention by Week:
- Week 0: 100%
- Week 1: {cohort_data.get('w1', 0)}%
- Week 2: {cohort_data.get('w2', 0)}%
- Week 4: {cohort_data.get('w4', 0)}%
- Week 8: {cohort_data.get('w8', 0)}%

Provide:
1. Retention curve analysis
2. Critical drop-off points
3. Comparison to benchmarks
4. Improvement opportunities
5. Cohort segmentation insights"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "agent": "data_analyst",
            }
        except Exception as e:
            logger.error("Cohort analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "agent": "data_analyst", "error": True}
    
    async def recommend_kpis(
        self,
        business_type: str,
        stage: str,
    ) -> Dict[str, Any]:
        """Recommend KPIs for a business"""
        if not self.llm:
            return {"recommendations": "AI Service Unavailable", "agent": "data_analyst", "error": True}
        
        prompt = f"""Recommend KPIs for:

Business Type: {business_type}
Stage: {stage}

Provide:
1. North Star metric
2. Primary KPIs (3-5)
3. Secondary metrics
4. Leading vs lagging indicators
5. Dashboard layout
6. Alert thresholds"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "recommendations": response.content,
                "agent": "data_analyst",
            }
        except Exception as e:
            logger.error("KPI recommendation failed", error=str(e))
            return {"recommendations": f"Error: {str(e)}", "agent": "data_analyst", "error": True}
    
    async def detect_anomalies(
        self,
        metric_name: str,
        values: List[float],
    ) -> Dict[str, Any]:
        """Detect anomalies in metric data"""
        anomalies = self._find_anomalies(values)
        
        return {
            "metric": metric_name,
            "anomalies": anomalies,
            "analysis": f"Found {len(anomalies)} potential anomalies in {metric_name}",
            "agent": "data_analyst",
        }
    
    def _get_system_prompt(self) -> str:
        return """You are the Data Analyst agent - expert in business analytics.

Your expertise:
- Statistical analysis
- A/B testing
- Cohort analysis
- Dashboard design
- KPI frameworks
- Data visualization

Be precise with numbers. Always consider statistical significance.
Explain findings in business terms, not just technical terms."""
    
    def _build_context(self, ctx: Dict[str, Any]) -> str:
        metrics = ctx.get('metrics', {})
        return f"""Startup Context:
- Name: {ctx.get('name', 'Unknown')}
- Industry: {ctx.get('industry', 'SaaS')}
- MRR: ${metrics.get('mrr', 0):,}
- DAU: {metrics.get('dau', 0):,}"""
    
    def _calculate_significance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate A/B test statistics"""
        c_visitors = max(data.get('control_visitors', 1), 1)
        c_conv = data.get('control_conversions', 0)
        v_visitors = max(data.get('variant_visitors', 1), 1)
        v_conv = data.get('variant_conversions', 0)
        
        c_rate = c_conv / c_visitors
        v_rate = v_conv / v_visitors
        lift = (v_rate - c_rate) / c_rate if c_rate > 0 else 0
        
        # Simplified significance (in production use scipy)
        significant = (c_visitors > 100 and v_visitors > 100 and abs(lift) > 0.05)
        
        return {
            "control_rate": c_rate,
            "variant_rate": v_rate,
            "lift": lift,
            "significant": significant,
        }
    
    def _find_anomalies(self, values: List[float]) -> List[Dict[str, Any]]:
        """Find anomalies using simple z-score"""
        if len(values) < 3:
            return []
        
        mean = sum(values) / len(values)
        std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
        
        anomalies = []
        for i, v in enumerate(values):
            if std > 0:
                z = abs((v - mean) / std)
                if z > 2:  # 2 standard deviations
                    anomalies.append({
                        "index": i,
                        "value": v,
                        "z_score": round(z, 2),
                    })
        
        return anomalies
    


# Singleton
data_analyst_agent = DataAnalystAgent()
