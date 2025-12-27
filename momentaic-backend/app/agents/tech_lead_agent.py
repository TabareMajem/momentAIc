"""
Tech Lead Agent
LangGraph-based technical advisor and code architect
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
)
from app.models.conversation import AgentType

logger = structlog.get_logger()


class TechLeadAgent:
    """
    Tech Lead Agent - Expert in software architecture and development
    
    Capabilities:
    - Tech stack recommendations
    - Architecture review and design
    - Code review and best practices
    - Development effort estimation
    - Technical debt assessment
    - Scalability analysis
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.TECH_LEAD)
        self.llm = get_llm("gemini-pro", temperature=0.5)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process a technical question or request
        """
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": AgentType.TECH_LEAD.value, "error": True}
        
        try:
            # Build context-aware prompt
            context_section = self._build_context(startup_context)
            
            prompt = f"""{context_section}

User Request: {message}

As the Tech Lead, provide:
1. Direct answer to the question
2. Technical recommendations
3. Trade-offs to consider
4. Implementation steps if applicable
5. Estimated effort (if relevant)

Be practical and consider the startup's stage and resources."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": AgentType.TECH_LEAD.value,
                "tools_used": [],
            }
            
        except Exception as e:
            logger.error("Tech Lead agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": AgentType.TECH_LEAD.value, "error": True}
    
    async def review_architecture(
        self,
        architecture_description: str,
        startup_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Review a proposed architecture
        """
        if not self.llm:
            return {"review": "AI Service Unavailable", "agent": AgentType.TECH_LEAD.value, "error": True}
        
        prompt = f"""Review this architecture for a startup:

{architecture_description}

Startup Context:
- Industry: {startup_context.get('industry', 'Unknown')}
- Stage: {startup_context.get('stage', 'MVP')}

Provide:
1. Strengths of this architecture
2. Potential issues or bottlenecks
3. Scalability assessment (1-10)
4. Security considerations
5. Recommended improvements
6. Alternative approaches to consider"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "review": response.content,
                "agent": AgentType.TECH_LEAD.value,
            }
        except Exception as e:
            logger.error("Architecture review failed", error=str(e))
            return {"review": f"Error: {str(e)}", "agent": AgentType.TECH_LEAD.value, "error": True}
    
    async def estimate_effort(
        self,
        feature_description: str,
        tech_stack: List[str],
        team_size: int = 1,
    ) -> Dict[str, Any]:
        """
        Estimate development effort for a feature
        """
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "estimates": {}, "agent": AgentType.TECH_LEAD.value, "error": True}
        
        prompt = f"""Estimate development effort:

Feature: {feature_description}
Tech Stack: {', '.join(tech_stack)}
Team Size: {team_size} developer(s)

Provide:
1. Time estimate (optimistic, realistic, pessimistic)
2. Complexity rating (1-10)
3. Key development tasks breakdown
4. Technical risks
5. Dependencies to consider
6. MVP vs Full implementation timeline"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            # Parse estimates from response
            estimates = self._parse_estimates(response.content)
            
            return {
                "analysis": response.content,
                "estimates": estimates,
                "agent": AgentType.TECH_LEAD.value,
            }
        except Exception as e:
            logger.error("Effort estimation failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "estimates": {}, "agent": AgentType.TECH_LEAD.value, "error": True}
    
    async def suggest_tech_stack(
        self,
        project_type: str,
        requirements: List[str],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Recommend a tech stack for a project
        """
        constraints = constraints or {}
        
        if not self.llm:
            return {"recommendation": "AI Service Unavailable", "agent": AgentType.TECH_LEAD.value, "error": True}
        
        prompt = f"""Recommend a tech stack for:

Project Type: {project_type}
Requirements: {', '.join(requirements)}
Constraints: {constraints}

Provide:
1. Recommended stack (frontend, backend, database, infrastructure)
2. Why this stack (pros)
3. Trade-offs (cons)
4. Alternative options
5. Learning curve assessment
6. Cost considerations"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "recommendation": response.content,
                "agent": AgentType.TECH_LEAD.value,
            }
        except Exception as e:
            logger.error("Tech stack suggestion failed", error=str(e))
            return {"recommendation": f"Error: {str(e)}", "agent": AgentType.TECH_LEAD.value, "error": True}
    
    def _build_context(self, startup_context: Dict[str, Any]) -> str:
        """Build startup context section"""
        if not startup_context:
            return ""
        
        return f"""Startup Context:
- Name: {startup_context.get('name', 'Unknown')}
- Industry: {startup_context.get('industry', 'Technology')}
- Stage: {startup_context.get('stage', 'MVP')}
- Description: {startup_context.get('description', '')}"""
    
    def _parse_estimates(self, response: str) -> Dict[str, Any]:
        """Extract time estimates from response"""
        estimates = {
            "optimistic": None,
            "realistic": None,
            "pessimistic": None,
            "complexity": None,
        }
        
        # Simple pattern matching for time estimates
        time_pattern = r'(\d+(?:\.\d+)?)\s*(days?|weeks?|months?|hours?)'
        matches = re.findall(time_pattern, response.lower())
        
        if len(matches) >= 3:
            estimates["optimistic"] = f"{matches[0][0]} {matches[0][1]}"
            estimates["realistic"] = f"{matches[1][0]} {matches[1][1]}"
            estimates["pessimistic"] = f"{matches[2][0]} {matches[2][1]}"
        
        # Extract complexity rating
        complexity_pattern = r'complexity[:\s]*(\d+)'
        complexity_match = re.search(complexity_pattern, response.lower())
        if complexity_match:
            estimates["complexity"] = int(complexity_match.group(1))
        
        return estimates
    


# Singleton instance
tech_lead_agent = TechLeadAgent()
