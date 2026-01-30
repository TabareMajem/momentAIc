"""
Magic URL Endpoint - The Single Most Powerful Endpoint
One URL → Full Analysis → Instant Action

Part of Project PHOENIX
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
import structlog

logger = structlog.get_logger()

router = APIRouter()


class MagicURLRequest(BaseModel):
    url: str
    auto_execute: bool = False  # If True, schedule posts immediately


class MagicURLResponse(BaseModel):
    success: bool
    startup_id: Optional[str] = None
    analysis: Dict[str, Any]
    posts_scheduled: int = 0
    leads_icp: Optional[str] = None
    experiment: Optional[Dict[str, Any]] = None
    message: str


@router.post("/magic", response_model=MagicURLResponse)
async def magic_url_onboarding(
    request: MagicURLRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    🪄 THE MAGIC URL ENDPOINT
    
    Input: A single URL
    Output: Full growth strategy + scheduled posts + leads ICP + experiment
    
    This is the "paste URL, get users" experience.
    """
    from app.agents.browser_agent import browser_agent
    from app.agents.growth_hacker_agent import growth_hacker_agent
    from app.agents.onboarding_genius import onboarding_genius
    from app.models.startup import Startup, StartupStage
    from app.triggers.default_triggers import create_default_triggers
    
    logger.info("Magic URL: Starting analysis", url=request.url, user_id=str(current_user.id))
    
    try:
        # === STEP 1: SCRAPE THE URL ===
        logger.info("Magic URL: Scraping website...")
        scraped = await browser_agent.scrape_url(request.url)
        scraped_content = scraped.get("content", "") if isinstance(scraped, dict) else str(scraped)
        page_title = scraped.get("title", "My Startup") if isinstance(scraped, dict) else "My Startup"
        
        if not scraped_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not scrape URL content. Please check the URL is accessible."
            )
        
        # === STEP 2: AI ANALYSIS ===
        logger.info("Magic URL: Running AI analysis...")
        strategy = await growth_hacker_agent.analyze_startup_wizard(
            url=request.url,
            description=scraped_content[:5000]
        )
        
        if "error" in strategy:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {strategy['error']}"
            )
        
        # === STEP 3: CREATE STARTUP IF NEEDED ===
        # Check if startup with this URL already exists
        from sqlalchemy import select
        result = await db.execute(
            select(Startup).where(
                Startup.owner_id == current_user.id,
                Startup.website_url == request.url
            )
        )
        startup = result.scalar_one_or_none()
        
        if not startup:
            # Create new startup
            startup = Startup(
                owner_id=current_user.id,
                name=page_title[:100],
                description=strategy.get("value_prop", ""),
                industry="Technology",  # Could be inferred from strategy
                stage=StartupStage.MVP,
                website_url=request.url,
                metrics={},
            )
            db.add(startup)
            await db.flush()
            
            # Create default triggers
            await create_default_triggers(db, startup.id, current_user.id)
            logger.info("Magic URL: Created new startup", startup_id=str(startup.id))
        
        # === STEP 4: GENERATE & SCHEDULE POSTS ===
        posts_scheduled = 0
        
        if request.auto_execute:
            from app.services.social_scheduler import social_scheduler
            from app.agents.marketing_agent import marketing_agent
            from datetime import datetime, timedelta
            
            # Generate 3 posts
            platforms = ["twitter", "linkedin"]
            hook = strategy.get("viral_post_hook", "")
            audience = strategy.get("target_audience", "")
            
            for i, platform in enumerate(platforms):
                try:
                    content = await marketing_agent.create_social_post(
                        context=f"Target: {audience}. Hook: {hook}. Platform: {platform}. Goal: Viral Launch.",
                        platform=platform
                    )
                    
                    scheduled_time = datetime.utcnow() + timedelta(hours=i * 24 + 2)
                    await social_scheduler.schedule_post(
                        startup_id=str(startup.id),
                        content=content,
                        platforms=[platform],
                        scheduled_at=scheduled_time
                    )
                    posts_scheduled += 1
                except Exception as e:
                    logger.warning(f"Failed to schedule {platform} post", error=str(e))
        
        await db.commit()
        
        return MagicURLResponse(
            success=True,
            startup_id=str(startup.id),
            analysis=strategy,
            posts_scheduled=posts_scheduled,
            leads_icp=strategy.get("target_audience"),
            experiment={
                "name": "First Week Launch",
                "hypothesis": f"Posting about {strategy.get('pain_point', 'the problem')} will attract early adopters",
                "metric": strategy.get("weekly_goal", "10 signups")
            },
            message=f"🪄 Magic complete! {'Posts scheduled.' if posts_scheduled > 0 else 'Ready to execute.'}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Magic URL failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Magic failed: {str(e)}"
        )
