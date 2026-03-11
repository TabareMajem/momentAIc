"""
Camoufox Anti-Detect Client
Interfaces with a Camoufox MCP/REST server to provide C++-level
fingerprint spoofing and strict session isolation for stealth browsing.
"""

import httpx
import uuid
import structlog
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from app.core.config import settings

logger = structlog.get_logger(__name__)


@dataclass
class CamoufoxSession:
    """Represents an isolated anti-detect browser session."""
    session_id: str
    fingerprint: Dict[str, Any] = field(default_factory=dict)
    proxy: Optional[str] = None
    channel_peer: Optional[str] = None  # Cookie/storage isolation scope
    user_agent: str = ""
    is_active: bool = True
    cookies: Optional[str] = None  # Raw cookie string for session injection


class CamoufoxClient:
    """
    REST client for the Camoufox anti-detect server.
    Manages session creation, fingerprint assignment, and per-account isolation.
    """

    def __init__(self):
        self.base_url = getattr(settings, "camoufox_api_url", "http://localhost:8585")
        self.api_key = getattr(settings, "camoufox_api_key", None)
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        self.active_sessions: Dict[str, CamoufoxSession] = {}

    async def create_session(
        self,
        account_id: str,
        proxy: Optional[str] = None,
        platform: str = "generic",
        cookies: Optional[str] = None,
    ) -> CamoufoxSession:
        """
        Create a new anti-detect browser session with unique fingerprint.
        Each session is strictly isolated by channel_peer (account_id).
        """
        session_id = f"camo-{uuid.uuid4().hex[:12]}"
        channel_peer = f"scraper-{account_id}"

        payload = {
            "session_id": session_id,
            "channel_peer": channel_peer,
            "proxy": proxy,
            "platform_hint": platform,
            "config": {
                "tls_fingerprint": "randomize",
                "webgl_vendor": "randomize",
                "canvas_noise": True,
                "audio_context_noise": True,
                "timezone": "auto",      # Match proxy geo
                "language": "en-US",
                "screen_resolution": "randomize",
                "hardware_concurrency": "randomize",
                "device_memory": "randomize",
                "webrtc_leak_prevention": True,
                "navigator_plugins": "randomize",
            },
        }

        # Inject cookies for session auth if provided
        if cookies:
            payload["cookies"] = cookies

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/sessions/create",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()

            session = CamoufoxSession(
                session_id=session_id,
                fingerprint=data.get("fingerprint", {}),
                proxy=proxy,
                channel_peer=channel_peer,
                user_agent=data.get("user_agent", ""),
                is_active=True,
                cookies=cookies,
            )
            self.active_sessions[session_id] = session
            logger.info(
                "Camoufox session created",
                session_id=session_id,
                account_id=account_id,
                platform=platform,
            )
            return session

        except httpx.HTTPStatusError as e:
            logger.error("Camoufox session creation failed (HTTP)", status=e.response.status_code)
            # Fallback: return a degraded session with randomized UA
            return self._create_fallback_session(session_id, account_id, proxy)

        except Exception as e:
            logger.warning("Camoufox server unreachable, using fallback", error=str(e))
            return self._create_fallback_session(session_id, account_id, proxy)

    def _create_fallback_session(
        self, session_id: str, account_id: str, proxy: Optional[str]
    ) -> CamoufoxSession:
        """Create a degraded session when Camoufox server is unavailable."""
        import random

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
        ]

        session = CamoufoxSession(
            session_id=session_id,
            fingerprint={"mode": "fallback"},
            proxy=proxy,
            channel_peer=f"scraper-{account_id}",
            user_agent=random.choice(user_agents),
            is_active=True,
        )
        self.active_sessions[session_id] = session
        logger.info("Fallback session created", session_id=session_id)
        return session

    async def destroy_session(self, session_id: str) -> bool:
        """Tear down a session, clearing all fingerprints and cookies."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/sessions/destroy",
                    json={"session_id": session_id},
                    headers=self.headers,
                )
                response.raise_for_status()
        except Exception as e:
            logger.warning("Camoufox session destroy failed (non-critical)", error=str(e))

        self.active_sessions.pop(session_id, None)
        logger.info("Camoufox session destroyed", session_id=session_id)
        return True

    async def get_browser_context_config(self, session: CamoufoxSession) -> Dict[str, Any]:
        """
        Returns Playwright-compatible browser context config
        injected with Camoufox fingerprint data.
        """
        config = {
            "user_agent": session.user_agent,
            "viewport": {"width": 1920, "height": 1080},
            "ignore_https_errors": True,
            "java_script_enabled": True,
        }

        if session.proxy:
            proxy_parts = session.proxy.split("://")
            scheme = proxy_parts[0] if len(proxy_parts) > 1 else "http"
            server = proxy_parts[-1]
            config["proxy"] = {"server": f"{scheme}://{server}"}

        fp = session.fingerprint
        if fp.get("timezone"):
            config["timezone_id"] = fp["timezone"]
        if fp.get("locale"):
            config["locale"] = fp["locale"]
        if fp.get("screen_resolution"):
            w, h = fp["screen_resolution"].split("x")
            config["viewport"] = {"width": int(w), "height": int(h)}

        # Inject cookies into context if available
        if session.cookies:
            config["cookies"] = self._parse_cookie_string(session.cookies)

        return config

    @staticmethod
    def _parse_cookie_string(cookie_str: str) -> list:
        """Parse raw 'key=val; key2=val2' cookie string into Playwright cookie list."""
        cookies = []
        for pair in cookie_str.split(";"):
            pair = pair.strip()
            if "=" in pair:
                name, value = pair.split("=", 1)
                cookies.append({"name": name.strip(), "value": value.strip(), "domain": ".", "path": "/"})
        return cookies

    async def health_check(self) -> bool:
        """Check if Camoufox server is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self.headers,
                )
                return response.status_code == 200
        except Exception:
            return False


# Global singleton
camoufox_client = CamoufoxClient()
