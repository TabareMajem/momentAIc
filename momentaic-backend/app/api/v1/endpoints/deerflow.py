from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.deerflow_service import run_deal_oracle, run_roast_engine, run_marketing_campaign

router = APIRouter()

@router.post("/oracle")
async def execute_deal_oracle(
    submission: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deal Oracle: Spawns 6 parallel sub-agents to analyze a startup.
    Returns a Server-Sent Events (SSE) stream.
    Requires Lite tier or above.
    """
    if current_user.tier == "starter":
        raise HTTPException(status_code=403, detail="Deal Oracle requires Lite tier or above.")
        
    return StreamingResponse(
        run_deal_oracle(submission),
        media_type="text/event-stream"
    )

@router.post("/roast")
async def execute_roast_engine(
    payload: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Roast Engine: Brutal pitch deck destruction via web search facts.
    Returns a Server-Sent Events (SSE) stream.
    Open to Free/Starter tier for viral growth loop.
    """
    file_text = payload.get("file_text", "")
    claims = payload.get("claims", [])
    
    return StreamingResponse(
        run_roast_engine(file_text, claims),
        media_type="text/event-stream"
    )

@router.post("/campaign")
async def execute_marketing_campaign(
    goals: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Massive Marketing Campaigns: TikTok, X, Email blasts.
    Returns a Server-Sent Events (SSE) stream.
    Requires Lite tier or above.
    """
    if current_user.tier == "starter":
        raise HTTPException(status_code=403, detail="Marketing Campaigns require Lite tier or above.")
        
    return StreamingResponse(
        run_marketing_campaign(goals),
        media_type="text/event-stream"
    )
