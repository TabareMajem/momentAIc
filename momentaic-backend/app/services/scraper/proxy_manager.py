"""
Proxy Manager
Manages sticky session proxy assignments for stealth scraping.
Each account gets a dedicated proxy IP for 5-10 min windows.
"""

import time
import random
import structlog
from typing import Dict, Optional, List
from dataclasses import dataclass

from app.core.config import settings

logger = structlog.get_logger(__name__)


@dataclass
class ProxyAssignment:
    """A proxy IP assigned to a specific account for a sticky window."""
    proxy_url: str
    account_id: str
    assigned_at: float
    request_count: int = 0
    max_duration: float = 420.0  # 7 min default
    max_requests: int = 25       # 15-30 request window


class ProxyManager:
    """
    Assigns and rotates sticky session proxies for accounts.
    Ensures IP-account affinity within rotation windows.
    """

    def __init__(self):
        self._assignments: Dict[str, ProxyAssignment] = {}  # account_id -> assignment
        self._proxy_pool: List[str] = []
        self._used_proxies: Dict[str, float] = {}  # proxy -> last_used_at
        self._sticky_duration = getattr(settings, "scraper_proxy_sticky_duration", 420)

    def load_proxies(self, proxy_list: List[str]) -> int:
        """
        Load proxy URLs into the pool.
        Format: protocol://user:pass@host:port or protocol://host:port
        """
        self._proxy_pool = list(set(proxy_list))
        logger.info("Proxy pool loaded", count=len(self._proxy_pool))
        return len(self._proxy_pool)

    def get_proxy(self, account_id: str) -> Optional[str]:
        """
        Get the current sticky proxy for an account.
        If expired or unassigned, rotates to a new one.
        """
        existing = self._assignments.get(account_id)

        if existing and not self._is_expired(existing):
            existing.request_count += 1
            return existing.proxy_url

        # Need a new proxy
        return self._rotate_proxy(account_id)

    def _rotate_proxy(self, account_id: str) -> Optional[str]:
        """Assign a fresh proxy to the account."""
        if not self._proxy_pool:
            logger.warning("No proxies available, running direct")
            return None

        # Pick a proxy not recently used by another account
        now = time.time()
        available = [
            p for p in self._proxy_pool
            if p not in [a.proxy_url for a in self._assignments.values()]
            or self._used_proxies.get(p, 0) < now - 60
        ]

        if not available:
            available = self._proxy_pool  # Fallback to any

        proxy = random.choice(available)

        # Randomize sticky window duration (5-10 min)
        duration = random.uniform(300, 600)
        max_requests = random.randint(15, 30)

        self._assignments[account_id] = ProxyAssignment(
            proxy_url=proxy,
            account_id=account_id,
            assigned_at=now,
            max_duration=duration,
            max_requests=max_requests,
        )
        self._used_proxies[proxy] = now

        logger.info(
            "Proxy rotated",
            account_id=account_id,
            proxy=proxy[:30] + "...",
            sticky_duration=f"{duration:.0f}s",
            max_requests=max_requests,
        )
        return proxy

    def _is_expired(self, assignment: ProxyAssignment) -> bool:
        """Check if a proxy assignment has expired by time or request count."""
        now = time.time()
        time_expired = (now - assignment.assigned_at) > assignment.max_duration
        requests_exceeded = assignment.request_count >= assignment.max_requests
        return time_expired or requests_exceeded

    def force_rotate(self, account_id: str) -> Optional[str]:
        """Force an immediate proxy rotation for an account."""
        self._assignments.pop(account_id, None)
        return self._rotate_proxy(account_id)

    def release(self, account_id: str) -> None:
        """Release a proxy assignment when an account is done."""
        assignment = self._assignments.pop(account_id, None)
        if assignment:
            logger.info(
                "Proxy released",
                account_id=account_id,
                requests_served=assignment.request_count,
            )

    def get_stats(self) -> Dict:
        """Get proxy pool statistics."""
        return {
            "total_proxies": len(self._proxy_pool),
            "active_assignments": len(self._assignments),
            "assignments": {
                acc_id: {
                    "proxy": a.proxy_url[:30] + "...",
                    "requests": a.request_count,
                    "age_seconds": int(time.time() - a.assigned_at),
                }
                for acc_id, a in self._assignments.items()
            },
        }


# Global singleton
proxy_manager = ProxyManager()
