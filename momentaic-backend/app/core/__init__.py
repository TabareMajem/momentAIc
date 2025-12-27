"""
MomentAIc Core
Core configuration, database, and security modules
"""

from app.core.config import settings
from app.core.database import (
    Base,
    engine,
    async_session_maker,
    get_db,
    init_db,
    close_db,
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    require_credits,
    verify_startup_access,
)

__all__ = [
    # Config
    "settings",
    # Database
    "Base",
    "engine",
    "async_session_maker",
    "get_db",
    "init_db",
    "close_db",
    # Security
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "require_credits",
    "verify_startup_access",
]
