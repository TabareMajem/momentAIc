"""
Vercel Deployment Webhook
Triggers growth campaign on new deployments

Part of Project PHOENIX - Vibe-Coder Integrations
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
import hmac
import hashlib

from app.core.database import AsyncSessionLocal
from app.models.startup import Startup
from app.models.user import User

logger = structlog.get_logger()

router = APIRouter()


class VercelDeploymentEvent(BaseModel):
    """Vercel webhook payload (simplified)"""
    type: str  # "deployment.created", "deployment.succeeded", etc.
    payload: Dict[str, Any]


async def trigger_launch_campaign(startup_id: str, deployment_url: str):
    """Background task to trigger growth campaign after deployment"""
    from app.agents.growth_hacker_agent import growth_hacker_agent
    from app.agents.marketing_agent import marketing_agent
    from app.services.social_scheduler import social_scheduler
    from datetime import datetime, timedelta
    
    logger.info("Vercel webhook: Triggering launch campaign", startup_id=startup_id, url=deployment_url)
    
    try:
        # 1. Analyze the deployment
        strategy = await growth_hacker_agent.analyze_startup_wizard(
            url=deployment_url,
            description=f"Fresh deployment at {deployment_url}"
        )
        
        if "error" in strategy:
            logger.error("Strategy generation failed", error=strategy["error"])
            return
        
        # 2. Generate and schedule a launch post
        hook = strategy.get("viral_post_hook", "Just shipped a new update!")
        
        content = await marketing_agent.create_social_post(
            context=f"New deployment just went live! Hook: {hook}",
            platform="twitter"
        )
        
        await social_scheduler.schedule_post(
            startup_id=startup_id,
            content=content,
            platforms=["twitter"],
            scheduled_at=datetime.utcnow() + timedelta(minutes=30)
        )
        
        logger.info("Vercel webhook: Launch campaign scheduled", startup_id=startup_id)
        
    except Exception as e:
        logger.error("Launch campaign failed", error=str(e))


@router.post("/vercel")
async def vercel_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Vercel Deployment Webhook
    
    Triggered when a Vercel project is deployed.
    Auto-triggers growth campaign for connected startups.
    
    Setup in Vercel:
    1. Go to Project Settings > Webhooks
    2. Add webhook URL: https://api.momentaic.com/api/v1/webhooks/vercel
    3. Select events: deployment.succeeded
    """
    body = await request.json()
    
    event_type = body.get("type", "")
    payload = body.get("payload", {})
    
    logger.info("Vercel webhook received", event_type=event_type)
    
    # Only process successful deployments
    if event_type != "deployment.succeeded":
        return {"status": "ignored", "reason": f"Event type {event_type} not handled"}
    
    # Extract deployment info
    deployment_url = payload.get("url", "")
    project_name = payload.get("name", "")
    
    if not deployment_url:
        return {"status": "ignored", "reason": "No deployment URL"}
    
    # Ensure https
    if not deployment_url.startswith("http"):
        deployment_url = f"https://{deployment_url}"
    
    # Find startup with matching website URL
    async with AsyncSessionLocal() as db:
        # Try to match by URL pattern
        result = await db.execute(
            select(Startup).where(
                Startup.website_url.contains(project_name)
            )
        )
        startup = result.scalar_one_or_none()
        
        if not startup:
            # Create a placeholder or just log
            logger.info("Vercel webhook: No matching startup found", project=project_name)
            return {"status": "no_match", "message": "No startup linked to this project. Connect via MomentAIc dashboard."}
        
        # Trigger campaign in background
        background_tasks.add_task(trigger_launch_campaign, str(startup.id), deployment_url)
        
        return {
            "status": "triggered",
            "startup_id": str(startup.id),
            "message": "Launch campaign triggered!"
        }


@router.post("/netlify") 
async def netlify_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Netlify Deployment Webhook
    
    Same logic as Vercel, adapted for Netlify payload format.
    """
    body = await request.json()
    
    # Netlify uses different payload structure
    state = body.get("state", "")
    deploy_url = body.get("deploy_ssl_url", "") or body.get("url", "")
    site_name = body.get("name", "")
    
    logger.info("Netlify webhook received", state=state, site=site_name)
    
    if state != "ready":
        return {"status": "ignored", "reason": f"State {state} not handled"}
    
    if not deploy_url:
        return {"status": "ignored", "reason": "No deploy URL"}
    
    # Find matching startup
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Startup).where(
                Startup.website_url.contains(site_name)
            )
        )
        startup = result.scalar_one_or_none()
        
        if not startup:
            return {"status": "no_match", "message": "No startup linked to this site."}
        
        background_tasks.add_task(trigger_launch_campaign, str(startup.id), deploy_url)
        
        return {
            "status": "triggered",
            "startup_id": str(startup.id),
            "message": "Launch campaign triggered!"
        }
