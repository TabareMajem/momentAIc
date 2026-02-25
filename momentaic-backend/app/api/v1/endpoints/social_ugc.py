"""
Social UGC API Endpoints
API routes for the Social Media UGC Agent System.

Endpoints for:
- Reddit Sniper (opportunity scanning, comment generation)
- Viral Campaigns (exit survey, wedding vows, stats cards)
- Discord (bot commands)
- Guerrilla Marketing (parking tickets, product mockups, wedding embeds)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User

# Import agents
from app.agents.guerrilla.reddit_sniper_agent import reddit_sniper
from app.agents.viral_campaign_agent import viral_campaign_agent
from app.agents.guerrilla.discord_agent import discord_dispute_bot, DisputeContext
from app.agents.guerrilla.guerrilla_campaign_agent import guerrilla_campaign_agent

import structlog

logger = structlog.get_logger()
router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

# --- Reddit Schemas ---
class RedditScanRequest(BaseModel):
    keywords: List[str] = Field(default=[], description="Additional keywords to scan for")
    limit: int = Field(default=5, ge=1, le=10)


class RedditCommentRequest(BaseModel):
    thread_title: str
    thread_url: str
    subreddit: str
    pain_point: str
    gamification_angle: str


class BreakthroughStoryRequest(BaseModel):
    theme: str = Field(default="communication", description="communication, intimacy, boredom, money")
    age_range: str = Field(default="28M/26F")


# --- Viral Campaign Schemas ---
class ExitSurveyRequest(BaseModel):
    tone: str = Field(default="playful", description="playful, serious, sarcastic")
    categories: List[str] = Field(default=["Communication", "Intimacy", "Humor"])


class WeddingVowsRequest(BaseModel):
    partner_name: str
    style: str = Field(default="gamer", description="gamer, romantic, funny, nerdy")
    bond_stats: Dict[str, Any] = Field(default={}, description="Relationship facts")


class StatsCardRequest(BaseModel):
    user_data: Dict[str, Any] = Field(description="User relationship data")
    visual_style: str = Field(default="nano_banana")


# --- Discord Schemas ---
class DiscordSettleRequest(BaseModel):
    channel_id: str
    guild_id: str
    user1_id: str
    user2_id: str
    dispute_topic: Optional[str] = None


class DiscordPollRequest(BaseModel):
    channel_id: str
    guild_id: str
    user1_id: str
    user2_id: str
    question: str


# --- Guerrilla Schemas ---
class ProductMockupRequest(BaseModel):
    product_type: str = Field(default="starter_pack")
    style: str = Field(default="nano_banana")
    target_store: str = Field(default="Target")


class ParkingTicketRequest(BaseModel):
    violation_type: str = Field(default="missing_date_night")
    severity: str = Field(default="medium")


class WeddingEmbedRequest(BaseModel):
    partner1_name: str
    partner2_name: str
    how_they_met: str
    fun_facts: List[str] = []
    question_count: int = Field(default=5, ge=3, le=10)


# ═══════════════════════════════════════════════════════════════════════════════
# REDDIT SNIPER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/reddit/scan-opportunities")
async def scan_reddit_opportunities(
    startup_id: UUID,
    request: RedditScanRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Scan Reddit for high-intent relationship threads.
    Returns opportunities with gamification angles.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    opportunities = await reddit_sniper.find_relationship_opportunities(
        limit=request.limit
    )
    
    return {
        "opportunities": [
            opp.model_dump() if hasattr(opp, 'model_dump') else opp.__dict__ 
            for opp in opportunities
        ],
        "count": len(opportunities),
        "scanned_at": datetime.utcnow().isoformat(),
    }


@router.post("/reddit/generate-comment")
async def generate_reddit_comment(
    startup_id: UUID,
    request: RedditCommentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a value-first comment for a specific Reddit thread.
    Returns draft comment ready for review.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Get startup context
    from sqlalchemy import select
    from app.models.startup import Startup
    result = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = result.scalar_one_or_none()
    
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    from app.agents.guerrilla.reddit_sniper_agent import RelationshipThread
    
    thread = RelationshipThread(
        title=request.thread_title,
        url=request.thread_url,
        subreddit=request.subreddit,
        pain_point=request.pain_point,
        gamification_angle=request.gamification_angle,
        engagement_score=8,
    )
    
    comment = await reddit_sniper.draft_value_first_comment(
        thread=thread,
        product_context={
            "name": startup.name,
            "description": startup.description,
        }
    )
    
    return comment


@router.post("/reddit/generate-breakthrough-story")
async def generate_breakthrough_story(
    startup_id: UUID,
    request: BreakthroughStoryRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an UPDATE-style Reddit success story.
    Returns full post content with follow-up comment reply.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    from sqlalchemy import select
    from app.models.startup import Startup
    result = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = result.scalar_one_or_none()
    
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    story = await reddit_sniper.generate_breakthrough_story(
        theme=request.theme,
        product_context={
            "name": startup.name,
            "description": startup.description,
        },
        age_range=request.age_range,
    )
    
    return {
        "title": story.title,
        "post": story.full_post,
        "comment_reply": story.product_mention,
        "theme": request.theme,
    }


@router.post("/reddit/run-campaign")
async def run_reddit_campaign(
    startup_id: UUID,
    stories_count: int = 2,
    comments_count: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Run a complete Reddit Sniper campaign.
    Generates stories, comments, and red flag receipts.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    from sqlalchemy import select
    from app.models.startup import Startup
    result = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = result.scalar_one_or_none()
    
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    results = await reddit_sniper.run_sniper_campaign(
        product_context={
            "name": startup.name,
            "description": startup.description,
        },
        stories_count=stories_count,
        comments_count=comments_count,
    )
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# VIRAL CAMPAIGN ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/viral/exit-survey")
async def generate_exit_survey(
    request: ExitSurveyRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate content for the "Exit Survey" viral microgame.
    Returns questions, results categories, and shareable text.
    """
    content = await viral_campaign_agent.generate_exit_survey_content(
        tone=request.tone,
        include_categories=request.categories,
    )
    
    return content.model_dump() if hasattr(content, 'model_dump') else content.__dict__


@router.post("/viral/wedding-vows")
async def generate_wedding_vows(
    request: WeddingVowsRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate gamified wedding vows based on bond stats.
    Returns personalized vow content with gaming references.
    """
    vow = await viral_campaign_agent.generate_wedding_vows(
        bond_stats=request.bond_stats,
        style=request.style,
        partner_name=request.partner_name,
    )
    
    return vow.model_dump() if hasattr(vow, 'model_dump') else vow.__dict__


@router.post("/viral/relationship-stats")
async def generate_relationship_stats(
    request: StatsCardRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate a shareable relationship stats card.
    Returns character sheet style data ready for visualization.
    """
    card = await viral_campaign_agent.generate_relationship_stats_card(
        user_data=request.user_data,
        visual_style=request.visual_style,
    )
    
    return card.model_dump() if hasattr(card, 'model_dump') else card.__dict__


@router.post("/viral/generate-batch")
async def generate_campaign_batch(
    campaign_type: str,
    variations: int = 3,
    current_user: User = Depends(get_current_active_user),
    **kwargs,
):
    """
    Generate multiple variations of a campaign type.
    """
    assets = await viral_campaign_agent.generate_campaign_assets(
        campaign_type=campaign_type,
        variations=variations,
        **kwargs,
    )
    
    return {"assets": assets, "count": len(assets)}


# ═══════════════════════════════════════════════════════════════════════════════
# DISCORD ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/discord/settle-dispute")
async def handle_settle_dispute(
    request: DiscordSettleRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Handle "@BondJudge settle this" command.
    Returns message content and game links.
    """
    context = DisputeContext(
        channel_id=request.channel_id,
        guild_id=request.guild_id,
        user1_id=request.user1_id,
        user2_id=request.user2_id,
        dispute_topic=request.dispute_topic,
    )
    
    response = await discord_dispute_bot.handle_settle_command(context)
    return response


@router.post("/discord/whos-right")
async def handle_whos_right(
    request: DiscordPollRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Handle "@BondJudge who's right" poll command.
    Returns poll message with reaction options.
    """
    context = DisputeContext(
        channel_id=request.channel_id,
        guild_id=request.guild_id,
        user1_id=request.user1_id,
        user2_id=request.user2_id,
    )
    
    response = await discord_dispute_bot.handle_whos_right_command(
        context=context,
        question=request.question,
    )
    return response


@router.post("/discord/rate-us")
async def handle_rate_us(
    request: DiscordSettleRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Handle "@BondJudge rate us" mini-game command.
    Returns compatibility check game content.
    """
    context = DisputeContext(
        channel_id=request.channel_id,
        guild_id=request.guild_id,
        user1_id=request.user1_id,
        user2_id=request.user2_id,
    )
    
    response = await discord_dispute_bot.handle_rate_us_command(context)
    return response


@router.get("/discord/bot-invite")
async def get_bot_invite_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get BondJudge bot invite information and marketing content.
    """
    return discord_dispute_bot.get_bot_invite_content()


# ═══════════════════════════════════════════════════════════════════════════════
# GUERRILLA CAMPAIGN ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/guerrilla/product-mockup")
async def generate_product_mockup(
    request: ProductMockupRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate concept for a fake product mockup.
    Returns box design specs and Reddit caption.
    """
    concept = await guerrilla_campaign_agent.generate_product_mockup_concept(
        product_type=request.product_type,
        style=request.style,
        target_store=request.target_store,
    )
    
    return concept.model_dump() if hasattr(concept, 'model_dump') else concept.__dict__


@router.post("/guerrilla/parking-ticket")
async def generate_parking_ticket(
    request: ParkingTicketRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate a relationship parking ticket.
    Returns printable citation content.
    """
    ticket = await guerrilla_campaign_agent.generate_parking_ticket(
        violation_type=request.violation_type,
        severity=request.severity,
    )
    
    return ticket.model_dump() if hasattr(ticket, 'model_dump') else ticket.__dict__


@router.post("/guerrilla/parking-tickets-batch")
async def generate_parking_ticket_batch(
    count: int = 5,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate a batch of varied parking tickets for printing.
    """
    tickets = await guerrilla_campaign_agent.generate_ticket_batch(count=count)
    
    return {
        "tickets": [
            t.model_dump() if hasattr(t, 'model_dump') else t.__dict__ 
            for t in tickets
        ],
        "count": len(tickets),
    }


@router.post("/guerrilla/wedding-embed")
async def generate_wedding_embed(
    request: WeddingEmbedRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate embeddable "Know the Couple" game for wedding websites.
    Returns questions, result messages, and embed code.
    """
    embed = await guerrilla_campaign_agent.generate_wedding_embed(
        couple_data={
            "partner1_name": request.partner1_name,
            "partner2_name": request.partner2_name,
            "how_they_met": request.how_they_met,
            "fun_facts": request.fun_facts,
        },
        question_count=request.question_count,
    )
    
    return embed.model_dump() if hasattr(embed, 'model_dump') else embed.__dict__


@router.get("/guerrilla/wedding-embed-guide")
async def get_wedding_embed_guide(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get installation guide for wedding website embed.
    """
@router.post("/guerrilla/batch-generate")
async def batch_generate_assets(
    asset_type: str,
    count: int = 5,
    visual_style: str = "nano_banana",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a BATCH of visual assets (Concepts + Images).
    This triggers the Asset Factory to create actual DALL-E generated images.
    
    WARNING: This consumes OpenAI credits.
    """
    from app.agents.guerrilla.asset_factory_agent import asset_factory_agent
    
    results = await asset_factory_agent.generate_batch(
        asset_type=asset_type,
        count=count,
        visual_style=visual_style
    )
    
    # Optional: Save to DB or Gallery here
    
    return {
        "count": len(results),
        "assets": [
            {
                "type": res.asset_type,
                "image_url": res.image_url,
                "concept": res.concept,
                "status": res.status
            } 
            for res in results
        ]
    }
