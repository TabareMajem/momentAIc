"""
Cross-Startup Intelligence Endpoints
"""

from typing import List, Dict, Any
import structlog
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User
from app.models.startup import Startup
from app.services.cross_startup_intelligence import cross_startup_intelligence

router = APIRouter()
logger = structlog.get_logger()

@router.get("/cross-startup", response_model=Dict[str, Any])
async def get_cross_startup_insights(
    startup_id: UUID,
    limit: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get aggregated successful playbooks from other startups in the same industry.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Get the startup's industry
    result = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = result.scalar_one_or_none()
    
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
        
    insights = await cross_startup_intelligence.get_industry_insights(
        db=db,
        industry=startup.industry,
        limit=limit
    )
    
    return {
        "industry": startup.industry,
        "insights": insights
    }
