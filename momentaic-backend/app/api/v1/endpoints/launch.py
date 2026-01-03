"""
Launch API Endpoints
Product launch strategy generation with credit gating
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user, require_credits
from app.core.database import get_db
from app.models.user import User
from app.agents.launch_strategist_agent import launch_strategist_agent
from app.data.launch_platforms import get_all_segments, get_platforms_for_segment

router = APIRouter(prefix="/launch", tags=["Launch Strategy"])


# ==================
# Request/Response Models
# ==================

class LaunchStrategyRequest(BaseModel):
    """Request body for launch strategy"""
    product_name: str
    description: str
    target_audience: str = "early adopters and tech enthusiasts"
    include_product_hunt: bool = True


class PlatformResponse(BaseModel):
    """Single platform response"""
    name: str
    url: str
    type: str
    audience_size: str
    cost: str
    best_for: List[str]
    tips: List[str]


# ==================
# Endpoints
# ==================

@router.post("/strategy")
async def generate_launch_strategy(
    request: LaunchStrategyRequest,
    current_user: "User" = Depends(require_credits(15, "Launch Strategy")),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a comprehensive launch strategy - 15 credits
    
    Includes:
    - Segment detection
    - Top 15 platform recommendations with custom copy
    - 3-phase launch plan (pre-launch, launch day, post-launch)
    - Product Hunt strategy (optional)
    - Launch calendar
    """
    try:
        strategy = await launch_strategist_agent.generate_launch_strategy(
            product_name=request.product_name,
            description=request.description,
            target_audience=request.target_audience,
            include_product_hunt=request.include_product_hunt,
        )
        result = strategy.to_dict()
        result["credits_consumed"] = 15
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy generation failed: {str(e)}")


@router.get("/segments")
async def list_segments():
    """Get available launch segments (free)"""
    return {
        "segments": [
            {"id": "entrepreneur", "name": "Entrepreneur & Startup", "platforms": 50, "description": "Directories, communities, and media for startups"},
            {"id": "ai_agents", "name": "AI & Agents", "platforms": 40, "description": "AI-specific directories, newsletters, and communities"},
            {"id": "anime_gaming", "name": "Anime & Gaming", "platforms": 30, "description": "Gaming marketplaces, anime communities, streaming"},
            {"id": "b2c_consumer", "name": "B2C Consumer", "platforms": 30, "description": "App stores, consumer tech, influencer platforms"},
            {"id": "developer_tools", "name": "Developer Tools", "platforms": 20, "description": "Package registries, dev communities, marketplaces"},
        ]
    }


@router.get("/platforms/{segment}")
async def get_platforms(
    segment: str,
    limit: int = 20,
    current_user: "User" = Depends(require_credits(5, "Platform List")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get platforms for a specific segment - 5 credits
    
    Valid segments: entrepreneur, ai_agents, anime_gaming, b2c_consumer, developer_tools
    """
    valid_segments = get_all_segments()
    
    if segment not in valid_segments:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid segment. Valid options: {', '.join(valid_segments)}"
        )
    
    platforms = get_platforms_for_segment(segment, limit=limit)
    
    return {
        "segment": segment,
        "count": len(platforms),
        "platforms": platforms,
        "credits_consumed": 5,
    }


@router.post("/product-hunt")
async def generate_product_hunt_strategy(
    request: LaunchStrategyRequest,
    current_user: "User" = Depends(require_credits(20, "Product Hunt Strategy")),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate Product Hunt specific strategy - 20 credits
    
    Includes:
    - Optimal launch timing
    - Tagline generation (60 chars max)
    - First comment draft
    - Hunter recommendations
    - Preparation checklist
    """
    try:
        strategy = await launch_strategist_agent.generate_launch_strategy(
            product_name=request.product_name,
            description=request.description,
            target_audience=request.target_audience,
            include_product_hunt=True,
        )
        
        result = {
            "product_name": request.product_name,
            "product_hunt_strategy": strategy.to_dict().get("product_hunt_strategy"),
            "top_complementary_platforms": [
                p for p in strategy.to_dict().get("platforms", [])[:5]
            ],
            "credits_consumed": 20,
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy generation failed: {str(e)}")


@router.get("/health")
async def launch_health():
    """Check launch agent health"""
    from app.agents.launch_executor_agent import launch_executor_agent
    
    return {
        "status": "ready",
        "agents": {
            "strategist": "launch_strategist",
            "executor": "launch_executor",
        },
        "segments": get_all_segments(),
        "supported_platforms": launch_executor_agent.get_supported_platforms(),
    }


# ==================
# EXECUTOR ENDPOINTS
# ==================

class ExecuteRequest(BaseModel):
    """Request body for launch execution"""
    product_name: str
    tagline: str
    url: str
    description: str
    email: str = ""
    platforms: List[str] = []  # Empty = all supported
    mode: str = "dry_run"  # "dry_run" or "execute"


@router.post("/execute/dry-run")
async def execute_dry_run(
    request: ExecuteRequest,
    current_user: "User" = Depends(require_credits(10, "Launch Dry Run")),
    db: AsyncSession = Depends(get_db),
):
    """
    Preview launch submissions without actually submitting - 10 credits
    
    Shows what would be submitted to each platform:
    - Form data mapping
    - Field values
    - Screenshots of filled forms
    """
    from app.agents.launch_executor_agent import launch_executor_agent, ExecutionMode
    
    try:
        # Prepare product info
        product_info = {
            "name": request.product_name,
            "tagline": request.tagline,
            "url": request.url,
            "description": request.description,
            "email": request.email,
        }
        
        # Use all supported platforms if none specified
        platforms = request.platforms
        if not platforms:
            platforms = [p["id"] for p in launch_executor_agent.get_supported_platforms() if not p["requires_login"]][:5]
        
        job = await launch_executor_agent.execute_launch(
            product_info=product_info,
            platforms=platforms,
            mode=ExecutionMode.DRY_RUN,
        )
        
        result = job.to_dict()
        result["credits_consumed"] = 10
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dry run failed: {str(e)}")


@router.post("/execute")
async def execute_launch(
    request: ExecuteRequest,
    current_user: "User" = Depends(require_credits(50, "Launch Execute")),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute autonomous launch submissions - 50 credits
    
    ⚠️ This will ACTUALLY submit your product to platforms!
    
    Includes:
    - Automated form filling
    - Real submissions
    - Screenshot proofs
    - Status tracking
    """
    from app.agents.launch_executor_agent import launch_executor_agent, ExecutionMode
    
    if request.mode != "execute":
        raise HTTPException(
            status_code=400,
            detail="Use /execute/dry-run for preview mode. Set mode='execute' to confirm submission."
        )
    
    try:
        product_info = {
            "name": request.product_name,
            "tagline": request.tagline,
            "url": request.url,
            "description": request.description,
            "email": request.email,
        }
        
        platforms = request.platforms
        if not platforms:
            # For execute, only use platforms that don't require login
            platforms = [p["id"] for p in launch_executor_agent.get_supported_platforms() if not p["requires_login"]]
        
        job = await launch_executor_agent.execute_launch(
            product_info=product_info,
            platforms=platforms,
            mode=ExecutionMode.EXECUTE,
        )
        
        result = job.to_dict()
        result["credits_consumed"] = 50
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/execute/{job_id}/status")
async def get_execution_status(
    job_id: str,
    current_user: "User" = Depends(get_current_active_user),
):
    """Get status of an execution job (free)"""
    from app.agents.launch_executor_agent import launch_executor_agent
    
    job = launch_executor_agent.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job.to_dict()


@router.post("/execute/{job_id}/cancel")
async def cancel_execution(
    job_id: str,
    current_user: "User" = Depends(get_current_active_user),
):
    """Cancel a running execution job (free)"""
    from app.agents.launch_executor_agent import launch_executor_agent
    
    success = launch_executor_agent.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Job not found or already completed")
    
    return {"status": "cancelled", "job_id": job_id}


@router.get("/execute/platforms")
async def get_supported_platforms():
    """Get list of platforms supported for execution (free)"""
    from app.agents.launch_executor_agent import launch_executor_agent
    
    platforms = launch_executor_agent.get_supported_platforms()
    
    return {
        "total": len(platforms),
        "platforms": platforms,
        "notes": "Platforms marked as 'requires_login: true' need credentials to be provided",
    }
