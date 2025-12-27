"""
Cross-Platform SSO API Endpoints
Share premium users between MomentAIc and AgentForgeai.com
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/sso", tags=["Cross-Platform SSO"])


# --- Request/Response Models ---

class SSOTokenRequest(BaseModel):
    token: str


class LinkAccountRequest(BaseModel):
    local_user_id: str
    sso_token: str


class GenerateRedirectRequest(BaseModel):
    user_id: str
    email: str
    tier: str
    target_platform: str  # "agentforge" or "momentaic"
    return_url: Optional[str] = None


# --- Endpoints ---

@router.post("/validate-token")
async def validate_sso_token(request: SSOTokenRequest):
    """
    Validate an SSO token from another platform.
    
    Returns user info if valid, error if invalid.
    """
    from app.services.cross_platform_sso import get_sso_service
    
    sso = get_sso_service()
    result = sso.validate_sso_token(request.token)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired SSO token")
    
    return {
        "valid": True,
        "user": result
    }


@router.post("/link-account")
async def link_accounts(request: LinkAccountRequest):
    """
    Link a local account to an external platform account.
    
    After linking, premium tier is shared between platforms.
    """
    from app.services.cross_platform_sso import get_sso_service
    
    sso = get_sso_service()
    linked_user = sso.link_accounts(request.local_user_id, request.sso_token)
    
    if not linked_user:
        raise HTTPException(status_code=400, detail="Failed to link accounts")
    
    return {
        "success": True,
        "user_id": linked_user.user_id,
        "email": linked_user.email,
        "tier": linked_user.tier.value,
        "platforms": linked_user.platforms
    }


@router.get("/premium-status/{user_id}")
async def get_premium_status(user_id: str):
    """
    Get cross-platform premium status for a user.
    
    Shows if user has premium access from another platform.
    """
    from app.services.cross_platform_sso import get_sso_service
    
    sso = get_sso_service()
    status = sso.get_premium_status(user_id)
    
    return status


@router.post("/generate-redirect")
async def generate_redirect_url(request: GenerateRedirectRequest):
    """
    Generate redirect URL for cross-platform login.
    
    Use this to create a "Login with AgentForge" or 
    "Login with MomentAIc" button.
    """
    from app.services.cross_platform_sso import get_sso_service
    
    sso = get_sso_service()
    redirect_url = sso.generate_redirect_url(
        target_platform=request.target_platform,
        user_id=request.user_id,
        email=request.email,
        tier=request.tier,
        return_url=request.return_url
    )
    
    return {
        "redirect_url": redirect_url,
        "target_platform": request.target_platform
    }


@router.get("/login")
async def sso_login(
    token: str = Query(..., description="SSO token from partner platform"),
    return_url: Optional[str] = Query(None, description="URL to redirect after login")
):
    """
    SSO Login endpoint - validates token and creates/links user.
    
    This is where users land when coming from another platform.
    """
    from app.services.cross_platform_sso import get_sso_service
    
    sso = get_sso_service()
    
    # Validate token
    user_data = sso.validate_sso_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid SSO token")
    
    # In production: Create or get local user, set session/JWT
    # For now, return success with user data
    
    return {
        "success": True,
        "message": "SSO login successful",
        "user": {
            "email": user_data.get("email"),
            "tier": user_data.get("tier"),
            "source_platform": user_data.get("source")
        },
        "return_url": return_url
    }


@router.get("/platforms")
async def list_platforms():
    """
    List available platforms for cross-platform SSO.
    """
    from app.services.cross_platform_sso import CrossPlatformSSO
    
    return {
        "platforms": CrossPlatformSSO.PLATFORMS,
        "current": "momentaic"
    }
