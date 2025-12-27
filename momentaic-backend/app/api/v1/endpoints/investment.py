"""
Investment Dashboard API Endpoints
Provides investment-related data for dashboard display
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.startup import Startup

router = APIRouter(prefix="/investment", tags=["Investment"])


class InvestmentDashboardItem(BaseModel):
    startup_id: str
    startup_name: str
    stage: str
    composite_score: float
    technical_velocity_score: float
    pmf_score: float
    capital_efficiency_score: float
    founder_performance_score: float
    investment_status: str
    investment_eligible: bool
    last_updated: str | None = None

    class Config:
        from_attributes = True


@router.get("/dashboard", response_model=List[InvestmentDashboardItem])
async def get_investment_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get investment dashboard data showing all startups with their scores.
    
    Returns investment-relevant metrics for each startup.
    """
    # Get user's startups
    result = await db.execute(
        select(Startup).where(Startup.owner_id == current_user.id)
    )
    startups = result.scalars().all()

    dashboard_items = []
    for startup in startups:
        # TODO: Get actual signal scores from signals service
        # For now, return placeholder scores
        item = InvestmentDashboardItem(
            startup_id=str(startup.id),
            startup_name=startup.name,
            stage=startup.stage.value if hasattr(startup.stage, 'value') else str(startup.stage),
            composite_score=75.0,  # Placeholder
            technical_velocity_score=80.0,
            pmf_score=70.0,
            capital_efficiency_score=75.0,
            founder_performance_score=78.0,
            investment_status="tracking",
            investment_eligible=True,
            last_updated=startup.updated_at.isoformat() if startup.updated_at else None,
        )
        dashboard_items.append(item)

    return dashboard_items
