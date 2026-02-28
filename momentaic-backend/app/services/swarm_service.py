import asyncio
import structlog
from typing import Dict, Any, List
from uuid import UUID

from app.core.database import AsyncSessionLocal
from sqlalchemy.future import select
from sqlalchemy import update
from app.models.startup import Startup
from app.models.user import User, CreditTransaction
from app.models.growth import Lead, LeadSource, LeadStatus
from app.agents.data_harvester_agent import data_harvester
from app.agents.sdr_agent import SDRAgent
from app.agents.browser_agent import browser_agent
from app.services.lead_magnet_generator import lead_magnet_generator
from app.agents.creator_agent import creator_agent

logger = structlog.get_logger()

class SwarmService:
    """
    Phase 11: Multi-Tenant Swarm Execution
    
    This service abstracts the standalone Swarm scripts into a dynamic, 
    multi-tenant backend service. It fetches context from the Momentaic 
    Postgres `Startup` model to autonomously run customized campaigns 
    for ANY user on the platform.
    """
    
    def __init__(self):
        self.sdr = SDRAgent()

    async def _fetch_startup_context(self, startup_id: UUID) -> Dict[str, Any]:
        """Fetches the Startup's specific context from Postgres to customize the Swarm."""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Startup).filter(Startup.id == startup_id))
                startup = result.scalars().first()
                if not startup:
                    logger.error("swarm_service_startup_not_found", startup_id=str(startup_id))
                    return None
                    
                return {
                    "id": str(startup.id),
                    "name": startup.name,
                    "industry": startup.industry,
                    "description": startup.description or "",
                    "description": startup.description or "",
                    "github_repo": startup.github_repo,
                    "settings": startup.settings or {},
                    "owner_id": str(startup.owner_id)
                }
        except Exception as e:
             logger.error("swarm_service_db_fetch_error", error=str(e))
             return None

    async def _persist_lead_to_crm(self, startup_id: str, prospect: Dict[str, str], status: LeadStatus, magnet_path: str = None):
        """Saves the harvested Swarm targets into the Momentaic CRM."""
        try:
            async with AsyncSessionLocal() as db:
                new_lead = Lead(
                    startup_id=UUID(startup_id),
                    company_name=f"Swarm Target ({prospect['inferred_stack']})",
                    contact_name=prospect['handle'],
                    contact_linkedin=prospect.get('profile_url'),
                    status=status,
                    source=LeadSource.AGENT_PROSPECTING,
                    notes=f"Generated via Phase 11 Multi-Tenant Swarm. Platform: {prospect['platform']}. Delivered Blueprint: {magnet_path}"
                )
                db.add(new_lead)
                await db.commit()
                logger.info("swarm_service_lead_persisted", startup_id=startup_id, handle=prospect['handle'])
        except Exception as e:
            logger.error("swarm_service_lead_persist_error", error=str(e))


    async def _deduct_credits(self, user_id: str, amount: int, reason: str) -> bool:
        """Deducts API credits from the user's balance and records an audit log."""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(User).filter(User.id == UUID(user_id)))
                user = result.scalars().first()
                if not user or user.credits_balance < amount:
                    logger.warning("swarm_service_insufficient_credits", user_id=user_id, balance=user.credits_balance if user else 0, required=amount)
                    return False
                    
                # Deduct exactly
                user.credits_balance -= amount
                
                # Write to the audit ledger
                transaction = CreditTransaction(
                    user_id=UUID(user_id),
                    amount=-amount,
                    balance_after=user.credits_balance,
                    transaction_type="deduction",
                    reason=reason,
                    transaction_meta={"service": "piapi_kling_3_0"}
                )
                db.add(transaction)
                await db.commit()
                
                logger.info("swarm_service_credits_deducted", user_id=user_id, amount=amount, new_balance=user.credits_balance)
                return True
        except Exception as e:
            logger.error("swarm_service_credit_deduction_error", error=str(e))
            return False

    async def worker_proof_of_work_generator(self, startup_context: Dict[str, Any], prospect: Dict[str, str]) -> Dict[str, Any]:
        """
        Generates the customized JSON API blueprint and demo video tailored specifically 
        to the Tenant's (Startup's) product rather than Symbiotask.
        """
        logger.info("swarm_worker_starting_proof_of_work", target=prospect['handle'], tenant=startup_context['name'])
        
        # 1. Blueprint Generation with Multi-Tenant Context Injection
        magnet_result = await lead_magnet_generator.generate_n8n_blueprint(
            prospect_context=f"Handle: {prospect['handle']}, Tech Stack: {prospect['inferred_stack']}",
            specific_request=f"Provide an API node integration template syncing their stack with {startup_context['name']}. Context: {startup_context['description']}"
        )
        
        if not magnet_result.get("success"):
            return {"success": False, "error": magnet_result.get("error")}
            
        # 2. Video Rendering (Creator Agent with Kling 3.0 Integration)
        # Verify and Deduct Credits before dispatching to PiAPI
        # We charge 5 credits per UGC Avatar compilation
        video_cost = 5
        has_credits = await self._deduct_credits(user_id=startup_context['owner_id'], amount=video_cost, reason=f"UGC Avatar render for {prospect['handle']}")
        
        if not has_credits:
            logger.error("creator_agent_kling_blocked_no_credits", target=prospect['handle'], owner=startup_context['owner_id'])
            return {
                "success": True, 
                "blueprint_path": magnet_result["filepath"], 
                "video_path": None, # Fails gracefully, DM will still send just the blueprint
                "message": "Insufficient credits for video generation."
            }
            
        logger.info("creator_agent_rendering_custom_demo", target=prospect['handle'])
        render_result = await creator_agent.render_demo_video(prospect['handle'], magnet_result["filepath"], startup_context)
        
        return {
            "success": True,
            "blueprint_path": magnet_result["filepath"],
            "video_path": render_result.get("video_path")
        }
        
    async def worker_omnichannel_dispatch(self, startup_context: Dict[str, Any], prospect: Dict[str, str], proof_of_work: Dict[str, Any]):
        """
        Sends the DM using multi-tenant isolated Browser Sessions/Proxies.
        """
        logger.info("swarm_worker_dispatching_dm", target=prospect['handle'], tenant=startup_context['name'])
        
        # Multi-Tenant DM Context
        dm_context = f"Handing them free infrastructure for {startup_context['name']}. Pitch: {startup_context['description']}"
        dm_result = await self.sdr.generate_x_dm(prospect, dm_context)
        
        if dm_result.get("success"):
            message = dm_result["x_dm_text"] + "\n\n[Attached: Blueprint & Demo Video]"
            
            # Use Tenant-Specific Session to ensure we send from their corporate X account, not Admin
            tenant_session_id = f"tenant_{startup_context['id']}_x"
            await browser_agent.initialize(force_local=True, proxy_url="http://mock-residential-proxy.local:8080")
            await browser_agent.load_session(tenant_session_id)
            
            # Dispatch
            exec_result = await browser_agent.execute_x_dm(handle=prospect['handle'], message=message)
            
            if exec_result.get("success"):
                logger.info("swarm_dispatch_successful", target=prospect['handle'], tenant=startup_context['name'])
                await self._persist_lead_to_crm(startup_context['id'], prospect, LeadStatus.CONTACTED, proof_of_work.get('blueprint_path'))
            else:
                logger.error("swarm_dispatch_failed", error=exec_result.get("error"))
        else:
            logger.error("sdr_failed_to_write_dm", error=dm_result.get("error"))


    async def launch_swarm_for_startup(self, startup_id: UUID) -> Dict[str, Any]:
        """
        Main entrypoint exposed to the API. Executes the full Swarm pipeline 
        dynamically customized for the requesting Startup.
        """
        logger.info("=========================================")
        logger.info("INITIATING MULTI-TENANT SWARM QUEUE", startup_id=str(startup_id))
        logger.info("=========================================")
        
        # 1. Fetch Dynamic Context
        context = await self._fetch_startup_context(startup_id)
        if not context:
            return {"success": False, "error": "Startup context not found or invalid"}
            
        logger.info("multi_tenant_context_loaded", startup=context['name'])
        
        # 2. Wave 1: Data Harvester (Dynamic Targeting)
        # Target their own repo stargazers if available, else fallback to a generic industry repo
        target_repo = context['github_repo'] if context.get('github_repo') else "celery/celery"
        
        logger.info("WAVE 1: Autonomous Lead Intelligence Scraping", target_repo=target_repo)
        harvest_result = await data_harvester.scrape_github_stars(repo_name=target_repo, max_results=2)
        
        if not harvest_result.get("success"):
            return {"success": False, "error": harvest_result.get("error")}
            
        prospects = harvest_result["data"]
        
        # 3. Wave 2 & 3: Asynchronous Pipeline Execution
        for prospect in prospects:
            logger.info("queue_processing_target", handle=prospect['handle'])
            
            # Persist the lead immediately as 'NEW' before beginning expensive work
            await self._persist_lead_to_crm(context['id'], prospect, LeadStatus.NEW)
            
            # Generate Assets (Dynamically passing the Startup's description to DeepSeek)
            pow_result = await self.worker_proof_of_work_generator(context, prospect)
            
            if pow_result.get("success"):
                # Dispatch DM using the Startup's isolated Playwright Session
                await self.worker_omnichannel_dispatch(context, prospect, pow_result)
                
        # Clean up global agent state
        await browser_agent.close()
        logger.info("MULTI_TENANT_SWARM_EXECUTION_COMPLETE", startup=context['name'])
        
        return {"success": True, "message": f"Successfully unleashed swarm for {context['name']}. Processed {len(prospects)} targets."}

swarm_service = SwarmService()
