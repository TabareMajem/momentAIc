"""
Product PM Agent
AI-powered product manager for startups
"""

from typing import Dict, Any, List, Optional
import structlog
from pydantic import BaseModel, Field

from app.agents.base import (
    get_llm,
    get_agent_config,
    BaseAgent,
)
from app.models.conversation import AgentType
from app.services.agent_memory_service import agent_memory_service

logger = structlog.get_logger()

# ==========================================
# Pydantic Structured Outputs
# ==========================================

class ProductPMProcess(BaseModel):
    response: str = Field(description="Clear, actionable product guidance")
    framework: str = Field(description="Framework applied to this problem")
    metrics: List[str] = Field(description="Metrics to measure success")
    recommendations: List[str] = Field(description="Specific actionable recommendations")

class PrioritizationResult(BaseModel):
    prioritization: str = Field(description="Detailed scoring breakdown and rationale")
    recommended_order: List[str] = Field(description="List of feature names in order of implementation")
    strategic_investments: List[str] = Field(description="Strategic investments vs quick wins")

class UserStoriesResult(BaseModel):
    epic: str = Field(description="The overarching Epic-level story")
    user_stories: List[str] = Field(description="Specific user stories with acceptance criteria")
    edge_cases: List[str] = Field(description="Edge cases to consider")

class PRDResult(BaseModel):
    prd: str = Field(description="The complete, comprehensive PRD content")

class FeedbackAnalysisResult(BaseModel):
    themes: List[str] = Field(description="Key themes extracted from feedback")
    analysis: str = Field(description="Detailed synthesis of feedback sentiment and requests")
    quick_wins: List[str] = Field(description="Quick wins identified from feedback")

class RoadmapResult(BaseModel):
    roadmap: str = Field(description="The complete product roadmap breakdown")
    milestones: List[str] = Field(description="Key milestones to track")

class CompetitiveResult(BaseModel):
    analysis: str = Field(description="Detailed competitive analysis and comparison matrix")
    opportunities: List[str] = Field(description="Specific differentiation opportunities to exploit")

# ==========================================
# Agent Class
# ==========================================

class ProductPMAgent(BaseAgent):
    """
    Product PM Agent - Expert in product management
    Now upgraded to BaseAgent with cognitive depth and memory recall.
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.PRODUCT_PM)
        self.llm = get_llm("gemini-2.0-flash", temperature=0.6)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a product-related question or request"""
        if not self.llm:
             return {"response": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
             
        try:
            # Inject Cognitive Memory
            memory_context = await agent_memory_service.recall_as_context(user_id)
            context_section = self._build_context(startup_context)
            
            prompt = f"""{context_section}
{memory_context}

User Request: {message}

As the Product PM, provide clear guidance, frameworks, specific recommendations, and precise metrics.
Focus on user value and business impact. Tie everything to outcomes."""
            
            structured_data = await self.structured_llm_call(
                prompt=f"{self.config['system_prompt']}\n\n{prompt}",
                response_model=ProductPMProcess
            )
            
            # Formatting Response
            if isinstance(structured_data, dict):
                response_text = structured_data.get("response", str(structured_data))
            else:
                response_text = f"{structured_data.response}\n\n**Framework:** {structured_data.framework}\n\n**Metrics:**\n" + "\n".join(f"- {m}" for m in structured_data.metrics) + "\n\n**Recommendations:**\n" + "\n".join(f"- {r}" for r in structured_data.recommendations)

            # Store memory for continuous learning
            await agent_memory_service.remember(
                user_id=user_id,
                agent_type=AgentType.PRODUCT_PM.value,
                memory_type="preference",
                content=f"User asked PM about: {message[:100]}"
            )

            return {
                "response": response_text,
                "agent": AgentType.PRODUCT_PM.value,
                "tools_used": [],
            }
        except Exception as e:
            logger.error("Product PM agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}
    
    async def prioritize_features(self, features: List[Dict[str, Any]], method: str = "RICE") -> Dict[str, Any]:
        if not self.llm: return {"prioritization": "AI Service Unavailable", "method": method, "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        features_text = "\n".join([f"- {f['name']}: {f.get('description', '')}" for f in features])
        prompt = f"Prioritize these features using {method} framework:\nFeatures:\n{features_text}\nProvide detailed breakdown, recommended order, and strategic investments."
        try:
            result = await self.structured_llm_call(prompt=f"{self.config['system_prompt']}\n\n{prompt}", response_model=PrioritizationResult)
            val = result.prioritization if hasattr(result, "prioritization") else str(result)
            return {"prioritization": val, "method": method, "agent": AgentType.PRODUCT_PM.value}
        except Exception as e:
            return {"prioritization": f"Error: {str(e)}", "method": method, "agent": AgentType.PRODUCT_PM.value, "error": True}

    async def write_user_stories(self, feature_description: str, personas: List[str] = None) -> Dict[str, Any]:
        if not self.llm: return {"user_stories": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        personas = personas or ["User", "Admin", "Power User"]
        prompt = f"Write user stories for this feature:\nFeature: {feature_description}\nPersonas: {', '.join(personas)}\nGenerate an epic, specific stories with acceptance criteria, and edge cases."
        try:
            result = await self.structured_llm_call(prompt=f"{self.config['system_prompt']}\n\n{prompt}", response_model=UserStoriesResult)
            if hasattr(result, "user_stories"):
                val = f"**EPIC**: {result.epic}\n\n" + "\n\n".join(result.user_stories) + "\n\n**Edge Cases:**\n" + "\n".join(f"- {ec}" for ec in result.edge_cases)
            else:
                val = str(result)
            return {"user_stories": val, "agent": AgentType.PRODUCT_PM.value}
        except Exception as e:
            return {"user_stories": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}

    async def generate_prd(self, feature_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.llm: return {"prd": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        prompt = f"Generate a comprehensive PRD for:\nFeature: {feature_name}\nContext: {context.get('description', '')}\nTarget Users: {context.get('target_users', 'All users')}\nBusiness Goal: {context.get('business_goal', 'Improve user experience')}"
        try:
            result = await self.structured_llm_call(prompt=f"{self.config['system_prompt']}\n\n{prompt}", response_model=PRDResult)
            val = result.prd if hasattr(result, "prd") else str(result)
            return {"prd": val, "agent": AgentType.PRODUCT_PM.value}
        except Exception as e:
            return {"prd": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}

    async def analyze_feedback(self, feedback_items: List[str]) -> Dict[str, Any]:
        if not self.llm: return {"analysis": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        feedback_text = "\n".join([f"- {f}" for f in feedback_items[:20]])
        prompt = f"Analyze this user feedback:\n{feedback_text}\nExtract themes, synthesize analysis, and identify quick wins."
        try:
            result = await self.structured_llm_call(prompt=f"{self.config['system_prompt']}\n\n{prompt}", response_model=FeedbackAnalysisResult)
            if hasattr(result, "analysis"):
                val = result.analysis + "\n\n**Themes:**\n" + "\n".join(f"- {t}" for t in result.themes) + "\n\n**Quick Wins:**\n" + "\n".join(f"- {w}" for w in result.quick_wins)
            else:
                val = str(result)
            return {"analysis": val, "agent": AgentType.PRODUCT_PM.value}
        except Exception as e:
            return {"analysis": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}

    async def create_roadmap(self, features: List[Dict[str, Any]], timeline_months: int = 6) -> Dict[str, Any]:
        if not self.llm: return {"roadmap": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        features_text = "\n".join([f"- {f['name']}" for f in features])
        prompt = f"Create a {timeline_months}-month product roadmap:\nFeatures: {features_text}\nProvide the detailed roadmap and key milestones."
        try:
            result = await self.structured_llm_call(prompt=f"{self.config['system_prompt']}\n\n{prompt}", response_model=RoadmapResult)
            if hasattr(result, "roadmap"):
                val = result.roadmap + "\n\n**Milestones:**\n" + "\n".join(f"- {m}" for m in result.milestones)
            else:
                val = str(result)
            return {"roadmap": val, "agent": AgentType.PRODUCT_PM.value}
        except Exception as e:
            return {"roadmap": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}

    async def competitive_analysis(self, competitors: List[str], our_product: str) -> Dict[str, Any]:
        if not self.llm: return {"analysis": "AI Service Unavailable", "agent": AgentType.PRODUCT_PM.value, "error": True}
        
        prompt = f"Perform competitive analysis:\nOur Product: {our_product}\nCompetitors: {', '.join(competitors)}\nProvide a detailed comparison and find unique opportunities."
        try:
            result = await self.structured_llm_call(prompt=f"{self.config['system_prompt']}\n\n{prompt}", response_model=CompetitiveResult)
            if hasattr(result, "analysis"):
                val = result.analysis + "\n\n**Opportunities:**\n" + "\n".join(f"- {o}" for o in result.opportunities)
            else:
                val = str(result)
            return {"analysis": val, "agent": AgentType.PRODUCT_PM.value}
        except Exception as e:
            return {"analysis": f"Error: {str(e)}", "agent": AgentType.PRODUCT_PM.value, "error": True}

    def _build_context(self, startup_context: Dict[str, Any]) -> str:
        return f"""Product Context:
- Product: {startup_context.get('name', 'Unknown')}
- Industry: {startup_context.get('industry', 'Technology')}
- Stage: {startup_context.get('stage', 'MVP')}
- Target Users: {startup_context.get('target_customer', 'General')}
- Value Prop: {startup_context.get('description', '')}"""

# Legacy singleton export
product_pm_agent = ProductPMAgent()
