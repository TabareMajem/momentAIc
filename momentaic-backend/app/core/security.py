"""
Security Module
JWT authentication, password hashing, and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import secrets
import structlog

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, RefreshToken

logger = structlog.get_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token() -> str:
    """Create a secure refresh token"""
    return secrets.token_urlsafe(64)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate JWT access token"""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError as e:
        logger.warning("JWT decode error", error=str(e))
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    result = await db.execute(
        select(User).where(User.id == user_uuid, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency to get current verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user


async def get_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency to get superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )
    return current_user


class RequireCredits:
    """
    Dependency to check and deduct credits
    Usage: Depends(RequireCredits(5))
    """
    
    def __init__(self, amount: int, reason: str = "API call"):
        self.amount = amount
        self.reason = reason
    
    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        if current_user.credits_balance < self.amount:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Required: {self.amount}, Available: {current_user.credits_balance}",
                headers={"X-Required-Credits": str(self.amount)},
            )
        
        # Deduct credits
        current_user.credits_balance -= self.amount
        
        # Log transaction
        from app.models.user import CreditTransaction
        transaction = CreditTransaction(
            user_id=current_user.id,
            amount=-self.amount,
            balance_after=current_user.credits_balance,
            transaction_type="deduction",
            reason=self.reason,
        )
        db.add(transaction)
        
        logger.info(
            "Credits deducted",
            user_id=str(current_user.id),
            amount=self.amount,
            balance=current_user.credits_balance,
            reason=self.reason,
        )
        
        return current_user


def require_credits(amount: int, reason: str = "API call"):
    """Factory function for RequireCredits dependency"""
    return RequireCredits(amount, reason)


async def verify_startup_access(
    startup_id: UUID,
    user: User,
    db: AsyncSession,
) -> bool:
    """
    Verify user has access to a startup (Row-Level Security)
    """
    from app.models.startup import Startup
    
    result = await db.execute(
        select(Startup).where(
            Startup.id == startup_id,
            Startup.owner_id == user.id
        )
    )
    startup = result.scalar_one_or_none()
    
    if startup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found or access denied"
        )
    
    return True
