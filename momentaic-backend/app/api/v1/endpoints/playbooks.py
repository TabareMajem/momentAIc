"""
Industry Playbook Endpoints
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.playbook_service import playbook_service

router = APIRouter()

@router.get("", response_model=List[Dict[str, Any]])
async def get_industry_playbooks(
    industry: str = Query(..., description="The industry of the startup"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get pre-configured agent playbooks tailored to a specific industry.
    These are used for quick 1-click activation in the Agent Studio.
    """
    playbooks = playbook_service.get_playbooks_for_industry(industry)
    return playbooks
