"""
DevOps/Infrastructure Agent
AI-powered infrastructure and deployment advisor
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm, web_search

logger = structlog.get_logger()


class DevOpsAgent:
    """
    DevOps Agent - Expert in infrastructure and deployment
    
    Capabilities:
    - Deployment strategies
    - CI/CD pipeline design
    - Cloud architecture
    - Cost optimization
    - Monitoring setup
    - Security hardening
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-pro", temperature=0.4)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a DevOps question"""
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": "devops", "error": True}
        
        try:
            context = self._build_context(startup_context)
            prompt = f"""{context}

User Request: {message}

As DevOps expert, provide:
1. Technical recommendations
2. Implementation steps
3. Best practices
4. Security considerations
5. Cost implications"""

            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": "devops",
                "tools_used": [],
            }
        except Exception as e:
            logger.error("DevOps agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "devops", "error": True}
    
    async def design_cicd(
        self,
        tech_stack: List[str],
        deployment_target: str,
    ) -> Dict[str, Any]:
        """Design CI/CD pipeline"""
        if not self.llm:
            return {"pipeline_design": "AI Service Unavailable", "agent": "devops", "error": True}
        
        prompt = f"""Design CI/CD pipeline:

Tech Stack: {', '.join(tech_stack)}
Deploy To: {deployment_target}

Provide:
1. Pipeline stages
2. Tool recommendations
3. GitHub Actions workflow
4. Testing strategy
5. Deployment strategy
6. Rollback procedures"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "pipeline_design": response.content,
                "agent": "devops",
            }
        except Exception as e:
            logger.error("CI/CD design failed", error=str(e))
            return {"pipeline_design": f"Error: {str(e)}", "agent": "devops", "error": True}
    
    async def recommend_hosting(
        self,
        requirements: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Recommend hosting solution"""
        if not self.llm:
            return {"recommendation": "AI Service Unavailable", "agent": "devops", "error": True}
        
        prompt = f"""Recommend hosting for:

Requirements:
- Expected traffic: {requirements.get('traffic', 'Unknown')}
- Database needs: {requirements.get('database', 'PostgreSQL')}
- Budget: ${requirements.get('budget', 100)}/month
- Team DevOps experience: {requirements.get('experience', 'Low')}

Compare and recommend:
1. Vercel/Railway/Render (PaaS)
2. AWS/GCP/Azure (IaaS)
3. Cost breakdown
4. Scaling path
5. Tradeoffs"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "recommendation": response.content,
                "agent": "devops",
            }
        except Exception as e:
            logger.error("Hosting recommendation failed", error=str(e))
            return {"recommendation": f"Error: {str(e)}", "agent": "devops", "error": True}
    
    async def setup_monitoring(
        self,
        services: List[str],
    ) -> Dict[str, Any]:
        """Design monitoring setup"""
        if not self.llm:
            return {"monitoring_plan": "AI Service Unavailable", "agent": "devops", "error": True}
        
        prompt = f"""Design monitoring for services: {', '.join(services)}

Provide:
1. Key metrics to track
2. Alerting thresholds
3. Tool recommendations
4. Dashboard layout
5. On-call setup
6. Incident response playbook"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "monitoring_plan": response.content,
                "agent": "devops",
            }
        except Exception as e:
            logger.error("Monitoring setup failed", error=str(e))
            return {"monitoring_plan": f"Error: {str(e)}", "agent": "devops", "error": True}
    
    async def security_audit(
        self,
        infrastructure: str,
    ) -> Dict[str, Any]:
        """Perform security audit recommendations"""
        if not self.llm:
            return {"audit": "AI Service Unavailable", "agent": "devops", "error": True}
        
        prompt = f"""Security audit for: {infrastructure}

Provide:
1. Security checklist
2. Common vulnerabilities
3. Hardening steps
4. Access control recommendations
5. Secrets management
6. Compliance considerations"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "audit": response.content,
                "agent": "devops",
            }
        except Exception as e:
            logger.error("Security audit failed", error=str(e))
            return {"audit": f"Error: {str(e)}", "agent": "devops", "error": True}
    
    async def cost_optimization(
        self,
        current_spend: int,
        services: List[str],
    ) -> Dict[str, Any]:
        """Recommend cost optimizations"""
        if not self.llm:
            return {"optimizations": "AI Service Unavailable", "agent": "devops", "error": True}
        
        prompt = f"""Optimize infrastructure costs:

Current Spend: ${current_spend}/month
Services: {', '.join(services)}

Provide:
1. Cost breakdown analysis
2. Optimization opportunities
3. Reserved vs on-demand
4. Right-sizing recommendations
5. Alternative services
6. Expected savings"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "optimizations": response.content,
                "agent": "devops",
            }
        except Exception as e:
            logger.error("Cost optimization failed", error=str(e))
            return {"optimizations": f"Error: {str(e)}", "agent": "devops", "error": True}
    
    def _get_system_prompt(self) -> str:
        return """You are the DevOps/Infrastructure agent - expert in cloud and deployment.

Your expertise:
- CI/CD pipelines
- Cloud architecture (AWS, GCP, Azure)
- Container orchestration (Docker, K8s)
- Monitoring and observability
- Security hardening
- Cost optimization

Focus on reliability, security, and cost-efficiency.
Prefer simple solutions for startups - avoid over-engineering."""
    
    def _build_context(self, ctx: Dict[str, Any]) -> str:
        return f"""Startup Context:
- Product: {ctx.get('name', 'Unknown')}
- Stage: {ctx.get('stage', 'MVP')}
- Industry: {ctx.get('industry', 'Technology')}"""
    


# Singleton
devops_agent = DevOpsAgent()
