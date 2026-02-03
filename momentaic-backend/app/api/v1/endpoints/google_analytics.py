"""
Google Analytics OAuth Integration
OAuth2 flow for connecting GA4 to enable proactive analytics
"""

import json
import secrets
from datetime import datetime
from typing import Optional
from uuid import UUID
import structlog

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
from app.models.startup import Startup
from app.models.integration import Integration

router = APIRouter()
logger = structlog.get_logger()

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Required scopes for GA4 Data API
GA4_SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
]


@router.get("/oauth/google-analytics/init")
async def init_ga_oauth(
    startup_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Initialize Google Analytics OAuth flow.
    Returns the authorization URL for the user to visit.
    """
    # Verify startup access
    result = await db.execute(
        select(Startup).where(Startup.id == startup_id, Startup.owner_id == current_user.id)
    )
    startup = result.scalar_one_or_none()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    # Check if Google OAuth is configured
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=501,
            detail="Google OAuth not configured. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to environment."
        )
    
    # Generate state token for CSRF protection
    state = f"{startup_id}:{secrets.token_urlsafe(16)}"
    
    # Build authorization URL
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": f"{settings.backend_url}/api/v1/integrations/oauth/google-analytics/callback",
        "response_type": "code",
        "scope": " ".join(GA4_SCOPES),
        "access_type": "offline",  # Get refresh token
        "prompt": "consent",  # Force consent screen to get refresh token
        "state": state,
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    logger.info("GA4 OAuth initiated", startup_id=str(startup_id), user_id=str(current_user.id))
    
    return {
        "auth_url": auth_url,
        "state": state,
    }


@router.get("/oauth/google-analytics/callback")
async def ga_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth callback endpoint. Exchanges code for tokens and stores integration.
    """
    # Parse startup_id from state
    try:
        startup_id_str, _ = state.split(":", 1)
        startup_id = UUID(startup_id_str)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{settings.backend_url}/api/v1/integrations/oauth/google-analytics/callback",
            },
        )
        
        if token_response.status_code != 200:
            logger.error("GA4 token exchange failed", response=token_response.text)
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
        
        tokens = token_response.json()
        
        # Get user info to identify the connected account
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        userinfo = userinfo_response.json() if userinfo_response.status_code == 200 else {}
    
    # Check if integration already exists
    result = await db.execute(
        select(Integration).where(
            Integration.startup_id == startup_id,
            Integration.type == "google_analytics",
        )
    )
    integration = result.scalar_one_or_none()
    
    if integration:
        # Update existing integration
        integration.credentials = json.dumps({
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "expires_in": tokens.get("expires_in"),
            "token_type": tokens.get("token_type"),
            "connected_email": userinfo.get("email"),
        })
        integration.status = "active"
        integration.last_sync = datetime.utcnow()
    else:
        # Create new integration
        integration = Integration(
            startup_id=startup_id,
            type="google_analytics",
            name="Google Analytics 4",
            credentials=json.dumps({
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "expires_in": tokens.get("expires_in"),
                "token_type": tokens.get("token_type"),
                "connected_email": userinfo.get("email"),
            }),
            status="active",
            last_sync=datetime.utcnow(),
        )
        db.add(integration)
    
    await db.commit()
    
    logger.info("GA4 integration connected", startup_id=str(startup_id), email=userinfo.get("email"))
    
    # Redirect to frontend success page
    frontend_url = settings.frontend_url or "http://localhost:5173"
    return RedirectResponse(url=f"{frontend_url}/integrations?ga_connected=true")


@router.get("/oauth/google-analytics/status")
async def get_ga_status(
    startup_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if GA4 is connected for a startup"""
    result = await db.execute(
        select(Integration).where(
            Integration.startup_id == startup_id,
            Integration.type == "google_analytics",
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        return {"connected": False}
    
    # Parse credentials to get connected email
    try:
        creds = json.loads(integration.credentials) if integration.credentials else {}
    except json.JSONDecodeError:
        creds = {}
    
    return {
        "connected": integration.status == "active",
        "email": creds.get("connected_email"),
        "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
    }


@router.post("/oauth/google-analytics/disconnect")
async def disconnect_ga(
    startup_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect Google Analytics integration"""
    result = await db.execute(
        select(Integration).where(
            Integration.startup_id == startup_id,
            Integration.type == "google_analytics",
        )
    )
    integration = result.scalar_one_or_none()
    
    if integration:
        integration.status = "disconnected"
        integration.credentials = None
        await db.commit()
    
    logger.info("GA4 integration disconnected", startup_id=str(startup_id))
    
    return {"success": True, "message": "Google Analytics disconnected"}
