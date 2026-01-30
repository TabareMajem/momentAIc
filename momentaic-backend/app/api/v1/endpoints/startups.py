"""
Startup Management Endpoints
CRUD and dashboard operations for startups
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
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
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

router = APIRouter()


# ============ INSTANT ANALYSIS (WOW ONBOARDING) ============

class InstantAnalysisRequest(BaseModel):
    description: str


@router.post("/instant-analysis")
async def instant_analysis(
    request: InstantAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    SSE endpoint for the WOW onboarding experience.
    Streams progress updates as agents analyze the startup.
    
    Events:
    - progress: Step updates with percentage
    - competitor: Each competitor discovered
    - insight: Industry/stage detection
    - complete: Full AI CEO report
    - error: If something fails
    """
    from app.services.instant_analysis import instant_analysis_service
    
    async def event_generator():
        async for event in instant_analysis_service.stream_analysis(
            description=request.description,
            user_id=str(current_user.id)
        ):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ============ STARTUP CRUD ============


@router.post("", response_model=StartupResponse, status_code=status.HTTP_201_CREATED)
async def create_startup(
    startup_data: StartupCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new startup entity.
    """
    # === TIER LIMIT CHECK ===
    from app.core.tier_limits import can_create_startup
    
    # Count user's current startups
    result = await db.execute(
        select(func.count(Startup.id)).where(Startup.owner_id == current_user.id)
    )
    current_count = result.scalar() or 0
    
    allowed, message = can_create_startup(current_user, current_count)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=message
        )
    # === END TIER LIMIT CHECK ===
    
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
    
    # === WOW ONBOARDING: PERSIST MEMORY ===
    if startup_data.initial_analysis:
        try:
            from app.models.conversation import AgentMemory, AgentType
            import json
            
            # Save the full report as context for the Supervisor/General agent
            memory = AgentMemory(
                startup_id=startup.id,
                agent_type=AgentType.GENERAL,
                memory_type="context",
                content=json.dumps(startup_data.initial_analysis),
                importance=10, # Critical context
                source_conversation_id=None
            )
            db.add(memory)
            await db.flush()
            logger.info("Persisted initial analysis to AgentMemory", startup_id=startup.id)
            
        except Exception as e:
            logger.error(f"Failed to persist initial analysis: {e}")
    # ======================================

    # === WOW ONBOARDING: TRIGGER DAILY DRIVER IMMEDIATELY ===
    # This pre-seeds the dashboard with an action plan and "activity"
    try:
        from app.tasks.daily_driver import run_daily_driver
        
        startup_context = {
            "id": str(startup.id),
            "name": startup.name,
            "description": startup.description or "",
            "industry": startup.industry or "Technology",
            "stage": startup.stage or "idea",
            "founder_name": current_user.full_name or "Founder"
        }
        
        background_tasks.add_task(run_daily_driver, str(startup.id), startup_context)
    except Exception as e:
        # Don't fail creation if trigger fails, just log it
        print(f"Failed to trigger initial daily driver: {e}")
    # ========================================================
    
    # === PROJECT PHOENIX: AUTO-CREATE DEFAULT TRIGGERS ===
    try:
        from app.triggers.default_triggers import create_default_triggers
        await create_default_triggers(db, startup.id, current_user.id)
    except Exception as e:
        print(f"Failed to create default triggers: {e}")
    # =====================================================
    
    await db.commit()
    
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
    
    # Recent activity (REAL)
    activities = []
    
    # 1. New Leads (Last 5)
    recent_leads = await db.execute(
        select(Lead)
        .where(Lead.startup_id == startup_id)
        .order_by(Lead.created_at.desc())
        .limit(5)
    )
    for lead in recent_leads.scalars():
        activities.append({
            "type": "lead_acquired",
            "message": f"New lead identified: {lead.company_name}",
            "timestamp": lead.created_at,
            "agent": "Sales Hunter",
            "status": "success"
        })

    # 2. Content Updates (Last 5)
    recent_content = await db.execute(
        select(ContentItem)
        .where(ContentItem.startup_id == startup_id)
        .order_by(ContentItem.updated_at.desc())
        .limit(5)
    )
    for content in recent_content.scalars():
        action = "drafted"
        if content.status == ContentStatus.SCHEDULED: action = "scheduled"
        elif content.status == ContentStatus.PUBLISHED: action = "published"
        
        activities.append({
            "type": f"content_{action}",
            "message": f"Content '{content.title[:30]}...' {action}",
            "timestamp": content.updated_at,
            "agent": "Content Strategist",
            "status": "success"
        })

    # 3. Agent Workflow Logs (Last 10)
    # We join with WorkflowRun and Workflow to ensure it belongs to this startup
    from app.models.workflow import WorkflowLog, WorkflowRun, Workflow, LogLevel
    
    recent_logs = await db.execute(
        select(WorkflowLog, Workflow.name)
        .join(WorkflowRun, WorkflowLog.run_id == WorkflowRun.id)
        .join(Workflow, WorkflowRun.workflow_id == Workflow.id)
        .where(Workflow.startup_id == startup_id, WorkflowLog.level == LogLevel.SUCCESS)
        .order_by(WorkflowLog.timestamp.desc())
        .limit(10)
    )
    
    for log, wf_name in recent_logs:
        activities.append({
            "type": "agent_action",
            "message": f"{wf_name}: {log.message}",
            "timestamp": log.timestamp,
            "agent": "Workflow Agent", # Could be more specific if we had agent name in log
            "status": "success"
        })
        
    # 4. Startup Creation (Always include if recent)
    activities.append({
        "type": "startup_created", 
        "message": f"Startup '{startup.name}' initialized", 
        "timestamp": startup.created_at,
        "agent": "System",
        "status": "success"
    })
    
    # Sort by timestamp desc and take top 10
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    activities = activities[:10]
    
    # Convert timestamps to string for JSON
    recent_activity = [
        {**a, "timestamp": a["timestamp"].isoformat()} 
        for a in activities
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
    
    # [PHASE 25 FIX] Calculate alignment using LLM
    from app.agents.base import get_llm
    
    llm = get_llm("gemini-flash", temperature=0.3)
    alignment_score = 0.5
    feedback = "Keep pushing!"
    
    if llm:
        try:
            prompt = f"""Evaluate daily standup alignment with sprint goal.
            Sprint Goal: {sprint.goal}
            
            Standup:
            - Yesterday: {standup_data.yesterday}
            - Today: {standup_data.today}
            - Blockers: {standup_data.blockers}
            
            Return strictly JSON:
            {{
                "score": <float 0.0-1.0>,
                "feedback": "<short constructive feedback>"
            }}"""
            
            response = await llm.ainvoke(prompt)
            import json
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            data = json.loads(content)
            alignment_score = float(data.get("score", 0.5))
            feedback = data.get("feedback", "Good update.")
        except Exception as e:
            logger.warning("Failed to calculate alignment", error=str(e))
            
    standup.alignment_score = alignment_score
    standup.ai_feedback = feedback
    
    db.add(standup)
    await db.flush()
    
    return StandupResponse.model_validate(standup)
