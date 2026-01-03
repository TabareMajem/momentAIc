"""
Swarm Router (The "CEO" Agent)
Orchestrates the three sub-swarms: Siren, Hunter, and Builder.
Part of the Unified Empire architecture.
"""

from typing import Dict, Any, List, Optional, Literal
from enum import Enum
import structlog
import asyncio

from app.agents.base import get_llm, get_agent_config
from app.models.conversation import AgentType

# Import Swarm Leaders/Agents
from app.agents.content_agent import content_agent
from app.agents.sales_agent import sales_agent
from app.agents.lead_scraper_agent import lead_scraper_agent
from app.agents.lead_researcher_agent import lead_researcher_agent
from app.agents.sdr_agent import sdr_agent
# from app.agents.devops_agent import devops_agent # Assuming exists or using TechLead
from app.agents.tech_lead_agent import tech_lead_agent

logger = structlog.get_logger()

class SwarmType(str, Enum):
    SIREN = "siren"   # Growth & Traffic
    HUNTER = "hunter" # Revenue & Sales
    BUILDER = "builder" # Dev & Ops

class SwarmRouter:
    """
    The Master Router that delegates tasks to specialized sub-swarms.
    Acts as the "Central Nervous System" for the Unified Empire.
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-2.5-pro", temperature=0.1) # Low temp for routing logic
        
    async def route_task(self, task_description: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Analyze a high-level task and route it to the appropriate Swarm.
        """
        logger.info("Swarm Router: Analyzing task", task=task_description)
        
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}

        prompt = f"""You are the CEO of an autonomous AI organization.
Decompose this task and assign it to ONE of the three specialized swarms.

TASK: "{task_description}"

SWARMS:
1. THE SIREN (Growth & Traffic)
   - Capabilities: Content creation, social media, viral campaigns, community engagement.
   - Keywords: Post, tweet, blog, video, viral, traffic, soul card, marketing.

2. THE HUNTER (Revenue & Sales)
   - Capabilities: Lead generation, scraping, researching companies, cold outreach, sales.
   - Keywords: Lead, scrap, email, outreach, sell, B2B, close deal, Juku, nursing home.

3. THE BUILDER (Dev & Ops)
   - Capabilities: Coding, debugging, deployment, server management, database, API.
   - Keywords: Code, bug, fix, deploy, feature, endpoint, database, error.

Return JSON format:
{{
    "target_swarm": "siren" | "hunter" | "builder",
    "reasoning": "Why you chose this swarm",
    "sub_tasks": ["List of specific actionable steps for the swarm"]
}}
"""
        try:
            response = await self.llm.ainvoke(prompt)
            # In a real impl, we'd use structured output or a parser.
            # For now, let's assume we get a parseable response or mock the routing logic if needed.
            # Simple heuristic callback if LLM output is raw text:
            
            # Clean up response to ensure valid JSON
            content = response.content.replace("```json", "").replace("```", "").strip()
            import json
            
            try:
                parsed_response = json.loads(content)
                target_swarm_str = parsed_response.get("target_swarm", "").lower()
                
                if target_swarm_str == "hunter":
                    target_swarm = SwarmType.HUNTER
                elif target_swarm_str == "siren":
                    target_swarm = SwarmType.SIREN
                elif target_swarm_str == "builder":
                    target_swarm = SwarmType.BUILDER
                else:
                    # Fallback
                    target_swarm = SwarmType.HUNTER if "sales" in task_description.lower() else SwarmType.SIREN
                    
                context["reasoning"] = parsed_response.get("reasoning")
                context["sub_tasks"] = parsed_response.get("sub_tasks")
                
            except json.JSONDecodeError:
                logger.warning("Swarm Router: Failed to parse JSON, using fallback text analysis")
                content_lower = content.lower()
                target_swarm = None
                if "hunter" in content_lower and "sales" in content_lower:
                    target_swarm = SwarmType.HUNTER
                elif "siren" in content_lower or "marketing" in content_lower or "content" in content_lower:
                    target_swarm = SwarmType.SIREN
                elif "builder" in content_lower or "code" in content_lower or "dev" in content_lower:
                    target_swarm = SwarmType.BUILDER
                
                if not target_swarm:
                     # Default to Hunter if vague for now, or error
                     return {"success": False, "error": "Could not determine target swarm"}
            
            return await self._execute_swarm(target_swarm, task_description, context)

        except Exception as e:
            logger.error("Swarm routing failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def _execute_swarm(self, swarm: SwarmType, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the chosen swarm's logic.
        """
        logger.info(f"Swarm Router: Delegating to {swarm}")
        
        if swarm == SwarmType.SIREN:
            return await self._run_siren_swarm(task, context)
        elif swarm == SwarmType.HUNTER:
            return await self._run_hunter_swarm(task, context)
        elif swarm == SwarmType.BUILDER:
            return await self._run_builder_swarm(task, context)
        else:
            return {"success": False, "error": "Unknown Swarm Type"}

    # --- SWARM INTENTIONS ---

    async def _run_siren_swarm(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate The Siren: Content & Viral Growth
        """
        # Example: "Post a founder story"
        # Uses ContentAgent
        logger.info("Activiting Siren Swarm...")
        
        # Simple mapping for now
        if "post" in task.lower() or "story" in task.lower():
            # Delegate to ContentAgent
            return await content_agent.generate(
                platform=context.get("platform", "twitter"), # Default
                topic=task,
                startup_context=context.get("startup_context", {}),
                content_type="post"
            )
        
        return {"success": True, "message": "Siren Swarm task acknowledged (stub)"}

    async def _run_hunter_swarm(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate The Hunter: Sales & Leads
        """
        logger.info("Activiting Hunter Swarm...")
        
        # 1. Scrape Leads?
        if "find" in task.lower() or "scrape" in task.lower():
            if "juku" in task.lower():
                return await lead_scraper_agent.find_juku_leads(region="Tokyo")
            elif "nursing" in task.lower():
                return await lead_scraper_agent.find_nursing_home_leads(region="Kanto")
            else:
                 return await lead_scraper_agent.scrape_google_maps(
                     business_type=task, location="Japan"
                 )
        
        # 2. Research Leads?
        if "research" in task.lower():
            # specialized research logic
            pass
            
        # 3. Outreach?
        if "email" in task.lower() or "outreach" in task.lower():
            # Delegate to SDRAgent
            pass

        return {"success": True, "message": "Hunter Swarm task acknowledged (stub)"}

    async def _run_builder_swarm(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate The Builder: Dev & Ops
        """
        logger.info("Activiting Builder Swarm...")
        return {"success": True, "message": "Builder Swarm task acknowledged (stub)"}

# Singleton
swarm_router = SwarmRouter()
