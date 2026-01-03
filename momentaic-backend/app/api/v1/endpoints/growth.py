"""
Growth Engine Endpoints
CRM (Leads) and Content Studio
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access, require_credits
from app.core.config import settings
from app.models.user import User
from app.models.startup import Startup
from app.models.growth import (
    Lead, LeadStatus, LeadSource, OutreachMessage,
    ContentItem, ContentPlatform, ContentStatus,
    AcquisitionChannel, ChannelMetric,
)
from app.schemas.growth import (
    LeadCreate, LeadUpdate, LeadResponse, LeadWithMessages, LeadKanbanResponse,
    LeadAutopilotRequest, OutreachMessageCreate, OutreachMessageResponse,
    GenerateOutreachRequest, GenerateOutreachResponse,
    ContentCreate, ContentUpdate, ContentResponse,
    GenerateContentRequest, GenerateContentResponse, ContentCalendarResponse,
    AcquisitionChannelCreate, AcquisitionChannelUpdate, AcquisitionChannelResponse,
    ChannelSummaryResponse,
)

router = APIRouter()


# ==================
# Lead Management (CRM)
# ==================

@router.get("/leads", response_model=List[LeadResponse])
async def list_leads(
    startup_id: UUID,
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List leads for a startup with optional filters.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    query = select(Lead).where(Lead.startup_id == startup_id)
    
    if status:
        query = query.where(Lead.status == status)
    if source:
        query = query.where(Lead.source == source)
    
    query = query.order_by(Lead.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    leads = result.scalars().all()
    
    return [LeadResponse.model_validate(l) for l in leads]


@router.get("/leads/kanban", response_model=LeadKanbanResponse)
async def get_leads_kanban(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get leads organized by pipeline stage (Kanban view).
    """
    await verify_startup_access(startup_id, current_user, db)
    
    kanban = {}
    
    for status in LeadStatus:
        result = await db.execute(
            select(Lead)
            .where(Lead.startup_id == startup_id, Lead.status == status)
            .order_by(Lead.updated_at.desc())
            .limit(50)
        )
        leads = result.scalars().all()
        kanban[status.value] = [LeadResponse.model_validate(l) for l in leads]
    
    return LeadKanbanResponse(**kanban)


@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    startup_id: UUID,
    lead_data: LeadCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new lead to the CRM.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    lead = Lead(
        startup_id=startup_id,
        company_name=lead_data.company_name,
        company_website=lead_data.company_website,
        company_size=lead_data.company_size,
        company_industry=lead_data.company_industry,
        contact_name=lead_data.contact_name,
        contact_title=lead_data.contact_title,
        contact_email=lead_data.contact_email,
        contact_linkedin=lead_data.contact_linkedin,
        contact_phone=lead_data.contact_phone,
        source=lead_data.source,
        deal_value=lead_data.deal_value,
        notes=lead_data.notes,
        tags=lead_data.tags,
    )
    
    db.add(lead)
    await db.flush()
    
    return LeadResponse.model_validate(lead)


@router.get("/leads/{lead_id}", response_model=LeadWithMessages)
async def get_lead(
    startup_id: UUID,
    lead_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a lead with its outreach history.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Lead)
        .options(selectinload(Lead.outreach_messages))
        .where(Lead.id == lead_id, Lead.startup_id == startup_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return LeadWithMessages.model_validate(lead)


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    startup_id: UUID,
    lead_id: UUID,
    lead_update: LeadUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a lead's details or move in pipeline.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.startup_id == startup_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    update_data = lead_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    return LeadResponse.model_validate(lead)


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    startup_id: UUID,
    lead_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a lead.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.startup_id == startup_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    await db.delete(lead)


@router.post("/leads/{lead_id}/autopilot", response_model=LeadResponse)
async def toggle_autopilot(
    startup_id: UUID,
    lead_id: UUID,
    autopilot_request: LeadAutopilotRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Enable/disable autonomous outreach for a lead.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.startup_id == startup_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    lead.autopilot_enabled = autopilot_request.enabled
    lead.agent_state = {
        **lead.agent_state,
        "max_followups": autopilot_request.max_followups,
        "followup_interval_days": autopilot_request.followup_interval_days,
    }
    
    return LeadResponse.model_validate(lead)


@router.post("/leads/{lead_id}/generate-outreach", response_model=GenerateOutreachResponse)
async def generate_outreach(
    startup_id: UUID,
    lead_id: UUID,
    gen_request: GenerateOutreachRequest,
    current_user: User = Depends(require_credits(settings.credit_cost_outreach_gen, "Outreach generation")),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI-powered personalized outreach.
    
    Costs 2 credits.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Get lead and startup
    lead_result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.startup_id == startup_id)
    )
    lead = lead_result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    startup_result = await db.execute(
        select(Startup).where(Startup.id == startup_id)
    )
    startup = startup_result.scalar_one()
    
    # Use Sales Agent to generate outreach
    from app.agents.sales_agent import sales_agent
    
    result = await sales_agent.run(
        lead=lead,
        startup_context={
            "name": startup.name,
            "description": startup.description,
            "tagline": startup.tagline,
            "industry": startup.industry,
        },
        user_id=str(current_user.id),
    )
    
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Generation failed")
        )
    
    draft = result.get("draft", {})
    strategy = result.get("strategy", {})
    
    return GenerateOutreachResponse(
        subject=draft.get("subject"),
        body=draft.get("body", ""),
        hook_used=strategy.get("hook", ""),
        personalization_points=strategy.get("key_points", []),
    )


@router.post("/leads/{lead_id}/messages", response_model=OutreachMessageResponse)
async def create_outreach_message(
    startup_id: UUID,
    lead_id: UUID,
    message_data: OutreachMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create an outreach message (manual or from AI draft).
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Verify lead exists
    lead_result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.startup_id == startup_id)
    )
    lead = lead_result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    message = OutreachMessage(
        lead_id=lead_id,
        channel=message_data.channel,
        subject=message_data.subject,
        body=message_data.body,
        direction="outbound",
        status="draft",
    )
    
    db.add(message)
    await db.flush()
    
    return OutreachMessageResponse.model_validate(message)


@router.post("/leads/{lead_id}/messages/{message_id}/send", response_model=OutreachMessageResponse)
async def send_outreach_message(
    startup_id: UUID,
    lead_id: UUID,
    message_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a drafted outreach message.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(OutreachMessage)
        .join(Lead)
        .where(
            OutreachMessage.id == message_id,
            Lead.id == lead_id,
            Lead.startup_id == startup_id
        )
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # In production, actually send via Gmail/SendGrid API
    message.status = "sent"
    message.sent_at = datetime.utcnow()
    
    # Update lead
    lead_result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = lead_result.scalar_one()
    lead.last_contacted_at = datetime.utcnow()
    lead.status = LeadStatus.OUTREACH
    
    return OutreachMessageResponse.model_validate(message)


# ==================
# Content Studio
# ==================

@router.get("/content", response_model=List[ContentResponse])
async def list_content(
    startup_id: UUID,
    platform: Optional[ContentPlatform] = None,
    status: Optional[ContentStatus] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List content items for a startup.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    query = select(ContentItem).where(ContentItem.startup_id == startup_id)
    
    if platform:
        query = query.where(ContentItem.platform == platform)
    if status:
        query = query.where(ContentItem.status == status)
    
    query = query.order_by(ContentItem.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return [ContentResponse.model_validate(i) for i in items]


@router.get("/content/calendar", response_model=ContentCalendarResponse)
async def get_content_calendar(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get content organized for calendar view.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Scheduled content
    scheduled_result = await db.execute(
        select(ContentItem)
        .where(
            ContentItem.startup_id == startup_id,
            ContentItem.status == ContentStatus.SCHEDULED
        )
        .order_by(ContentItem.scheduled_for)
    )
    scheduled = scheduled_result.scalars().all()
    
    # Drafts
    drafts_result = await db.execute(
        select(ContentItem)
        .where(
            ContentItem.startup_id == startup_id,
            ContentItem.status.in_([ContentStatus.IDEA, ContentStatus.DRAFTING, ContentStatus.REVIEW])
        )
        .order_by(ContentItem.updated_at.desc())
        .limit(20)
    )
    drafts = drafts_result.scalars().all()
    
    # Published this week
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    published_result = await db.execute(
        select(ContentItem)
        .where(
            ContentItem.startup_id == startup_id,
            ContentItem.status == ContentStatus.PUBLISHED,
            ContentItem.published_at >= week_ago
        )
        .order_by(ContentItem.published_at.desc())
    )
    published = published_result.scalars().all()
    
    return ContentCalendarResponse(
        scheduled=[ContentResponse.model_validate(c) for c in scheduled],
        drafts=[ContentResponse.model_validate(c) for c in drafts],
        published_this_week=[ContentResponse.model_validate(c) for c in published],
    )


@router.post("/content", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    startup_id: UUID,
    content_data: ContentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new content item.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    content = ContentItem(
        startup_id=startup_id,
        title=content_data.title,
        platform=content_data.platform,
        content_type=content_data.content_type,
        body=content_data.body,
        hook=content_data.hook,
        cta=content_data.cta,
        hashtags=content_data.hashtags,
        media_urls=content_data.media_urls,
        scheduled_for=content_data.scheduled_for,
        status=ContentStatus.SCHEDULED if content_data.scheduled_for else ContentStatus.DRAFTING,
    )
    
    db.add(content)
    await db.flush()
    
    return ContentResponse.model_validate(content)


@router.post("/content/generate", response_model=GenerateContentResponse)
async def generate_content(
    startup_id: UUID,
    gen_request: GenerateContentRequest,
    current_user: User = Depends(require_credits(settings.credit_cost_content_gen, "Content generation")),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI-powered content for a platform.
    
    Costs 3 credits.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Get startup
    startup_result = await db.execute(
        select(Startup).where(Startup.id == startup_id)
    )
    startup = startup_result.scalar_one()
    
    # Use Content Agent
    from app.agents.content_agent import content_agent
    
    result = await content_agent.generate(
        platform=gen_request.platform,
        topic=gen_request.topic,
        startup_context={
            "name": startup.name,
            "description": startup.description,
            "tagline": startup.tagline,
            "industry": startup.industry,
        },
        content_type=gen_request.content_type,
        tone=gen_request.tone,
        trend_based=gen_request.trend_based,
        custom_context=gen_request.custom_context,
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Generation failed")
        )
    
    content = result.get("content", {})
    
    return GenerateContentResponse(
        title=content.get("title", ""),
        hook=content.get("hook", ""),
        body=content.get("full_body", content.get("body", "")),
        cta=content.get("cta", ""),
        hashtags=content.get("hashtags", []),
        trend_sources=result.get("trends_used"),
    )


@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    startup_id: UUID,
    content_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a content item.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(ContentItem)
        .where(ContentItem.id == content_id, ContentItem.startup_id == startup_id)
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return ContentResponse.model_validate(content)


@router.patch("/content/{content_id}", response_model=ContentResponse)
async def update_content(
    startup_id: UUID,
    content_id: UUID,
    content_update: ContentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a content item.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(ContentItem)
        .where(ContentItem.id == content_id, ContentItem.startup_id == startup_id)
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    update_data = content_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)
    
    return ContentResponse.model_validate(content)


@router.delete("/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    startup_id: UUID,
    content_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a content item.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(ContentItem)
        .where(ContentItem.id == content_id, ContentItem.startup_id == startup_id)
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    await db.delete(content)


@router.post("/content/{content_id}/publish", response_model=ContentResponse)
async def publish_content(
    startup_id: UUID,
    content_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Publish content immediately.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(ContentItem)
        .where(ContentItem.id == content_id, ContentItem.startup_id == startup_id)
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # In production, actually publish via platform APIs
    content.status = ContentStatus.PUBLISHED
    content.published_at = datetime.utcnow()
    # content.published_url = "https://..."
    
    return ContentResponse.model_validate(content)


# ==================
# Acquisition Optimizer
# ==================

@router.get("/channels", response_model=List[AcquisitionChannelResponse])
async def list_acquisition_channels(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all acquisition channels for a startup.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(AcquisitionChannel)
        .options(selectinload(AcquisitionChannel.metrics))
        .where(AcquisitionChannel.startup_id == startup_id)
        .order_by(AcquisitionChannel.created_at.desc())
    )
    channels = result.scalars().all()
    
    return [AcquisitionChannelResponse.model_validate(c) for c in channels]


@router.post("/channels", response_model=AcquisitionChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_acquisition_channel(
    startup_id: UUID,
    channel_data: AcquisitionChannelCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new acquisition channel to track.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    channel = AcquisitionChannel(
        startup_id=startup_id,
        name=channel_data.name,
        channel_type=channel_data.channel_type,
        platform=channel_data.platform,
        monthly_budget=channel_data.monthly_budget,
        settings=channel_data.settings,
    )
    
    db.add(channel)
    await db.flush()
    
    return AcquisitionChannelResponse.model_validate(channel)


@router.get("/channels/summary", response_model=List[ChannelSummaryResponse])
async def get_acquisition_summary(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get aggregated performance summary across all channels.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(AcquisitionChannel)
        .options(selectinload(AcquisitionChannel.metrics))
        .where(AcquisitionChannel.startup_id == startup_id)
    )
    channels = result.scalars().all()
    
    summary = []
    for chan in channels:
        total_leads = sum(m.leads_count for m in chan.metrics)
        total_conversions = sum(m.conversions_count for m in chan.metrics)
        total_spend = chan.total_spend
        total_revenue = sum(m.revenue for m in chan.metrics)
        
        cac = total_spend / total_leads if total_leads > 0 else 0
        roas = total_revenue / total_spend if total_spend > 0 else 0
        roi = (total_revenue - total_spend) / total_spend if total_spend > 0 else 0
        
        summary.append(ChannelSummaryResponse(
            channel_id=chan.id,
            name=chan.name,
            total_spend=total_spend,
            total_leads=total_leads,
            total_conversions=total_conversions,
            avg_cac=cac,
            avg_roas=roas,
            roi=roi
        ))
    
    return summary


@router.get("/metrics/velocity")
async def get_lead_velocity(
    startup_id: UUID,
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get Lead Velocity (New leads per day) for sparkline charts.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    from sqlalchemy import func
    from datetime import timedelta
    
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query leads grouped by day
    # Note: SQLite/Postgres syntax differs for date truncation. 
    # Using python-side aggregation for DB-agnostic safety in MVP, 
    # but Postgres 'date_trunc' is better for scale.
    
    # Efficient fetch: only created_at needed
    result = await db.execute(
        select(Lead.created_at)
        .where(
            Lead.startup_id == startup_id,
            Lead.created_at >= start_date
        )
    )
    lead_dates = result.scalars().all()
    
    # Aggregate in memory (MVP)
    daily_counts = {}
    for date in lead_dates:
        day_str = date.strftime("%Y-%m-%d")
        daily_counts[day_str] = daily_counts.get(day_str, 0) + 1
        
    # Fill missing days with 0
    velocity_data = []
    current = start_date
    now = datetime.utcnow()
    while current <= now:
        day_str = current.strftime("%Y-%m-%d")
        velocity_data.append({
            "date": day_str,
            "count": daily_counts.get(day_str, 0)
        })
        current += timedelta(days=1)
        
    return {
        "velocity": velocity_data,
        "total_period": len(lead_dates),
        "trend": "up" if len(velocity_data) > 1 and velocity_data[-1]["count"] >= velocity_data[0]["count"] else "down"
    }
