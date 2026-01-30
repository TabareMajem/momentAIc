from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.startup import Startup

router = APIRouter()

class UserContentRequest(BaseModel):
    startup_id: UUID
    
class StrategyResponse(BaseModel):
    result: dict

@router.post("/nano-bananas")
async def generate_user_content(
    request: UserContentRequest, 
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate 'Nano Bananas' style content for a specific user startup.
    Requires the startup to be owned by the user.
    """
    # 1. Fetch Startup
    result = await db.execute(select(Startup).where(Startup.id == request.startup_id, Startup.owner_id == current_user.id))
    startup = result.scalars().first()
    
    if not startup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found or access denied."
        )
        
    # 2. Call Agent
    from app.agents.empire_strategist import empire_strategist
    
    startup_context = {
        "name": startup.name,
        "description": startup.description or f"A startup in the {startup.industry} industry."
    }
    
    return await empire_strategist.generate_nano_bananas_content(
        product_name=startup.name,
        startup_context=startup_context
    )

@router.post("/surprise-me")
async def generate_user_strategy(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a synergistic GTM strategy for ALL of the user's startups.
    User must have at least one startup.
    """
    # 1. Fetch User's Startups
    result = await db.execute(select(Startup).where(Startup.owner_id == current_user.id))
    startups = result.scalars().all()
    
    if not startups:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need at least one startup to generate an ecosystem strategy."
        )
        
    # 2. Prepare Context
    products_context = [
        {"name": s.name, "desc": s.description or f"{s.industry} startup"}
        for s in startups
    ]
    
    # 3. Call Agent
    from app.agents.empire_strategist import empire_strategist
    return await empire_strategist.surprise_me_strategy(products_context=products_context)
