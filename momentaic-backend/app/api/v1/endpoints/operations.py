from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_current_user
from app.models.user import User
from app.agents.operations import operations_agent
from app.services.activity_stream import activity_stream

router = APIRouter()

class OperationsMissionRequest(BaseModel):
    mission: str # "compliance_check", "financial_review", "hr_policy"
    context: Dict[str, Any]
    startup_id: str

@router.post("/mission")
async def run_operations_mission(
    request: OperationsMissionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger the Operations Super Agent for a specific mission.
    """
    
    # Track request
    await activity_stream.track(
        agent_id="operations_super_agent",
        startup_id=request.startup_id,
        activity_type="mission_start",
        details={"mission": request.mission, "context": request.context}
    )
    
    # Run Agent in background (or foreground if fast enough - let's do background for now)
    # Actually, the UI expects a quick response to acknowledge.
    # We'll use background task to run the full agent loop.
    
    background_tasks.add_task(
        _run_agent_task,
        request.mission,
        request.context,
        request.startup_id,
        str(current_user.id)
    )

    return {"status": "mission_started", "mission": request.mission}

async def _run_agent_task(mission: str, context: Dict[str, Any], startup_id: str, user_id: str):
    """
    Background task wrapper for the agent
    """
    try:
        # Get startup context (mock for now or fetch from DB)
        startup_context = {
            "id": startup_id,
            "stage": "Growth", 
            "industry": "Technology" # In real app, fetch from DB
        }
        
        result = await operations_agent.run(
            mission=mission,
            context=context,
            startup_context=startup_context, # TODO: Load real context
            user_id=user_id
        )
        
        # Log success
        await activity_stream.track(
            agent_id="operations_super_agent",
            startup_id=startup_id,
            activity_type="mission_complete",
            details={"mission": mission, "result": result.get("report")}
        )
        
    except Exception as e:
        # Log failure
        await activity_stream.track(
            agent_id="operations_super_agent",
            startup_id=startup_id,
            activity_type="mission_failed",
            details={"mission": mission, "error": str(e)}
        )
