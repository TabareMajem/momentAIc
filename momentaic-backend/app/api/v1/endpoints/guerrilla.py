from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
import structlog
from app.agents.marketing_agent import marketing_agent
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()
logger = structlog.get_logger()

class ScanRequest(BaseModel):
    platform: str
    keywords: str

@router.post("/scan")
async def scan_opportunities(
    request: ScanRequest,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Trigger a guerrilla marketing scan for opportunities.
    """
    logger.info("Guerrilla Scan Request", platform=request.platform, user_id=str(current_user.id))
    
    try:
        results = await marketing_agent.scan_opportunities(
            platform=request.platform, 
            keywords=request.keywords
        )
        return results
    except Exception as e:
        logger.error("Scan endpoint failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
