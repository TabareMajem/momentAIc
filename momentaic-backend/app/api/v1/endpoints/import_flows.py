
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.startup import ImportSourceRequest
from app.services.import_service import import_service
from app.agents.growth_hacker_agent import growth_hacker_agent
import structlog

logger = structlog.get_logger()
router = APIRouter()

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.services.execution_maestro import execution_maestro

@router.post("", response_model=Dict[str, Any])
async def import_external_source(
    request: ImportSourceRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """
    Universal Import Endpoint (The "God Mode" Entry Point)
    Accepts specific sources (GitHub, Web, Doc) and returns a normalized Execution Strategy.
    Triggers autonomous execution in the background.
    """
    try:
        # 1. Fetch & Normalize Context
        context = await import_service.import_from_source(
            source_type=request.source_type.value,
            url=request.url,
            extra_data=request.extra_data
        )
        
        # 2. Analyze with Growth Hacker (Strategy Generation)
        prompt_desc = f"""
        Source: {context['source_metadata']['source'].upper()}
        Title: {context['name']}
        
        Content Overview:
        {context['description']}
        
        Full Content Sample:
        {context['content'][:15000]}
        """
        
        analysis = await growth_hacker_agent.analyze_startup_wizard(
            url=request.url,
            description=prompt_desc
        )
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])

        # 3. Generate Execution Plan (God Mode)
        # We use a placeholder startup_id for now, or the current user's ID/context
        # In a real flow, we should create the startup first. 
        # For this endpoint, we'll generate the plan and let the frontend decide to "Approve & Execute" or we just do it.
        # The user asked to "execute for real", so we go for it.
        
        plan = await execution_maestro.generate_plan_from_strategy(
            startup_id=str(current_user.id), # Using user ID as proxy for now
            strategy=analysis,
            context=context
        )
        
        # 4. Trigger Execution in Background
        background_tasks.add_task(execution_maestro.execute_plan, plan)
            
        # 5. Return Combined Result
        return {
            "source": request.source_type.value,
            "import_details": {
                "name": context["name"],
                "description": context["description"],
                "metadata": context["source_metadata"]
            },
            "strategy": analysis,
            "execution_plan": plan.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Universal import failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Import failed: {str(e)}"
        )
