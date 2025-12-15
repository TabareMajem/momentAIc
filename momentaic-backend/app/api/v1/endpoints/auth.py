"""
Authentication Endpoints
User registration, login, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    AuthResponse,
    RefreshTokenRequest,
    TokenPair,
    UpdateProfileRequest,
    CreditBalanceResponse,
    OAuthStatusResponse,
)
from app.models.user import User

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.
    
    Creates user with Starter tier and initial credits.
    """
    service = AuthService(db)
    return await service.register(user_data)


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and get access tokens.
    """
    service = AuthService(db)
    return await service.login(credentials)


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    """
    service = AuthService(db)
    return await service.refresh_tokens(refresh_request.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_request: RefreshTokenRequest = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user by revoking refresh tokens.
    """
    service = AuthService(db)
    refresh_token = refresh_request.refresh_token if refresh_request else None
    await service.logout(current_user.id, refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's profile.
    """
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    profile_update: UpdateProfileRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile.
    """
    service = AuthService(db)
    updated_user = await service.update_profile(
        user=current_user,
        full_name=profile_update.full_name,
        avatar_url=profile_update.avatar_url,
        preferences=profile_update.preferences,
    )
    return UserResponse.model_validate(updated_user)


@router.get("/credits", response_model=CreditBalanceResponse)
async def get_credit_balance(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current credit balance and usage.
    """
    from app.core.config import settings
    
    # Get tier monthly credits
    tier_credits = {
        "starter": settings.default_starter_credits,
        "growth": settings.default_growth_credits,
        "god_mode": settings.default_god_mode_credits,
    }
    
    return CreditBalanceResponse(
        balance=current_user.credits_balance,
        tier=current_user.tier,
        tier_monthly_credits=tier_credits.get(current_user.tier.value, 50),
        usage_this_month=0,  # TODO: Calculate from transactions
    )


@router.get("/oauth/status", response_model=OAuthStatusResponse)
async def get_oauth_status(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get OAuth connection status for integrations.
    """
    return OAuthStatusResponse(
        github_connected=bool(current_user.github_token),
        linkedin_connected=bool(current_user.linkedin_token),
        gmail_connected=bool(current_user.gmail_token),
    )
