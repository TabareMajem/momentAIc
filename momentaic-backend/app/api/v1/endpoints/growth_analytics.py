from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.growth import EmpireProgress
from app.schemas.growth import EmpireStatus, EmpireStepUpdate

router = APIRouter()

@router.get("/empire-status", response_model=EmpireStatus)
async def get_empire_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current user's progress in the Empire Builder flow.
    If no record exists, create one starting at step 0.
    """
    query = select(EmpireProgress).where(EmpireProgress.user_id == current_user.id)
    result = await db.execute(query)
    progress = result.scalar_one_or_none()
    
    if not progress:
        progress = EmpireProgress(user_id=current_user.id, current_step=0, step_data={})
        db.add(progress)
        await db.commit()
        await db.refresh(progress)
        
    return progress

@router.post("/empire-step", response_model=EmpireStatus)
async def update_empire_step(
    update: EmpireStepUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the user's current empire builder step and metadata.
    """
    query = select(EmpireProgress).where(EmpireProgress.user_id == current_user.id)
    result = await db.execute(query)
    progress = result.scalar_one_or_none()
    
    if not progress:
        progress = EmpireProgress(user_id=current_user.id, step_data={})
        db.add(progress)
    
    progress.current_step = update.step
    
    # Update metadata
    current_data = dict(progress.step_data or {})
    current_data.update(update.metadata)
    progress.step_data = current_data
    
    if update.complete:
        progress.completed_at = datetime.utcnow()
        
    await db.commit()
    await db.refresh(progress)
    return progress
