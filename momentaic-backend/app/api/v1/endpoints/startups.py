"""
Startup Management Endpoints
CRUD and dashboard operations for startups
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User
from app.models.startup import Startup, StartupStage, Signal, Sprint
from app.models.growth import Lead, LeadStatus
from app.models.conversation import Conversation
from app.schemas.startup import (
    StartupCreate,
    StartupUpdate,
    StartupResponse,
    StartupDashboard,
    MetricsUpdate,
    SprintCreate,
    SprintUpdate,
    SprintResponse,
    SprintWithStandups,
    StandupCreate,
    StandupResponse,
)

router = APIRouter()


@router.post("", response_model=StartupResponse, status_code=status.HTTP_201_CREATED)
async def create_startup(
    startup_data: StartupCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new startup entity.
    """
    startup = Startup(
        owner_id=current_user.id,
        name=startup_data.name,
        tagline=startup_data.tagline,
        description=startup_data.description,
        industry=startup_data.industry,
        stage=startup_data.stage,
        github_repo=startup_data.github_repo,
        website_url=startup_data.website_url,
        metrics=startup_data.metrics or {},
    )
    
    db.add(startup)
    await db.flush()
    
    return StartupResponse.model_validate(startup)


@router.get("", response_model=List[StartupResponse])
async def list_startups(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    List all startups owned by the current user.
    """
    result = await db.execute(
        select(Startup)
        .where(Startup.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Startup.created_at.desc())
    )
    startups = result.scalars().all()
    
    return [StartupResponse.model_validate(s) for s in startups]


@router.get("/{startup_id}", response_model=StartupResponse)
async def get_startup(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific startup by ID.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Startup).where(Startup.id == startup_id)
    )
    startup = result.scalar_one()
    
    return StartupResponse.model_validate(startup)


@router.patch("/{startup_id}", response_model=StartupResponse)
async def update_startup(
    startup_id: UUID,
    update_data: StartupUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a startup's details.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Startup).where(Startup.id == startup_id)
    )
    startup = result.scalar_one()
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(startup, field, value)
    
    return StartupResponse.model_validate(startup)


@router.delete("/{startup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_startup(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a startup and all related data.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Startup).where(Startup.id == startup_id)
    )
    startup = result.scalar_one()
    
    await db.delete(startup)


@router.get("/{startup_id}/dashboard", response_model=StartupDashboard)
async def get_dashboard(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get aggregated dashboard data for a startup.
    Includes latest signal, active sprint, lead summary, and recent activity.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Get startup
    result = await db.execute(
        select(Startup).where(Startup.id == startup_id)
    )
    startup = result.scalar_one()
    
    # Get latest signal
    result = await db.execute(
        select(Signal)
        .where(Signal.startup_id == startup_id)
        .order_by(Signal.calculated_at.desc())
        .limit(1)
    )
    latest_signal = result.scalar_one_or_none()
    
    # Get active sprint
    result = await db.execute(
        select(Sprint)
        .where(Sprint.startup_id == startup_id, Sprint.status == "active")
        .order_by(Sprint.created_at.desc())
        .limit(1)
    )
    active_sprint = result.scalar_one_or_none()
    
    # Get lead summary by status
    lead_counts = {}
    for status in LeadStatus:
        result = await db.execute(
            select(func.count(Lead.id))
            .where(Lead.startup_id == startup_id, Lead.status == status)
        )
        lead_counts[status.value] = result.scalar() or 0
    
    # Get scheduled content count
    from app.models.growth import ContentItem, ContentStatus
    result = await db.execute(
        select(func.count(ContentItem.id))
        .where(
            ContentItem.startup_id == startup_id,
            ContentItem.status == ContentStatus.SCHEDULED
        )
    )
    content_scheduled = result.scalar() or 0
    
    # Recent activity (simplified)
    recent_activity = [
        {"type": "startup_created", "message": f"Startup '{startup.name}' created", "timestamp": startup.created_at.isoformat()},
    ]
    
    from app.schemas.startup import SignalResponse, SprintResponse
    
    return StartupDashboard(
        startup=StartupResponse.model_validate(startup),
        latest_signal=SignalResponse.model_validate(latest_signal) if latest_signal else None,
        active_sprint=SprintResponse.model_validate(active_sprint) if active_sprint else None,
        lead_summary=lead_counts,
        content_scheduled=content_scheduled,
        recent_activity=recent_activity,
    )


@router.patch("/{startup_id}/metrics", response_model=StartupResponse)
async def update_metrics(
    startup_id: UUID,
    metrics_data: MetricsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update startup metrics (MRR, DAU, etc.).
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Startup).where(Startup.id == startup_id)
    )
    startup = result.scalar_one()
    
    # Merge new metrics with existing
    new_metrics = metrics_data.model_dump(exclude_unset=True, exclude_none=True)
    startup.metrics = {**startup.metrics, **new_metrics}
    
    return StartupResponse.model_validate(startup)


# Sprint endpoints
@router.post("/{startup_id}/sprints", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    startup_id: UUID,
    sprint_data: SprintCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new sprint for a startup.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    sprint = Sprint(
        startup_id=startup_id,
        goal=sprint_data.goal,
        key_results=sprint_data.key_results,
        start_date=sprint_data.start_date,
        end_date=sprint_data.end_date,
        status="active",
    )
    
    db.add(sprint)
    await db.flush()
    
    return SprintResponse.model_validate(sprint)


@router.get("/{startup_id}/sprints", response_model=List[SprintResponse])
async def list_sprints(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = None,
):
    """
    List sprints for a startup.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    query = select(Sprint).where(Sprint.startup_id == startup_id)
    if status:
        query = query.where(Sprint.status == status)
    query = query.order_by(Sprint.created_at.desc())
    
    result = await db.execute(query)
    sprints = result.scalars().all()
    
    return [SprintResponse.model_validate(s) for s in sprints]


@router.get("/{startup_id}/sprints/{sprint_id}", response_model=SprintWithStandups)
async def get_sprint(
    startup_id: UUID,
    sprint_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a sprint with its standups.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Sprint)
        .where(Sprint.id == sprint_id, Sprint.startup_id == startup_id)
        .options(selectinload(Sprint.standups))
    )
    sprint = result.scalar_one_or_none()
    
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    return SprintWithStandups.model_validate(sprint)


@router.patch("/{startup_id}/sprints/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    startup_id: UUID,
    sprint_id: UUID,
    update_data: SprintUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a sprint.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Sprint).where(Sprint.id == sprint_id, Sprint.startup_id == startup_id)
    )
    sprint = result.scalar_one_or_none()
    
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(sprint, field, value)
    
    return SprintResponse.model_validate(sprint)


# Standup endpoints
@router.post("/{startup_id}/sprints/{sprint_id}/standups", response_model=StandupResponse)
async def create_standup(
    startup_id: UUID,
    sprint_id: UUID,
    standup_data: StandupCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a daily standup entry.
    AI analyzes alignment with sprint goal.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Verify sprint exists
    result = await db.execute(
        select(Sprint).where(Sprint.id == sprint_id, Sprint.startup_id == startup_id)
    )
    sprint = result.scalar_one_or_none()
    
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    from app.models.startup import Standup
    
    standup = Standup(
        sprint_id=sprint_id,
        yesterday=standup_data.yesterday,
        today=standup_data.today,
        blockers=standup_data.blockers,
        mood=standup_data.mood,
    )
    
    # TODO: Use LLM to calculate alignment score
    # Compare standup.today with sprint.goal
    standup.alignment_score = 0.75  # Placeholder
    standup.ai_feedback = "Good progress on the sprint goal!"
    
    db.add(standup)
    await db.flush()
    
    return StandupResponse.model_validate(standup)
