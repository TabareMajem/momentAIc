"""
Account Pool Manager
Manages 30 social media accounts per platform with automatic
rotation, cooldown tracking, and failover on rate-limit detection.
State is persisted in-memory (Redis-backed in production).
"""

import asyncio
import time
import uuid
import structlog
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from app.core.config import settings

logger = structlog.get_logger(__name__)


class AccountStatus(str, Enum):
    ACTIVE = "active"
    IN_USE = "in_use"
    COOLDOWN = "cooldown"
    BANNED = "banned"
    EXHAUSTED = "exhausted"


@dataclass
class SocialAccount:
    """Represents a single social media account in the rotation pool."""
    id: str
    platform: str  # instagram, twitter, tiktok
    username: str
    credentials: Dict[str, str] = field(default_factory=dict)  # password, 2fa_secret, etc.
    cookies_path: Optional[str] = None
    proxy_ip: Optional[str] = None
    status: AccountStatus = AccountStatus.ACTIVE
    last_used_at: float = 0.0
    cooldown_until: float = 0.0
    request_count: int = 0
    total_requests: int = 0
    session_start: float = 0.0
    error_count: int = 0
    last_error: Optional[str] = None

    @property
    def is_available(self) -> bool:
        if self.status == AccountStatus.BANNED:
            return False
        if self.status == AccountStatus.COOLDOWN:
            return time.time() > self.cooldown_until
        return self.status == AccountStatus.ACTIVE

    @property
    def time_since_last_use(self) -> float:
        return time.time() - self.last_used_at if self.last_used_at else float("inf")


class AccountPool:
    """
    Thread-safe account pool manager for multi-platform scraping.
    Supports acquire/release semantics with automatic failover.
    """

    def __init__(self):
        self._pools: Dict[str, List[SocialAccount]] = {
            "instagram": [],
            "twitter": [],
            "tiktok": [],
        }
        self._lock = asyncio.Lock()
        self._cooldown_hours = getattr(settings, "scraper_cooldown_hours", 24)

    def load_accounts(self, platform: str, accounts: List[Dict[str, Any]]) -> int:
        """
        Load accounts from a list of dicts.
        Each dict must have: username, and optionally: password, cookies_path, proxy.
        """
        loaded = 0
        for acc_data in accounts:
            account = SocialAccount(
                id=f"{platform}-{uuid.uuid4().hex[:8]}",
                platform=platform,
                username=acc_data["username"],
                credentials={
                    k: v for k, v in acc_data.items()
                    if k in ("password", "2fa_secret", "auth_token")
                },
                cookies_path=acc_data.get("cookies_path"),
                proxy_ip=acc_data.get("proxy"),
            )
            self._pools[platform].append(account)
            loaded += 1

        logger.info(
            "Accounts loaded",
            platform=platform,
            count=loaded,
            total_pool=len(self._pools[platform]),
        )
        return loaded

    async def acquire_account(self, platform: str) -> Optional[SocialAccount]:
        """
        Acquire the next available account for scraping.
        Returns None if all accounts are in cooldown/banned.
        """
        async with self._lock:
            pool = self._pools.get(platform, [])
            if not pool:
                logger.error("No accounts loaded for platform", platform=platform)
                return None

            # Reactivate cooled-down accounts
            now = time.time()
            for acc in pool:
                if acc.status == AccountStatus.COOLDOWN and now > acc.cooldown_until:
                    acc.status = AccountStatus.ACTIVE
                    acc.request_count = 0
                    acc.error_count = 0
                    logger.info("Account reactivated from cooldown", account=acc.username)

            # Find the best available account (least recently used)
            available = [a for a in pool if a.is_available]
            if not available:
                cooldown_remaining = min(
                    (a.cooldown_until - now for a in pool if a.status == AccountStatus.COOLDOWN),
                    default=0,
                )
                logger.warning(
                    "No accounts available",
                    platform=platform,
                    total=len(pool),
                    next_available_in=f"{cooldown_remaining:.0f}s",
                )
                return None

            # Sort by least recently used
            available.sort(key=lambda a: a.last_used_at)
            account = available[0]
            account.status = AccountStatus.IN_USE
            account.last_used_at = now
            account.session_start = now

            logger.info(
                "Account acquired",
                account=account.username,
                platform=platform,
                request_count=account.request_count,
            )
            return account

    async def release_account(
        self,
        account_id: str,
        error_code: Optional[int] = None,
        error_msg: Optional[str] = None,
    ) -> None:
        """
        Release an account back to the pool.
        If error_code is 429 or ban-related, parks the account for cooldown.
        """
        async with self._lock:
            account = self._find_account(account_id)
            if not account:
                return

            if error_code in (429, 403) or (error_msg and "rate" in error_msg.lower()):
                cooldown_secs = self._cooldown_hours * 3600
                account.status = AccountStatus.COOLDOWN
                account.cooldown_until = time.time() + cooldown_secs
                account.error_count += 1
                account.last_error = error_msg or f"HTTP {error_code}"
                logger.warning(
                    "Account parked on cooldown",
                    account=account.username,
                    error_code=error_code,
                    cooldown_hours=self._cooldown_hours,
                )
            elif error_code == 401 or (error_msg and "banned" in error_msg.lower()):
                account.status = AccountStatus.BANNED
                account.last_error = error_msg or "Banned"
                logger.error("Account BANNED", account=account.username)
            else:
                account.status = AccountStatus.ACTIVE

    async def increment_request(self, account_id: str) -> None:
        """Track a request for the given account."""
        account = self._find_account(account_id)
        if account:
            account.request_count += 1
            account.total_requests += 1

    def get_pool_status(self, platform: str) -> Dict[str, Any]:
        """Get a summary of the account pool health."""
        pool = self._pools.get(platform, [])
        return {
            "platform": platform,
            "total": len(pool),
            "active": sum(1 for a in pool if a.status == AccountStatus.ACTIVE),
            "in_use": sum(1 for a in pool if a.status == AccountStatus.IN_USE),
            "cooldown": sum(1 for a in pool if a.status == AccountStatus.COOLDOWN),
            "banned": sum(1 for a in pool if a.status == AccountStatus.BANNED),
            "total_requests": sum(a.total_requests for a in pool),
        }

    def get_all_status(self) -> Dict[str, Any]:
        """Get pool status for all platforms."""
        return {
            platform: self.get_pool_status(platform)
            for platform in self._pools
        }

    def _find_account(self, account_id: str) -> Optional[SocialAccount]:
        for pool in self._pools.values():
            for acc in pool:
                if acc.id == account_id:
                    return acc
        return None


# Global singleton
account_pool = AccountPool()
