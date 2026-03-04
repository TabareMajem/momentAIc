"""
Lead Generation Endpoints
Powered by Browser-first Agents (Sales Navigator / LinkedIn)
"""

from typing import Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User
from app.models.startup import Startup
from app.agents.browser_prospector_agent import BrowserProspectorAgent

router = APIRouter()
browser_prospector = BrowserProspectorAgent()

class ProspectorRequest(BaseModel):
    icp_prompt: str = Field(..., description="Ideal Customer Profile description in plain text")
    limit: int = Field(default=50, le=200, description="Max number of leads to extract")

class ProspectorResponse(BaseModel):
    success: bool
    leads_found: int
    search_query: Optional[str] = None
    target_url: Optional[str] = None
    error: Optional[str] = None

@router.post("/runs", response_model=ProspectorResponse)
async def run_browser_prospector(
    startup_id: UUID,
    request: ProspectorRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger the AI SDR Browser Prospector.
    Executes a headless search (Sales Nav / LinkedIn) using the user's saved session,
    extracts matching leads based on the ICP prompt, and saves them to the CRM.
    """
    # Verify access to startup
    await verify_startup_access(startup_id, current_user, db)
    
    # Run the prospector loop
    result = await browser_prospector.run_sales_nav_loop(
        db=db,
        user_id=str(current_user.id),
        startup_id=startup_id,
        icp_prompt=request.icp_prompt,
        limit=request.limit
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to run prospector")
        )
        
    return ProspectorResponse(
        success=True,
        leads_found=result.get("leads_found", 0),
        search_query=result.get("search_query"),
        target_url=result.get("target_url")
    )
