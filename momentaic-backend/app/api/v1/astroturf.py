from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.astroturf import AstroTurfMention, MentionStatus
from app.core.security import get_current_user

router = APIRouter()

@router.get("/mentions")
async def get_mentions(
    startup_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = select(AstroTurfMention).where(
        AstroTurfMention.startup_id == startup_id
    ).order_by(AstroTurfMention.created_at.desc()).limit(50)
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/mentions/{mention_id}/deploy")
async def deploy_mention(
    mention_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    mention = await db.get(AstroTurfMention, mention_id)
    if not mention:
        raise HTTPException(status_code=404, detail="Mention not found")
        
    mention.status = MentionStatus.DEPLOYED
    await db.commit()
    return {"status": "deployed", "mention_id": str(mention.id)}

@router.post("/mentions/{mention_id}/dismiss")
async def dismiss_mention(
    mention_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    mention = await db.get(AstroTurfMention, mention_id)
    if not mention:
        raise HTTPException(status_code=404, detail="Mention not found")
        
    mention.status = MentionStatus.DISMISSED
    await db.commit()
    return {"status": "dismissed", "mention_id": str(mention.id)}
