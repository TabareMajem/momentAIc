"""
Content Loop API
Triggers for the Infinite Content Loop (Nolan & Manga).
"""

from fastapi import APIRouter, Depends
from app.core.security import get_current_active_user
from app.models.user import User
from app.agents.nolan_agent import nolan_agent
from app.agents.manga_agent import manga_agent
from pydantic import BaseModel

router = APIRouter()

class ReactRequest(BaseModel):
    text: str

@router.post("/nolan/daily")
async def trigger_nolan_daily(
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger Nolan Pro's Daily News Vector.
    """
    # Check connection
    prefs = current_user.preferences or {}
    connection = prefs.get("integrations", {}).get("symbiotask", {})
    user_email = connection.get("email")
    
    if not user_email or not connection.get("connected"):
        return {
            "success": False, 
            "error": "Not Connected",
            "message": "Please connect your Symbiotask account to use Nolan Pro Video."
        }

    return await nolan_agent.run_daily_news_cycle(user_email=user_email)

@router.post("/manga/react")
async def trigger_manga_reaction(
    request: ReactRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger Manga Magic's Reaction Engine.
    """
    # Check connection
    prefs = current_user.preferences or {}
    connection = prefs.get("integrations", {}).get("mangaka", {})
    user_email = connection.get("email")
    
    if not user_email or not connection.get("connected"):
        return {
             "success": False,
             "error": "Not Connected", 
             "message": "Please connect your Mangaka account."
        }

    return await manga_agent.generate_reaction_panel(request.text, user_email=user_email)
