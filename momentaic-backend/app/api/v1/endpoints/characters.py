"""
AI Character Factory API Endpoints
CRUD for characters, content generation, visual identity, UGC video, analytics.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User
from app.models.character import (
    Character, CharacterContent,
    CharacterStatus, CharacterContentStatus,
)
from app.services.character_factory import character_factory

import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/characters", tags=["AI Character Factory"])


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class CharacterCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    target_audience: str = Field(..., description="Who this character speaks to")
    brand_personality: str = Field(..., description="Personality traits, comma-separated")
    visual_direction: str = Field(default="", description="Style guide for visuals")
    voice_direction: str = Field(default="", description="Voice style direction")
    platform_focus: str = Field(default="tiktok,instagram", description="Comma-separated platforms")
    product_to_promote: str = Field(default="", description="Product/service to promote")


class CharacterUpdateRequest(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    persona: Optional[Dict[str, Any]] = None
    platforms: Optional[Dict[str, Any]] = None
    funnel_config: Optional[Dict[str, Any]] = None
    content_rules: Optional[Dict[str, Any]] = None
    autonomy_level: Optional[str] = None
    daily_budget_usd: Optional[float] = None
    monthly_budget_usd: Optional[float] = None


class GenerateContentRequest(BaseModel):
    platform: str = Field(default="tiktok", description="Target platform")
    funnel_stage: str = Field(default="awareness", description="AIDA funnel stage")
    script: str = Field(default="", description="Optional: custom script override")


class GenerateVisualsRequest(BaseModel):
    num_scenes: int = Field(default=6, ge=1, le=12, description="Number of scene images to generate")


class CharacterResponse(BaseModel):
    id: UUID
    startup_id: UUID
    name: str
    handle: Optional[str]
    tagline: Optional[str]
    persona: Dict[str, Any]
    visual_identity: Dict[str, Any]
    voice_identity: Optional[Dict[str, Any]]
    character_dna: Optional[str]
    platforms: Dict[str, Any]
    funnel_config: Optional[Dict[str, Any]]
    content_rules: Optional[Dict[str, Any]]
    performance_metrics: Optional[Dict[str, Any]]
    status: str
    autonomy_level: str
    daily_budget_usd: Optional[float]
    monthly_budget_usd: Optional[float]
    total_spent_usd: float
    created_at: datetime

    class Config:
        from_attributes = True


class ContentResponse(BaseModel):
    id: UUID
    character_id: UUID
    platform: str
    content_type: str
    content_data: Dict[str, Any]
    generation_pipeline: Optional[Dict[str, Any]]
    status: str
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    funnel_stage: Optional[str]
    engagement_metrics: Optional[Dict[str, Any]]
    cost_usd: float
    virality_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/{startup_id}", response_model=CharacterResponse, status_code=201)
async def create_character(
    startup_id: UUID,
    request: CharacterCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new AI virtual influencer character."""
    await verify_startup_access(startup_id, current_user, db)

    character = await character_factory.create_character(
        db=db,
        startup_id=str(startup_id),
        name=request.name,
        target_audience=request.target_audience,
        brand_personality=request.brand_personality,
        visual_direction=request.visual_direction,
        voice_direction=request.voice_direction,
        platform_focus=request.platform_focus,
        product_to_promote=request.product_to_promote,
    )
    return character


@router.get("/{startup_id}", response_model=List[CharacterResponse])
async def list_characters(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all characters for a startup."""
    await verify_startup_access(startup_id, current_user, db)
    characters = await character_factory.list_characters(db, str(startup_id))
    return characters


@router.get("/{startup_id}/{character_id}", response_model=CharacterResponse)
async def get_character(
    startup_id: UUID,
    character_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get character details including DNA."""
    await verify_startup_access(startup_id, current_user, db)
    character = await character_factory.get_character(db, str(character_id))
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.put("/{startup_id}/{character_id}", response_model=CharacterResponse)
async def update_character(
    startup_id: UUID,
    character_id: UUID,
    request: CharacterUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update character configuration."""
    await verify_startup_access(startup_id, current_user, db)
    updates = {k: v for k, v in request.model_dump().items() if v is not None}
    character = await character_factory.update_character(db, str(character_id), updates)
    return character


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER LIFECYCLE
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/{startup_id}/{character_id}/activate", response_model=CharacterResponse)
async def activate_character(
    startup_id: UUID,
    character_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Activate a character — start autonomous content generation."""
    await verify_startup_access(startup_id, current_user, db)
    character = await character_factory.activate_character(db, str(character_id))
    return character


@router.post("/{startup_id}/{character_id}/pause", response_model=CharacterResponse)
async def pause_character(
    startup_id: UUID,
    character_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Pause a character — stop content generation."""
    await verify_startup_access(startup_id, current_user, db)
    character = await character_factory.pause_character(db, str(character_id))
    return character


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/{startup_id}/{character_id}/generate-content")
async def generate_content(
    startup_id: UUID,
    character_id: UUID,
    request: GenerateContentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger manual content generation for a character."""
    await verify_startup_access(startup_id, current_user, db)

    result = await character_factory.generate_ugc_video(
        db=db,
        character_id=str(character_id),
        script=request.script,
        platform=request.platform,
        funnel_stage=request.funnel_stage,
    )
    return result


@router.post("/{startup_id}/{character_id}/generate-visuals")
async def generate_visuals(
    startup_id: UUID,
    character_id: UUID,
    request: GenerateVisualsRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate visual identity images for a character."""
    await verify_startup_access(startup_id, current_user, db)

    result = await character_factory.generate_character_visuals(
        db=db,
        character_id=str(character_id),
        num_scenes=request.num_scenes,
    )
    return result


@router.post("/{startup_id}/{character_id}/generate-video")
async def generate_video(
    startup_id: UUID,
    character_id: UUID,
    request: GenerateContentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a ChatCut-style UGC video for a character."""
    await verify_startup_access(startup_id, current_user, db)

    result = await character_factory.generate_ugc_video(
        db=db,
        character_id=str(character_id),
        script=request.script,
        platform=request.platform,
        funnel_stage=request.funnel_stage,
    )
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT FEED & ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/{startup_id}/{character_id}/content", response_model=List[ContentResponse])
async def get_character_content(
    startup_id: UUID,
    character_id: UUID,
    platform: Optional[str] = None,
    content_status: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get content feed for a character."""
    await verify_startup_access(startup_id, current_user, db)
    content = await character_factory.get_character_content(
        db=db,
        character_id=str(character_id),
        platform=platform,
        status=content_status,
        limit=limit,
    )
    return content


@router.get("/{startup_id}/{character_id}/analytics")
async def get_character_analytics(
    startup_id: UUID,
    character_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get performance analytics for a character."""
    await verify_startup_access(startup_id, current_user, db)
    analytics = await character_factory.get_character_analytics(db, str(character_id))
    if not analytics:
        raise HTTPException(status_code=404, detail="Character not found")
    return analytics


# ═══════════════════════════════════════════════════════════════════════════════
# VIRAL GROWTH ENGINE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/{startup_id}/trends/{platform}")
async def get_trending_content(
    startup_id: UUID,
    platform: str,
    industry: str = "general",
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get trending content for a platform."""
    await verify_startup_access(startup_id, current_user, db)

    from app.services.viral_growth_engine import viral_growth_engine
    trends = await viral_growth_engine.detect_trending_content(
        platform=platform,
        industry=industry,
        limit=limit,
    )
    return {"platform": platform, "trends": trends}


@router.post("/{startup_id}/{character_id}/score-virality")
async def score_content_virality(
    startup_id: UUID,
    character_id: UUID,
    content: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Score content virality before posting."""
    await verify_startup_access(startup_id, current_user, db)

    from app.services.viral_growth_engine import viral_growth_engine
    score = await viral_growth_engine.score_virality(content)
    return score
