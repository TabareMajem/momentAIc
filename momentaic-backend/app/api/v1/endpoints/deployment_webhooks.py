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


async def handle_incident_response(startup_id: str, project_name: str, payload: Dict[str, Any]):
    """Background task to analyze deployment failures and alert Slack"""
    from app.agents.devops_agent import devops_agent
    from app.integrations.community import community
    
    logger.info("Vercel webhook: Analyzing deployment failure", startup_id=startup_id, project=project_name)
    
    try:
        # Ask DevOpsAgent to analyze the failure context
        error_context = f"Project {project_name} failed deployment on Vercel. Payload details: {payload}"
        
        analysis = await devops_agent.process(
            message=f"A Vercel deployment just failed. Create a brief incident synthesis, deduce likely issues, and list 3 concrete commands or steps to triage. Source context: {error_context}",
            startup_context={"name": project_name},
            user_id="system"
        )
        
        response_text = analysis.get("response", "Could not analyze the failure.")
        
        # Format the Slack message block
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 Automated Incident Report: {project_name}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": response_text
                }
            }
        ]
        
        # Post the report to Slack
        success = await community.post_to_slack(
            channel="#incidents",
            text=f"Deployment failed for {project_name}. DevOpsAgent is on it.",
            blocks=blocks
        )
        
        if success:
            logger.info("Incident report posted to Slack successfully.")
        else:
            logger.warning("Failed to post incident report to Slack.")
            
    except Exception as e:
        logger.error("Incident response failed", error=str(e))


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
    
    # Process deployments
    if event_type == "deployment.succeeded":
        is_success = True
    elif event_type in ["deployment.error", "deployment.canceled", "deployment.failed"]:
        is_success = False
    else:
        return {"status": "ignored", "reason": f"Event type {event_type} not handled"}
    
    # Extract deployment info
    deployment_url = payload.get("url", "")
    project_name = payload.get("name", "Unknown Project")
    
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
            # Use a dummy ID for incident response if no startup is found
            startup_id = "unlinked_project"
        else:
            startup_id = str(startup.id)
        
        if is_success and startup:
            # Trigger campaign in background
            background_tasks.add_task(trigger_launch_campaign, startup_id, deployment_url)
            
            return {
                "status": "triggered_launch",
                "startup_id": startup_id,
                "message": "Launch campaign triggered!"
            }
        elif not is_success:
            # Trigger autonomous incident response
            background_tasks.add_task(handle_incident_response, startup_id, project_name, payload)
            
            return {
                "status": "triggered_incident",
                "startup_id": startup_id,
                "message": "DevOps Incident Response initiated."
            }
        
        return {"status": "ignored", "message": "Unhandled state"}


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
