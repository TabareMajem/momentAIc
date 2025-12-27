"""
Product PM Agent
AI-powered product manager for startups
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import structlog

from app.agents.base import (
    AgentState,
    get_llm,
    get_agent_config,
    web_search,
)
from app.models.conversation import AgentType

logger = structlog.get_logger()


class ProductPMAgent:
    """
    Product PM Agent - Expert in product management
    
    Capabilities:
    - Feature prioritization (RICE, ICE, MoSCoW)
    - User story writing
    - Requirements documentation
    - Roadmap planning
    - User feedback analysis
    - Competitive analysis
    - PRD generation
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.PRODUCT_PM)
        self.llm = get_llm("gemini-pro", temperature=0.6)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process a product-related question or request
        """
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        try:
            context_section = self._build_context(startup_context)
            
            prompt = f"""{context_section}

User Request: {message}

As the Product PM, provide:
1. Clear, actionable product guidance
2. Framework for thinking about this problem
3. Specific recommendations with rationale
4. Metrics to measure success
5. Trade-offs to consider

Focus on user value and business impact. Tie everything to outcomes."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": AgentType.PRODUCT_PM.value,
                "tools_used": [],
            }
            
        except Exception as e:
            logger.error("Product PM agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}
    
    async def prioritize_features(
        self,
        features: List[Dict[str, Any]],
        method: str = "RICE",
    ) -> Dict[str, Any]:
        """
        Prioritize features using a framework
        """
        if not self.llm:
            return {"prioritization": "AI Service Unavailable", "method": method, "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        
        features_text = "\n".join([
            f"- {f['name']}: {f.get('description', '')}" for f in features
        ])
        
        prompt = f"""Prioritize these features using {method} framework:

Features:
{features_text}

For each feature, provide:
1. {method} scoring breakdown
2. Final priority rank
3. Recommended order of implementation
4. Dependencies between features
5. Quick wins vs strategic investments
6. What to cut if resources are limited"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "prioritization": response.content,
                "method": method,
                "agent": AgentType.PRODUCT_PM.value,
            }
        except Exception as e:
            logger.error("Feature prioritization failed", error=str(e))
            return {"prioritization": f"Error: {str(e)}", "method": method, "agent": AgentType.PRODUCT_PM.value, "error": True}
    
    async def write_user_stories(
        self,
        feature_description: str,
        personas: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate user stories for a feature
        """
        personas = personas or ["User", "Admin", "Power User"]
        
        if not self.llm:
            return {"user_stories": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        prompt = f"""Write user stories for this feature:

Feature: {feature_description}
Personas: {', '.join(personas)}

Generate:
1. Epic-level story
2. 5-8 specific user stories (format: As a [persona], I want [goal], so that [benefit])
3. Acceptance criteria for each story
4. Edge cases to consider
5. Dependencies
6. Story points estimate (S/M/L/XL for each)"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "user_stories": response.content,
                "agent": AgentType.PRODUCT_PM.value,
            }
        except Exception as e:
            logger.error("User story generation failed", error=str(e))
            return {"user_stories": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}
    
    async def generate_prd(
        self,
        feature_name: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a Product Requirements Document
        """
        if not self.llm:
            return {"prd": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        prompt = f"""Generate a PRD for:

Feature: {feature_name}
Context: {context.get('description', '')}
Target Users: {context.get('target_users', 'All users')}
Business Goal: {context.get('business_goal', 'Improve user experience')}

Include these sections:
1. Executive Summary
2. Problem Statement
3. Goals & Success Metrics
4. User Stories
5. Functional Requirements
6. Non-Functional Requirements
7. UX/UI Considerations
8. Technical Considerations
9. Timeline & Milestones
10. Risks & Mitigations
11. Open Questions"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "prd": response.content,
                "agent": AgentType.PRODUCT_PM.value,
            }
        except Exception as e:
            logger.error("PRD generation failed", error=str(e))
            return {"prd": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}
    
    async def analyze_feedback(
        self,
        feedback_items: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze user feedback and extract insights
        """
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        feedback_text = "\n".join([f"- {f}" for f in feedback_items[:20]])  # Limit for token size
        
        prompt = f"""Analyze this user feedback:

Feedback Items:
{feedback_text}

Provide:
1. Key themes (grouped)
2. Sentiment breakdown
3. Feature requests extracted
4. Pain points identified
5. Priority recommendations
6. Quick wins from feedback
7. Responses to consider"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "agent": AgentType.PRODUCT_PM.value,
            }
        except Exception as e:
            logger.error("Feedback analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}
    
    async def create_roadmap(
        self,
        features: List[Dict[str, Any]],
        timeline_months: int = 6,
    ) -> Dict[str, Any]:
        """
        Create a product roadmap
        """
        if not self.llm:
            return {"roadmap": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        features_text = "\n".join([
            f"- {f['name']} (Priority: {f.get('priority', 'Medium')}, Effort: {f.get('effort', 'Unknown')})"
            for f in features
        ])
        
        prompt = f"""Create a {timeline_months}-month product roadmap:

Features:
{features_text}

Provide:
1. Monthly breakdown of features
2. Dependencies and sequencing
3. Milestone markers
4. Team focus areas by quarter
5. Buffer for unexpected work
6. Success metrics for each phase"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "roadmap": response.content,
                "agent": AgentType.PRODUCT_PM.value,
            }
        except Exception as e:
            logger.error("Roadmap creation failed", error=str(e))
            return {"roadmap": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}
    
    async def competitive_analysis(
        self,
        competitors: List[str],
        our_product: str,
    ) -> Dict[str, Any]:
        """
        Perform competitive analysis
        """
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        prompt = f"""Perform competitive analysis:

Our Product: {our_product}
Competitors: {', '.join(competitors)}

Provide:
1. Feature comparison matrix
2. Pricing comparison
3. Positioning differences
4. Their strengths to learn from
5. Their weaknesses to exploit
6. Differentiation opportunities
7. Go-to-market strategy implications"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "agent": AgentType.PRODUCT_PM.value,
            }
        except Exception as e:
            logger.error("Competitive analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}
    
    def _build_context(self, startup_context: Dict[str, Any]) -> str:
        """Build startup context"""
        return f"""Product Context:
- Product: {startup_context.get('name', 'Unknown')}
- Industry: {startup_context.get('industry', 'Technology')}
- Stage: {startup_context.get('stage', 'MVP')}
- Target Users: {startup_context.get('target_customer', 'General')}
- Value Prop: {startup_context.get('description', '')}"""
    


# Singleton instance
product_pm_agent = ProductPMAgent()
