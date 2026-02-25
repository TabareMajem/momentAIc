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
from app.services.ecosystem_service import ecosystem_service

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
        self.llm = get_llm("gemini-1.5-pro", temperature=0.1) # Low temp for routing logic
        
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
                # Explicit keyword routing for unmapped domains
                elif "legal" in content_lower or "contract" in content_lower:
                    target_swarm = SwarmType.BUILDER # Legal is under Builder swarm in _run_builder_swarm
                elif "fundrais" in content_lower or "investor" in content_lower or "pitch" in content_lower:
                    target_swarm = SwarmType.HUNTER # We'll route Fundraising to Hunter for now as it's "Sales" of equity
                
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
        
        Optimized to use Ecosystem Agents (Viral/Media) first, then fall back to internal chains.
        """
        logger.info("Activating Siren Swarm...")
        
        task_lower = task.lower()
        startup_context = context.get("startup_context", {})
        
        # 1. Check for Ecosystem Capabilities
        if "viral" in task_lower or "tiktok" in task_lower or "script" in task_lower:
            # Use Ecosystem Viral Agent
            logger.info("Delegating to Ecosystem: Viral Agent")
            topic = context.get("topic") or task
            result = await ecosystem_service.generate_viral_content(topic, platform="tiktok")
            return {
                "success": result.get("success", False),
                "swarm": "siren",
                "agent": "viral_agent",
                "result": result
            }
            
        if "image" in task_lower or "video" in task_lower or "media" in task_lower:
            # Use Ecosystem Media Agent
            logger.info("Delegating to Ecosystem: Media Agent")
            prompt = context.get("prompt") or task
            media_type = "video" if "video" in task_lower else "image"
            result = await ecosystem_service.generate_media(prompt, type=media_type)
            return {
                "success": result.get("success", False),
                "swarm": "siren",
                "agent": "media_agent",
                "result": result
            }
            
        if "voice" in task_lower or "audio" in task_lower or "tts" in task_lower:
            # Use AgentForge Voice Agent
            logger.info("Delegating to AgentForge: Voice Agent")
            text = context.get("text") or task
            action = "tts"
            result = await ecosystem_service.synthesize_voice(text, action=action)
            return {
                "success": result.get("success", False),
                "swarm": "siren",
                "agent": "voice_agent",
                "result": result
            }
            
        # 2. Fallback to Internal Chain Execution
        logger.info("Executing Internal Siren Chain...")
        from app.agents.chain_executor import chain_executor
        startup_context = context.get("startup_context", {})
        
        # Determine the appropriate chain based on task type
        if "viral" in task_lower or "campaign" in task_lower:
            # Full viral campaign: content → growth → community → ambassadors
            chain = ["content", "judgement", "growth_hacker", "community", "ambassador_outreach"]
        elif "post" in task_lower or "story" in task_lower or "content" in task_lower:
            # Content creation with optimization
            chain = ["content", "judgement", "growth_hacker"]
        elif "community" in task_lower or "engage" in task_lower:
            # Community focused
            chain = ["community", "content", "ambassador_outreach"]
        elif "ambassador" in task_lower or "influencer" in task_lower:
            # Ambassador outreach
            chain = ["lead_researcher", "ambassador_outreach", "sdr"]
        else:
            # Default: content + optimization
            chain = ["content", "judgement"]
        
        # Execute the chain
        result = await chain_executor.execute_chain(
            agent_chain=chain,
            initial_context={
                **startup_context,
                "task_name": task,
                "task_description": task,
                "user_id": context.get("user_id", "system"),
                "platform": context.get("platform", "linkedin"),
                "content_type": context.get("content_type", "post")
            }
        )
        
        return {
            "success": result.get("status") in ["completed", "partial"],
            "swarm": "siren",
            "chain_executed": chain,
            "result": result
        }

    async def _run_hunter_swarm(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate The Hunter: Sales & Leads
        
        Optimized to use Ecosystem Agents (Sniper/Moby/Lemlist) first, then internal chains.
        """
        logger.info("Activating Hunter Swarm...")
        
        task_lower = task.lower()
        startup_context = context.get("startup_context", {})
        
        # 1. Check for Ecosystem Capabilities
        if "lead" in task_lower and ("find" in task_lower or "scrape" in task_lower):
            # Use Ecosystem Sniper Agent
            logger.info("Delegating to Ecosystem: Sniper Agent")
            criteria = context.get("criteria") or {"query": task}
            result = await ecosystem_service.find_leads(criteria)
            return {
                "success": result.get("success", False),
                "swarm": "hunter",
                "agent": "sniper_agent",
                "result": result
            }
            
        if "whale" in task_lower or "high-ticket" in task_lower or "moby" in task_lower:
            # Use Ecosystem Moby Agent
            logger.info("Delegating to Ecosystem: Moby Agent")
            client = context.get("client_example") or "generic"
            result = await ecosystem_service.find_whale_clients(client)
            return {
                "success": result.get("success", False),
                "swarm": "hunter",
                "agent": "moby_agent",
                "result": result
            }
            
        if "campaign" in task_lower and "email" in task_lower:
            # Use Ecosystem Lemlist Agent
            logger.info("Delegating to Ecosystem: Lemlist Agent")
            leads = context.get("leads", [])
            template = context.get("template_id", "default")
            result = await ecosystem_service.launch_email_campaign(leads, template)
            return {
                "success": result.get("success", False),
                "swarm": "hunter",
                "agent": "lemlist_agent",
                "result": result
            }
            
        if "deep research" in task_lower or ("analyze" in task_lower and "market" in task_lower):
            # Use AgentForge Research Agent
            logger.info("Delegating to AgentForge: Research Agent")
            prompt = task
            result = await ecosystem_service.deep_research(prompt)
            return {
                "success": result.get("success", False),
                "swarm": "hunter",
                "agent": "research_agent",
                "result": result
            }
            
        # 2. Fallback to Internal Chain Execution
        logger.info("Executing Internal Hunter Chain...")
        from app.agents.chain_executor import chain_executor
        
        # Determine the appropriate chain based on task type
        if "find" in task_lower or "scrape" in task_lower or "lead" in task_lower:
            # Full lead generation pipeline
            if "juku" in task_lower or "nursing" in task_lower:
                # Japan-specific B2B targets
                chain = ["lead_scraper", "lead_researcher", "sdr"]
            else:
                chain = ["lead_scraper", "lead_researcher", "sdr", "sales"]
        elif "research" in task_lower:
            # Research focused
            chain = ["lead_researcher", "competitor_intel", "data_analyst"]
        elif "email" in task_lower or "outreach" in task_lower:
            # Outreach focused
            chain = ["lead_researcher", "sdr", "sales"]
        elif "close" in task_lower or "deal" in task_lower:
            # Closing focused
            chain = ["sales", "customer_success"]
        elif "competitor" in task_lower:
            # Competitor analysis
            chain = ["competitor_intel", "data_analyst", "strategy"]
        else:
            # Default: full pipeline
            chain = ["lead_scraper", "lead_researcher", "sdr", "sales"]
        
        # Execute the chain
        result = await chain_executor.execute_chain(
            agent_chain=chain,
            initial_context={
                **startup_context,
                "task_name": task,
                "task_description": task,
                "user_id": context.get("user_id", "system"),
                "target_region": context.get("region", "Global"),
                "business_type": context.get("business_type", "")
            }
        )
        
        return {
            "success": result.get("status") in ["completed", "partial"],
            "swarm": "hunter",
            "chain_executed": chain,
            "result": result
        }

    async def _run_builder_swarm(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate The Builder: Dev & Ops
        
        Optimized to use Ecosystem Agents (Recruiting/Legal/Support) first, then internal chains.
        """
        logger.info("Activating Builder Swarm...")
        
        task_lower = task.lower()
        startup_context = context.get("startup_context", {})
        
        # 1. Check for Ecosystem Capabilities
        if "hire" in task_lower or "recruit" in task_lower or "resume" in task_lower:
            # Use Ecosystem Recruiting Agent
            logger.info("Delegating to Ecosystem: Recruiting Agent")
            resume = context.get("resume_text", "")
            job = context.get("job_description", "")
            result = await ecosystem_service.screen_resume(resume, job)
            return {
                "success": result.get("success", False),
                "swarm": "builder",
                "agent": "recruiting_agent",
                "result": result
            }
            
        if "legal" in task_lower or "contract" in task_lower or "term" in task_lower:
            # Use Ecosystem Legal Agent
            logger.info("Delegating to Ecosystem: Legal Agent")
            terms = context.get("terms") or {"scope": task}
            result = await ecosystem_service.draft_contract(terms)
            return {
                "success": result.get("success", False),
                "swarm": "builder",
                "agent": "legal_agent",
                "result": result
            }
            
        if "support" in task_lower or "ticket" in task_lower or "refund" in task_lower:
            # Use Ecosystem Support Agent
            logger.info("Delegating to Ecosystem: Support Agent")
            ticket = context.get("ticket") or {"message": task}
            result = await ecosystem_service.handle_support_ticket(ticket)
            return {
                "success": result.get("success", False),
                "swarm": "builder",
                "agent": "support_agent",
                "result": result
            }
            
        if "code" in task_lower or "git" in task_lower or "docker" in task_lower:
            # Use AgentForge Developer Agent
            logger.info("Delegating to AgentForge: Developer Agent")
            tool_name = context.get("tool", "coding")
            args = context.get("args") or {"task": task}
            result = await ecosystem_service.execute_dev_task(tool_name, args)
            return {
                "success": result.get("success", False),
                "swarm": "builder",
                "agent": "developer_agent",
                "result": result
            }
            
        # 2. Fallback to Internal Chain Execution
        logger.info("Executing Internal Builder Chain...")
        from app.agents.chain_executor import chain_executor
        
        # Determine the appropriate chain based on task type
        if "launch" in task_lower or "submit" in task_lower or "product hunt" in task_lower:
            # Launch focused
            chain = ["launch_strategist", "launch_executor"]
        elif "test" in task_lower or "qa" in task_lower or "bug" in task_lower:
            # QA focused
            chain = ["qa_tester", "tech_lead"]
        elif "deploy" in task_lower or "server" in task_lower:
            # DevOps focused
            chain = ["devops", "tech_lead"]
        elif "feature" in task_lower or "code" in task_lower or "build" in task_lower:
            # Development focused
            chain = ["product_pm", "tech_lead", "qa_tester"]
        elif "design" in task_lower or "ui" in task_lower or "ux" in task_lower:
            # Design focused
            chain = ["design", "product_pm", "tech_lead"]
        else:
            # Default: production readiness
            chain = ["tech_lead", "qa_tester", "devops"]
        
        # Execute the chain
        result = await chain_executor.execute_chain(
            agent_chain=chain,
            initial_context={
                **startup_context,
                "task_name": task,
                "task_description": task,
                "user_id": context.get("user_id", "system")
            }
        )
        
        return {
            "success": result.get("status") in ["completed", "partial"],
            "swarm": "builder",
            "chain_executed": chain,
            "result": result
        }

# Singleton
swarm_router = SwarmRouter()
