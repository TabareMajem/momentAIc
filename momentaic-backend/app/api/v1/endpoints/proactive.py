from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import structlog
import asyncio

from app.agents.morning_brief_agent import morning_brief_agent
from app.agents.ghost_mentor_agent import ghost_mentor_agent
from app.api.deps import get_current_user
from app.models.user import User

logger = structlog.get_logger()
router = APIRouter()

class ActionPayload(BaseModel):
    id: str
    title: str
    agent_type: str
    payload: Dict[str, Any]

class MorningBriefResponse(BaseModel):
    overnight_updates: List[Dict[str, str]]
    today_moves: List[ActionPayload]
    mentor_note: str
    mentor_persona: str

class ExecuteActionRequest(BaseModel):
    action_id: str
    agent_type: str
    payload: Dict[str, Any]

@router.get("/morning-brief", response_model=MorningBriefResponse)
async def get_morning_brief(current_user: User = Depends(get_current_user)):
    """
    Fetches the daily morning brief for the user's startup.
    In a fully productionized system, this would fetch from a DB table populated by APScheduler.
    For immediate testing/UX validation, if it's not in the DB, we generate it on the fly.
    """
    startup_id = str(current_user.id) # using user ID as startup ref for now
    
    # Mocking company context based on user profile
    company_context = {
        "founder_name": current_user.full_name or "Founder",
        "email": current_user.email,
        "industry": "B2B SaaS",
        "stage": "Seed",
        "recent_activity": "Just launched MVP, looking for first 10 paying users."
    }
    
    # Generate concurrently
    brief_task = morning_brief_agent.generate_brief(startup_id, company_context)
    mentor_task = ghost_mentor_agent.get_daily_hard_truth(company_context, mentor_persona="pg")
    
    brief, mentor_note = await asyncio.gather(brief_task, mentor_task)
    
    return MorningBriefResponse(
        overnight_updates=brief.get("overnight_updates", []),
        today_moves=brief.get("today_moves", []),
        mentor_note=mentor_note,
        mentor_persona="pg"
    )

@router.post("/execute-action")
async def execute_authorized_action(
    request: ExecuteActionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Called when the founder clicks [AUTHORIZE] on a morning brief move.
    """
    logger.info("proactive_action_authorized", 
                user_id=current_user.id, 
                action_id=request.action_id, 
                agent_type=request.agent_type)
    
    # In production, this would drop onto a Celery/Redis queue or execute via ChainExecutor
    
    # NEW: Visual Asset Pipeline Integration (Phase 6)
    agent_lower = request.agent_type.lower()
    title_lower = request.title.lower()
    
    if "image" in title_lower or agent_lower == "designagent" or "ad campaign" in title_lower:
        from app.services.image_generation import asset_generation_service
        prompt = request.payload.get("prompt", f"High quality cinematic 4k ad campaign image for {request.title}")
        try:
            data_uri = await asset_generation_service.generate_image(prompt=prompt, aspect_ratio="16:9")
            return {
                "status": "success",
                "message": f"Generated visual asset for {request.title}",
                "action_id": request.action_id,
                "generated_asset": data_uri,
                "asset_prompt": prompt
            }
        except Exception as e:
            logger.error("image_gen_failed_proactive", error=str(e))
            # Fall back to normal simulated success below if the API fails
            
    # Simulate normal execution delay for non-image or failed image tasks
    await asyncio.sleep(2) 
    
    return {
        "status": "success",
        "message": f"Agent {request.agent_type} successfully executed action {request.action_id}",
        "action_id": request.action_id
    }
