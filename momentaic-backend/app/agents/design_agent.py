"""
Design Lead Agent
AI-powered brand identity and UI/UX designer
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm

logger = structlog.get_logger()


class DesignAgent:
    """
    Design Lead Agent - Expert in Brand Identity and UI/UX
    
    Capabilities:
    - Brand Identity Generation (Palettes, Typography)
    - UI/UX Critiques
    - Design System Creation
    - Accessibility Audits
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-pro", temperature=0.7)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a design request"""
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": "design", "error": True}
        
        try:
            context = self._build_context(startup_context)
            prompt = f"""{context}

User Request: {message}

As Design Lead, provide:
1. Visual direction recommendations
2. UX paradigms to employ
3. Color/Typography suggestions
4. Accessibility considerations"""

            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": "design",
                "tools_used": [],
            }
        except Exception as e:
            logger.error("Design agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "design", "error": True}
    
    async def generate_brand_identity(
        self,
        name: str,
        industry: str,
        vibe: str
    ) -> Dict[str, Any]:
        """Generate a brand identity system"""
        if not self.llm:
            return {"brand_identity": "AI Service Unavailable", "agent": "design", "error": True}
        
        prompt = f"""Generate Brand Identity:
Name: {name}
Industry: {industry}
Vibe: {vibe}

Provide:
1. Color Palette (Primary, Secondary, Accent with Hex codes)
2. Typography Pairings (Headings, Body)
3. Logo Concept Description
4. Visual Motif suggestions"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            return {
                "brand_identity": response.content,
                "agent": "design",
            }
        except Exception as e:
            return {"brand_identity": f"Error: {str(e)}", "agent": "design", "error": True}
        

    def _get_system_prompt(self) -> str:
        return """You are the Design Lead agent - expert in visual strategy and UX.
Your goals: Create stunning, functional, and accessible designs.
Focus on modern aesthetics (Glassmorphism, Bento grids, etc.) but prioritize usability."""
    
    def _build_context(self, ctx: Dict[str, Any]) -> str:
        return f"""Startup Context:
- Product: {ctx.get('name', 'Unknown')}
- Description: {ctx.get('description', '')}"""
    

# Singleton
design_agent = DesignAgent()
