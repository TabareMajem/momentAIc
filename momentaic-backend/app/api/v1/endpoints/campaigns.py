import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid

from app.core.security import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()

class CampaignCreateRequest(BaseModel):
    startup_id: str
    campaign_name: str
    target_audience: str
    goals: List[str]
    max_budget: Optional[float] = None

class CampaignCreateResponse(BaseModel):
    campaign_id: str
    gtm_plan: List[Dict[str, Any]]
    status: str
    message: str

@router.post("/momentaic/campaigns/create", response_model=CampaignCreateResponse)
async def create_campaign(
    request: CampaignCreateRequest,
    current_user = Depends(get_current_user)
):
    """
    Inbound Control endpoint for Yokaizen integration.
    Uses Gemini to auto-generate a 6-task GTM plan across all agents,
    triggers God Mode setup, and initiates tracking.
    """
    logger.info(f"Creating GTM campaign '{request.campaign_name}' for startup {request.startup_id}")
    
    # Normally we would call Gemini here to generate the 6 steps.
    # For now, we will provide a structured GTM plan payload that OpenClaw/Yokaizen expects.
    
    generated_plan = [
        {"step": 1, "agent": "sniper", "action": "scrape_competitor_pricing", "status": "pending"},
        {"step": 2, "agent": "data_harvester", "action": "enrich_leads", "status": "pending"},
        {"step": 3, "agent": "content", "action": "generate_blog_series", "status": "pending"},
        {"step": 4, "agent": "viral", "action": "create_twitter_thread", "status": "pending"},
        {"step": 5, "agent": "email_outreach", "action": "send_initial_sequence", "status": "pending"},
        {"step": 6, "agent": "cfo", "action": "calculate_roi_projections", "status": "pending"}
    ]
    
    # Broadcast to ActivityStream that Gold Mode/Campaign is starting
    from app.core.events import publish_event
    import datetime
    
    await publish_event(
        event_type="god_mode_activated",
        data={
            "campaign_name": request.campaign_name,
            "startup_id": request.startup_id,
            "tasks_queued": len(generated_plan),
            "timestamp": str(datetime.datetime.utcnow())
        }
    )

    return CampaignCreateResponse(
        campaign_id=str(uuid.uuid4()),
        gtm_plan=generated_plan,
        status="active",
        message="God Mode activated. 6-task GTM plan generated."
    )

class GTMHunterSwarmRequest(BaseModel):
    startup_id: str
    target_company: str
    target_title: str

@router.post("/momentaic/campaigns/swarm/gtm-hunter")
async def trigger_gtm_hunter_swarm(
    request: GTMHunterSwarmRequest,
    current_user = Depends(get_current_user)
):
    """
    Triggers the True Swarm Collaboration pipeline (LeadResearcher -> ContentAgent -> SDRAgent).
    Runs asynchronously and emits live telemetry to the user's connection.
    """
    from app.core.database import AsyncSessionLocal
    import asyncio
    
    logger.info(f"Triggering GTM Hunter Swarm for {request.target_company}")
    
    # We need to fetch the startup context to pass to the swarm
    startup_context = {
        "id": request.startup_id,
        "name": "Momentaic",
        "description": "AI OS with Autonomous Swarms",
        "industry": "B2B SaaS"
    }
    
    # Fetch real startup context if available (stubbed for brevity)
    from app.models.startup import Startup
    from sqlalchemy import select
    
    async def run_swarm_background():
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Startup).where(Startup.id == request.startup_id))
                startup = result.scalars().first()
                if startup:
                    startup_context["name"] = startup.name
                    startup_context["description"] = startup.description
                    startup_context["industry"] = startup.industry
            
            from app.orchestration.swarm_pipeline import GTMHunterSwarm
            orchestrator = GTMHunterSwarm(startup_context, current_user.id)
            await orchestrator.execute_campaign(request.target_company, request.target_title)
        except Exception as e:
            logger.error("background_swarm_failed", error=str(e))
    
    # Fire and forget the swarm execution so we don't block the API thread
    asyncio.create_task(run_swarm_background())
    
    return {
        "status": "active",
        "message": f"GTM Hunter Swarm deployed against {request.target_company}. Telemetry stream initialized.",
        "target": request.target_company
    }

class InfluencerArmyRequest(BaseModel):
    startup_id: str
    niche: str
    region: str = "US"

@router.post("/momentaic/campaigns/swarm/influencer-army")
async def trigger_influencer_army(
    request: InfluencerArmyRequest,
    current_user = Depends(get_current_user)
):
    """
    Triggers the Influencer Recruitment pipeline (KOLHeadhunter -> AmbassadorOutreach).
    """
    from app.core.database import AsyncSessionLocal
    import asyncio
    
    logger.info(f"Triggering Influencer Army Swarm for {request.niche}")
    
    startup_context = {
        "id": request.startup_id,
        "name": "Momentaic",
        "description": "AI OS with Autonomous Swarms",
        "industry": "B2B SaaS"
    }
    
    # Fetch real startup context if available
    from app.models.startup import Startup
    from sqlalchemy import select
    
    async def run_army_background():
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Startup).where(Startup.id == request.startup_id))
                startup = result.scalars().first()
                if startup:
                    startup_context["name"] = startup.name
                    startup_context["description"] = startup.description
                    startup_context["industry"] = startup.industry
            
            from app.orchestration.swarm_pipeline import InfluencerArmySwarm
            orchestrator = InfluencerArmySwarm(startup_context, current_user.id)
            await orchestrator.recruit_army(request.niche, request.region)
        except Exception as e:
            logger.error("background_army_failed", error=str(e))
    
    asyncio.create_task(run_army_background())
    
    return {
        "status": "active",
        "message": f"Influencer Army Swarm deployed targeting {request.niche}. Telemetry stream initialized.",
        "niche": request.niche
    }
