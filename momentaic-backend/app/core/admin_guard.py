"""
Admin Guard - War Room Access Control
Restricts sensitive War Room agents to authorized admin emails only.
"""

from functools import wraps
from fastapi import HTTPException, status, Depends
from typing import List, Callable
import structlog

from app.models.user import User
from app.core.security import get_current_user

logger = structlog.get_logger()

# War Room Admin Whitelist
ADMIN_EMAILS: List[str] = [
    "tabaremajem@gmail.com",
]


class AdminGuard:
    """
    Security layer for War Room operations.
    Only whitelisted admins can access these endpoints.
    """
    
    @staticmethod
    def is_admin(user: User) -> bool:
        """Check if user is a War Room admin."""
        return user.email.lower() in [e.lower() for e in ADMIN_EMAILS]
    
    @staticmethod
    async def require_admin(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Dependency that ensures the current user is a War Room admin.
        Raises 403 Forbidden if not authorized.
        """
        if not AdminGuard.is_admin(current_user):
            logger.warning(
                "Unauthorized War Room access attempt",
                user_email=current_user.email,
                user_id=str(current_user.id)
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="War Room access denied. Admin privileges required."
            )
        
        logger.info(
            "War Room access granted",
            admin_email=current_user.email
        )
        return current_user


def admin_only(func: Callable) -> Callable:
    """
    Decorator for War Room agent methods.
    Ensures only admins can trigger these operations.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract user from kwargs if present
        user = kwargs.get('current_user') or kwargs.get('user')
        if user and not AdminGuard.is_admin(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This agent is restricted to War Room admins."
            )
        return await func(*args, **kwargs)
    return wrapper


# Rate limit bypass for War Room operations
WAR_ROOM_RATE_LIMITS = {
    "kol_headhunter": None,  # No limit
    "dealmaker": None,       # No limit
    "localization": None,    # No limit
}
