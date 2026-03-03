"""
War Gaming Agent (Launch Simulator)
Simulates brutal feedback from different user personas to stress-test the startup.
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog
import asyncio

from app.agents.base import get_llm

logger = structlog.get_logger()

class WarGamingAgent:
    """
    War Gaming Agent - The brutal launch simulator.
    """
    
    @property
    def llm(self):
        # Use simple flash model for efficiency in parallel persona calls
        return get_llm("gemini-flash", temperature=0.7)
        
    @property
    def synth_llm(self):
         # Use smarter model for final report synthesis
        return get_llm("gemini-flash", temperature=0.4)

    async def simulate_launch(
        self,
        startup_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a launch simulation with multiple personas.
        """
        logger.info("WarGaming: Starting launch simulation")
        
        context_str = self._format_context(startup_context)
        
        # 1. Define Personas
        personas = [
            {
                "role": "The Cynical Skeptic", 
                "prompt": "You are a cynical Hacker News commenter. You hate marketing fluff. You believe most startups are wrappers. Tear this idea apart. Find the technical flaws and 'why this will fail'."
            },
            {
                "role": "The Enterprise CIO",
                "prompt": "You are a risk-averse CIO of a Fortune 500 company. You care about security, compliance, SLA, and vendor lock-in. Why would you NEVER buy this? What are the integration risks?"
            },
            {
                "role": "The Tired VC",
                "prompt": "You are a VC who has seen 50 pitches today. You are bored. You care about moat, TAM, and exit strategy. Why is this not a unicorn? Why is the market too small?"
            },
            {
                "role": "The Confused User",
                "prompt": "You are a non-technical user (Grandma test). You don't understand jargon. Read the description and tell me what is confusing. Do you even understand what it does?"
            }
        ]
        
        # 2. Run Simulations in Parallel
        critiques = []
        tasks = []
        
        for p in personas:
            tasks.append(self._get_critique(p, context_str))
            
        results = await asyncio.gather(*tasks)
        
        for i, res in enumerate(results):
            critiques.append(f"### Persona: {personas[i]['role']}\n\n{res}")

        # 3. Synthesize War Room Report
        logger.info("WarGaming: Synthesizing report")
        
        full_critiques = "\n\n".join(critiques)
        
        report_prompt = f"""
        You are the War Gaming Moderator. We just ran a brutal simulation of a startup launch.
        
        Startup:
        {context_str}
        
        Critiques from the Field:
        {full_critiques}
        
        Task:
        1. Synthesize a "Launch Survival Report".
        2. Assign a "Survival Score" (0-100) based on how fatal the flaws are.
        3. Identify the "Critical Kill Shot" - the one issue that is most likely to kill the company.
        4. List 3 immediate "Defense Maneuvers" to fix the biggest gaps.
        
        Format: Markdown
        """
        
        report_response = await self.synth_llm.ainvoke([HumanMessage(content=report_prompt)])
        
        return {
            "report": report_response.content,
            "raw_critiques": critiques,
            "agent": "war_gaming"
        }

    async def _get_critique(self, persona: Dict[str, str], context: str) -> str:
        """Helper to get critique from a specific persona"""
        try:
            prompt = f"""
            {persona['prompt']}
            
            Analyze this startup brutal and honest:
            {context}
            
            Keep your response under 200 words. Be direct.
            """
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            logger.error(f"Persona {persona['role']} failed", error=str(e))
            return "Persona unavailable."

    def _format_context(self, context: Dict[str, Any]) -> str:
        return f"""
        Name: {context.get('name', 'Stealth Startup')}
        Description: {context.get('description', '')}
        Industry: {context.get('industry', 'Tech')}
        Problem: {context.get('pain_point', 'Unknown')}
        Solution: {context.get('value_prop', 'Unknown')}
        Price: {context.get('price_point', 'Unknown')}
        """

# Singleton

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for competitive threats and strategic vulnerabilities.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} competitive threats and strategic vulnerabilities 2025")
        
        if results:
            from app.agents.base import get_llm
            llm = get_llm("gemini-pro", temperature=0.3)
            if llm:
                from langchain_core.messages import HumanMessage
                prompt = f"""Analyze these results for a {industry} startup:
{str(results)[:2000]}

Identify the top 3 actionable insights. Be concise."""
                try:
                    response = await llm.ainvoke([HumanMessage(content=prompt)])
                    from app.agents.base import BaseAgent
                    if hasattr(self, 'publish_to_bus'):
                        await self.publish_to_bus(
                            topic="intelligence_gathered",
                            data={
                                "source": "WarGamingAgent",
                                "analysis": response.content[:1500],
                                "agent": "war_gaming_agent",
                            }
                        )
                    actions.append({"name": "threat_detected", "industry": industry})
                except Exception as e:
                    logger.error(f"WarGamingAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Runs competitive simulations and generates strategic defense/attack playbooks.
        """
        action_type = action.get("action", action.get("name", "unknown"))

        try:
            from app.agents.base import get_llm, web_search
            from langchain_core.messages import HumanMessage
            
            industry = startup_context.get("industry", "Technology")
            llm = get_llm("gemini-pro", temperature=0.5)
            
            if not llm:
                return "LLM not available"
            
            search_results = await web_search(f"{industry} {action_type} best practices 2025")
            
            prompt = f"""You are the Competitive war games and stress testing agent for a {industry} startup.

Based on this context:
- Action requested: {action_type}
- Industry: {industry}
- Research: {str(search_results)[:1500]}

Generate a concrete, actionable deliverable. No fluff. Be specific and executable."""
            
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            if hasattr(self, 'publish_to_bus'):
                await self.publish_to_bus(
                    topic="deliverable_generated",
                    data={
                        "type": action_type,
                        "content": response.content[:2000],
                        "agent": "war_gaming_agent",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("WarGamingAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

war_gaming_agent = WarGamingAgent()
