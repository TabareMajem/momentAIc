from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_current_user
from app.models.user import User
from app.agents.product import product_agent, ProductState
from app.services.activity_stream import activity_stream

router = APIRouter()

class ProductMissionRequest(BaseModel):
    mission: str = "spec_feature" # "spec_feature", "review_code", "qa_test"
    requirement: Dict[str, Any]
    startup_id: str

@router.post("/mission")
async def run_product_mission(
    request: ProductMissionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger the Product Super Agent to architect a new feature.
    """
    
    # Track request
    await activity_stream.track(
        agent_id="product_super_agent",
        startup_id=request.startup_id,
        activity_type="mission_start",
        details={"mission": request.mission, "requirement": request.requirement}
    )
    
    background_tasks.add_task(
        _run_agent_task,
        request.mission,
        request.requirement,
        request.startup_id,
        str(current_user.id)
    )

    return {"status": "mission_started", "mission": request.mission}

async def _run_agent_task(mission: str, requirement: Dict[str, Any], startup_id: str, user_id: str):
    """
    Background task wrapper for the agent
    """
    try:
        from app.core.database import async_session_maker
        from app.models.startup import Startup
        from sqlalchemy import select
        import uuid
        
        try:
            startup_context = {
                "id": startup_id,
                "stage": "Growth", 
                "tech_stack": "React, Python, FastAPI, PostgreSQL"
            }
            async with async_session_maker() as db:
                result = await db.execute(select(Startup).where(Startup.id == uuid.UUID(startup_id)))
                startup = result.scalar_one_or_none()
                if startup:
                    startup_context["tech_stack"] = getattr(startup, "tech_stack", "React, Python, FastAPI, PostgreSQL")
        except Exception as dbe:
            import structlog
            structlog.get_logger().error("db_fetch_error", error=str(dbe))
        
        result = await product_agent.run(
            mission=mission,
            requirement=requirement,
            startup_context=startup_context,
            user_id=user_id
        )
        
        # Log success
        await activity_stream.track(
            agent_id="product_super_agent",
            startup_id=startup_id,
            activity_type="mission_complete",
            details={
                "mission": mission, 
                "spec_preview": str(result.get("spec", {}))[:200]
            }
        )
        
    except Exception as e:
        # Log failure
        await activity_stream.track(
            agent_id="product_super_agent",
            startup_id=startup_id,
            activity_type="mission_failed",
            details={"mission": mission, "error": str(e)}
        )
