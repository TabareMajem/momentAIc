"""
Authentication Service
User registration, login, token management
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import structlog

from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.models.user import User, RefreshToken, CreditTransaction, UserTier
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenPair,
    AuthResponse,
)

logger = structlog.get_logger()


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(self, user_data: UserCreate) -> AuthResponse:
        """
        Register a new user
        """
        # Check if email exists
        result = await self.db.execute(
            select(User).where(User.email == user_data.email.lower())
        )
        if result.scalar_one_or_none():
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            email=user_data.email.lower(),
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            tier=UserTier.STARTER,
            credits_balance=settings.default_starter_credits,
            avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data.full_name}",
        )
        
        self.db.add(user)
        await self.db.flush()
        
        # Create initial credit transaction
        transaction = CreditTransaction(
            user_id=user.id,
            amount=settings.default_starter_credits,
            balance_after=settings.default_starter_credits,
            transaction_type="topup",
            reason="Welcome bonus - Starter tier",
        )
        self.db.add(transaction)
        
        # Generate tokens
        tokens = await self._create_tokens(user)
        
        logger.info("User registered", user_id=str(user.id), email=user.email)
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )
    
    async def login(self, credentials: UserLogin) -> AuthResponse:
        """
        Authenticate user and return tokens
        """
        from fastapi import HTTPException, status
        
        result = await self.db.execute(
            select(User).where(User.email == credentials.email.lower())
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        
        # Generate tokens
        tokens = await self._create_tokens(user)
        
        logger.info("User logged in", user_id=str(user.id))
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )
    
    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """
        Refresh access token using refresh token
        """
        from fastapi import HTTPException, status
        
        # Find refresh token
        result = await self.db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.token == refresh_token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        )
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == token_record.user_id, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Revoke old token
        token_record.is_revoked = True
        
        # Create new tokens
        tokens = await self._create_tokens(user)
        
        logger.info("Tokens refreshed", user_id=str(user.id))
        
        return tokens
    
    async def logout(self, user_id: UUID, refresh_token: Optional[str] = None):
        """
        Logout user by revoking refresh tokens
        """
        if refresh_token:
            # Revoke specific token
            result = await self.db.execute(
                select(RefreshToken).where(
                    RefreshToken.token == refresh_token,
                    RefreshToken.user_id == user_id
                )
            )
            token_record = result.scalar_one_or_none()
            if token_record:
                token_record.is_revoked = True
        else:
            # Revoke all tokens for user
            result = await self.db.execute(
                select(RefreshToken).where(
                    RefreshToken.user_id == user_id,
                    RefreshToken.is_revoked == False
                )
            )
            tokens = result.scalars().all()
            for token in tokens:
                token.is_revoked = True
        
        logger.info("User logged out", user_id=str(user_id))
    
    async def _create_tokens(self, user: User) -> TokenPair:
        """
        Create access and refresh token pair
        """
        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "tier": user.tier.value,
            }
        )
        
        # Create refresh token
        refresh_token_value = create_refresh_token()
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_value,
            expires_at=datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days),
        )
        
        self.db.add(refresh_token)
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token_value,
        )
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_profile(
        self,
        user: User,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        preferences: Optional[dict] = None,
    ) -> User:
        """Update user profile"""
        if full_name:
            user.full_name = full_name
        if avatar_url:
            user.avatar_url = avatar_url
        if preferences:
            user.preferences = {**user.preferences, **preferences}
        
        return user
