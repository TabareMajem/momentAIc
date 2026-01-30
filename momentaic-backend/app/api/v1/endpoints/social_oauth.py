"""
Social OAuth Endpoints
Handles OAuth flows for Twitter, LinkedIn, Instagram
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import json
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.redis_client import redis_client
from app.models.user import User
from app.models.integration import Integration, IntegrationProvider, IntegrationStatus
from app.services.social.twitter import twitter_service
from app.services.social.linkedin import linkedin_service

logger = structlog.get_logger()
router = APIRouter()

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
    
    # Store state -> code_verifier mapping in Redis (TTL 10 mins)
    state_data = {
        "code_verifier": auth_data["code_verifier"],
        "user_id": str(current_user.id),
        "startup_id": startup_id,
        "platform": "twitter"
    }
    await redis_client.setex(
        f"oauth:{auth_data['state']}",
        600,
        json.dumps(state_data)
    )
    
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
    # Retrieve state data from Redis
    state_json = await redis_client.get(f"oauth:{state}")
    if not state_json:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    
    state_data = json.loads(state_json)
    # Cleanup state
    await redis_client.delete(f"oauth:{state}")
    
    code_verifier = state_data["code_verifier"]
    user_id = state_data["user_id"]
    startup_id = state_data["startup_id"]
    
    # Exchange code for tokens
    tokens = await twitter_service.exchange_code_for_tokens(code, code_verifier)
    
    if "error" in tokens:
        raise HTTPException(status_code=400, detail=tokens["error"])
    
    # Store in database
    existing = await db.execute(
        select(Integration).where(
            Integration.startup_id == startup_id,
            Integration.provider == IntegrationProvider.TWITTER
        )
    )
    integration = existing.scalar_one_or_none()
    
    if integration:
        # Update existing
        integration.access_token = tokens["access_token"]
        integration.refresh_token = tokens.get("refresh_token")
        integration.status = IntegrationStatus.ACTIVE
        integration.scopes = tokens.get("scope", "").split(" ")
    else:
        # Create new
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
    
    state_data = {
        "user_id": str(current_user.id),
        "startup_id": startup_id,
        "platform": "linkedin"
    }
    await redis_client.setex(
        f"oauth:{auth_data['state']}",
        600,
        json.dumps(state_data)
    )
    
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
    state_json = await redis_client.get(f"oauth:{state}")
    if not state_json:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    
    state_data = json.loads(state_json)
    await redis_client.delete(f"oauth:{state}")
    
    user_id = state_data["user_id"]
    startup_id = state_data["startup_id"]
    
    # Exchange code for tokens
    tokens = await linkedin_service.exchange_code_for_tokens(code)
    
    if "error" in tokens:
        raise HTTPException(status_code=400, detail=tokens["error"])
    
    # Get user profile to store URN
    profile = await linkedin_service.get_user_profile(tokens["access_token"])
    user_urn = f"urn:li:person:{profile.get('sub', 'unknown')}"
    
    existing = await db.execute(
        select(Integration).where(
            Integration.startup_id == startup_id,
            Integration.provider == IntegrationProvider.LINKEDIN
        )
    )
    integration = existing.scalar_one_or_none()
    
    if integration:
        integration.access_token = tokens["access_token"]
        integration.status = IntegrationStatus.ACTIVE
        integration.config = {"user_urn": user_urn}
    else:
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
