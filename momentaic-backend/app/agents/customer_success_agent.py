"""
Customer Success Agent
AI-powered customer success manager
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm, get_agent_config, web_search
from app.models.conversation import AgentType

logger = structlog.get_logger()


class CustomerSuccessAgent:
    """
    Customer Success Agent - Expert in customer retention and satisfaction
    
    Capabilities:
    - Churn risk analysis
    - Customer health scoring
    - Success playbooks
    - Onboarding optimization
    - QBR preparation
    - Upsell identification
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-pro", temperature=0.6)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a customer success question"""
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": "customer_success", "error": True}
        
        try:
            context = self._build_context(startup_context)
            prompt = f"""{context}

User Request: {message}

As Customer Success expert, provide:
1. Direct actionable advice
2. Customer health considerations
3. Retention strategies
4. Metrics to track
5. Playbook recommendations"""

            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": "customer_success",
                "tools_used": [],
            }
        except Exception as e:
            logger.error("Customer Success agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "customer_success", "error": True}
    
    async def analyze_churn_risk(
        self,
        customer_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze churn risk for a customer"""
        risk_score = self._calculate_risk_score(customer_data)
        
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "risk_score": risk_score, "agent": "customer_success", "error": True}
        
        prompt = f"""Analyze churn risk:

Customer Data:
- Last login: {customer_data.get('last_login', 'Unknown')}
- Usage trend: {customer_data.get('usage_trend', 'Unknown')}
- Support tickets: {customer_data.get('support_tickets', 0)}
- NPS score: {customer_data.get('nps', 'Not collected')}
- Account age: {customer_data.get('account_age_months', 0)} months

Calculated Risk Score: {risk_score}/100

Provide:
1. Risk assessment
2. Warning signs
3. Immediate actions
4. Re-engagement strategy"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "risk_score": risk_score,
                "agent": "customer_success",
            }
        except Exception as e:
            logger.error("Churn analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "risk_score": risk_score, "agent": "customer_success", "error": True}
    
    async def create_success_playbook(
        self,
        customer_segment: str,
        goals: List[str],
    ) -> Dict[str, Any]:
        """Create a customer success playbook"""
        if not self.llm:
            return {"playbook": "AI Service Unavailable", "agent": "customer_success", "error": True}
        
        prompt = f"""Create success playbook for:

Segment: {customer_segment}
Goals: {', '.join(goals)}

Include:
1. Onboarding milestones (first 30/60/90 days)
2. Success metrics per milestone
3. Touchpoint schedule
4. Health check triggers
5. Escalation procedures
6. Expansion opportunities"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "playbook": response.content,
                "agent": "customer_success",
            }
        except Exception as e:
            logger.error("Playbook creation failed", error=str(e))
            return {"playbook": f"Error: {str(e)}", "agent": "customer_success", "error": True}
    
    async def triage_ticket(self, ticket_content: str, sender_sentiment: str = "neutral") -> Dict[str, Any]:
        """Classify a support ticket and draft a reply"""
        if not self.llm:
            return {"classification": "error", "draft": "Service Unavailable"}
            
        prompt = f"""Triage this support ticket:
"{ticket_content}"
(Sentiment: {sender_sentiment})

Output JSON:
1. "priority": High/Medium/Low
2. "category": Technical/Billing/Feature/Other
3. "draft_reply": Empathetic and helpful response (max 100 words)
4. "action_required": Internal action needed if any
"""
        try:
            from langchain_core.output_parsers import JsonOutputParser
            chain = self.llm | JsonOutputParser()
            result = await chain.ainvoke([HumanMessage(content=prompt)])
            return result
        except Exception as e:
             # Fallback parsing
            return {"priority": "Medium", "category": "General", "draft_reply": "Thank you for your message. We are looking into it.", "item": str(e)}
    
    def _get_system_prompt(self) -> str:
        return """You are the Customer Success agent - expert in customer retention.

Your expertise:
- Churn prediction and prevention
- Customer health scoring
- Onboarding optimization
- NPS and satisfaction management
- Upsell and expansion strategies

Focus on proactive engagement and data-driven decisions."""
    
    def _build_context(self, ctx: Dict[str, Any]) -> str:
        metrics = ctx.get('metrics', {})
        return f"""Startup Context:
- Product: {ctx.get('name', 'Unknown')}
- Industry: {ctx.get('industry', 'SaaS')}
- Churn rate: {metrics.get('churn', 'Unknown')}%
- NPS: {metrics.get('nps', 'Unknown')}"""
    
    def _calculate_risk_score(self, data: Dict[str, Any]) -> int:
        """Calculate churn risk score (0-100, higher = more risk)"""
        score = 30  # Base
        
        # Usage decline
        if data.get('usage_trend') == 'declining':
            score += 25
        
        # Support issues
        tickets = data.get('support_tickets', 0)
        if tickets > 5:
            score += 20
        elif tickets > 2:
            score += 10
        
        # Low NPS
        nps = data.get('nps')
        if nps and nps < 6:
            score += 25
        
        return min(100, score)
    


# Singleton
customer_success_agent = CustomerSuccessAgent()
