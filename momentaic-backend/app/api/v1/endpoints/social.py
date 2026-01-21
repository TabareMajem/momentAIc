
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User
from app.models.social import SocialPost, PostStatus, SocialPlatform
from app.services.social_scheduler import social_scheduler
import structlog

logger = structlog.get_logger()
router = APIRouter()

# --- Schemas ---
class SocialPostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=280) # Twitter limit style
    platforms: List[str] # ["twitter", "linkedin"]
    scheduled_at: Optional[datetime] = None # None = Now
    media_urls: List[str] = []

class SocialPostResponse(BaseModel):
    id: UUID
    content: str
    platforms: List[str]
    status: str
    scheduled_at: datetime
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Endpoints ---

@router.post("/posts", response_model=SocialPostResponse)
async def schedule_social_post(
    startup_id: UUID,
    post_data: SocialPostCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Schedule a new social post (Buffer Killer)"""
    await verify_startup_access(startup_id, current_user, db)
    
    # Default to NOW if no time provided
    scheduled_at = post_data.scheduled_at or datetime.utcnow()
    
    post = await social_scheduler.schedule_post(
        startup_id=str(startup_id),
        content=post_data.content,
        platforms=post_data.platforms,
        scheduled_at=scheduled_at
    )
    
    return post

@router.get("/posts", response_model=List[SocialPostResponse])
async def get_social_posts(
    startup_id: UUID,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get content calendar"""
    await verify_startup_access(startup_id, current_user, db)
    
    query = select(SocialPost).where(SocialPost.startup_id == startup_id)
    
    if status:
        query = query.where(SocialPost.status == status)
        
    query = query.order_by(SocialPost.scheduled_at.desc())
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    return posts

@router.post("/queue/run")
async def force_run_queue(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
):
    """
    Force run the scheduler NOW.
    Useful for 'Post Now' functionality without waiting for Cron.
    """
    background_tasks.add_task(social_scheduler.publish_due_posts)
    return {"message": "Queue execution triggered in background"}
