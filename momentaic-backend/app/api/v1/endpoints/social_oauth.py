"""
Social OAuth Endpoints
Handles OAuth flows for Twitter, LinkedIn, Instagram
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.integration import Integration, IntegrationProvider, IntegrationStatus
from app.services.social.twitter import twitter_service
from app.services.social.linkedin import linkedin_service

logger = structlog.get_logger()
router = APIRouter()

# In-memory store for OAuth state (in production, use Redis)
oauth_state_store = {}

# ================
# TWITTER
# ================

@router.get("/connect/twitter")
async def connect_twitter(
    startup_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Initiate Twitter OAuth flow.
    Returns the authorization URL to redirect the user to.
    """
    auth_data = twitter_service.generate_auth_url()
    
    # Store state -> code_verifier mapping (needed for PKCE)
    oauth_state_store[auth_data["state"]] = {
        "code_verifier": auth_data["code_verifier"],
        "user_id": str(current_user.id),
        "startup_id": startup_id,
        "platform": "twitter"
    }
    
    return {"auth_url": auth_data["auth_url"]}


@router.get("/callback/twitter")
async def twitter_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Twitter OAuth callback. Exchanges code for tokens and stores them.
    """
    # Retrieve state data
    state_data = oauth_state_store.pop(state, None)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    
    code_verifier = state_data["code_verifier"]
    user_id = state_data["user_id"]
    startup_id = state_data["startup_id"]
    
    # Exchange code for tokens
    tokens = await twitter_service.exchange_code_for_tokens(code, code_verifier)
    
    if "error" in tokens:
        raise HTTPException(status_code=400, detail=tokens["error"])
    
    # Store in database
    integration = Integration(
        user_id=user_id,
        startup_id=startup_id,
        provider=IntegrationProvider.TWITTER,
        name="Twitter",
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        status=IntegrationStatus.ACTIVE,
        scopes=tokens.get("scope", "").split(" "),
    )
    
    db.add(integration)
    await db.commit()
    
    logger.info("Twitter connected successfully", user_id=user_id)
    
    # Redirect back to frontend
    return RedirectResponse(url="/#/integrations?connected=twitter")


# ================
# LINKEDIN
# ================

@router.get("/connect/linkedin")
async def connect_linkedin(
    startup_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Initiate LinkedIn OAuth flow.
    """
    auth_data = linkedin_service.generate_auth_url()
    
    oauth_state_store[auth_data["state"]] = {
        "user_id": str(current_user.id),
        "startup_id": startup_id,
        "platform": "linkedin"
    }
    
    return {"auth_url": auth_data["auth_url"]}


@router.get("/callback/linkedin")
async def linkedin_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """
    LinkedIn OAuth callback.
    """
    state_data = oauth_state_store.pop(state, None)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    
    user_id = state_data["user_id"]
    startup_id = state_data["startup_id"]
    
    # Exchange code for tokens
    tokens = await linkedin_service.exchange_code_for_tokens(code)
    
    if "error" in tokens:
        raise HTTPException(status_code=400, detail=tokens["error"])
    
    # Get user profile to store URN
    profile = await linkedin_service.get_user_profile(tokens["access_token"])
    user_urn = f"urn:li:person:{profile.get('sub', 'unknown')}"
    
    integration = Integration(
        user_id=user_id,
        startup_id=startup_id,
        provider=IntegrationProvider.LINKEDIN,
        name="LinkedIn",
        access_token=tokens["access_token"],
        status=IntegrationStatus.ACTIVE,
        config={"user_urn": user_urn},
    )
    
    db.add(integration)
    await db.commit()
    
    logger.info("LinkedIn connected successfully", user_id=user_id)
    
    return RedirectResponse(url="/#/integrations?connected=linkedin")
