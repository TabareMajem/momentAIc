"""
Authentication Schemas
Pydantic models for auth endpoints
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID

from app.models.user import UserTier


class UserBase(BaseModel):
    """Base user fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    """User registration"""
    password: str = Field(..., min_length=8, max_length=100)
    referral_code: Optional[str] = None
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """User login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User profile response"""
    id: UUID
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    tier: UserTier
    credits_balance: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    """JWT token pair"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Authentication response"""
    user: UserResponse
    tokens: TokenPair


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Change password (authenticated)"""
    current_password: str
    new_password: str = Field(..., min_length=8)


class UpdateProfileRequest(BaseModel):
    """Update user profile"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = None


class CreditBalanceResponse(BaseModel):
    """Credit balance info"""
    balance: int
    tier: UserTier
    tier_monthly_credits: int
    usage_this_month: int


class CreditTransactionResponse(BaseModel):
    """Credit transaction record"""
    id: UUID
    amount: int
    balance_after: int
    transaction_type: str
    reason: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class OAuthConnectRequest(BaseModel):
    """OAuth connection request"""
    provider: str  # github, linkedin, gmail
    code: str
    redirect_uri: str


class OAuthStatusResponse(BaseModel):
    """OAuth connection status"""
    github_connected: bool
    linkedin_connected: bool
    gmail_connected: bool
