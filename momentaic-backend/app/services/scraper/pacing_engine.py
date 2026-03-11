"""
Behavioral Pacing Engine
Implements human-mimicry timing patterns to evade platform detection.
Includes micro-delays, macro-pauses, jitter, and automatic 429 detection.
"""

import asyncio
import random
import time
import structlog
from typing import Optional, Callable, Awaitable

from app.core.config import settings

logger = structlog.get_logger(__name__)


class PacingEngine:
    """
    Human-behavior simulation engine for stealth scraping.
    Controls timing between requests to avoid rate-limit triggers.
    """

    def __init__(self):
        self.micro_delay_min = getattr(settings, "scraper_micro_delay_min", 3.0)
        self.micro_delay_max = getattr(settings, "scraper_micro_delay_max", 5.0)
        self.macro_pause_min = getattr(settings, "scraper_macro_pause_min", 300.0)
        self.macro_pause_max = getattr(settings, "scraper_macro_pause_max", 600.0)
        self.macro_interval = getattr(settings, "scraper_macro_pause_interval", 75)
        self._request_count = 0
        self._session_start = time.time()
        self._total_paused = 0.0

    async def micro_delay(self) -> float:
        """
        Random 3-5 second delay between profile visits.
        Adds sub-second Gaussian jitter for naturalness.
        """
        base = random.uniform(self.micro_delay_min, self.micro_delay_max)
        jitter = random.gauss(0, 0.3)  # ±0.3s Gaussian noise
        delay = max(1.0, base + jitter)
        await asyncio.sleep(delay)
        self._request_count += 1
        return delay

    async def macro_pause(self, force: bool = False) -> float:
        """
        Forced 5-10 minute pause every 50-100 requests.
        Simulates human fatigue / tab switching behavior.
        Returns the pause duration, or 0 if no pause was needed.
        """
        # Randomize the interval within the 50-100 range
        actual_interval = random.randint(
            max(50, self.macro_interval - 25),
            min(100, self.macro_interval + 25),
        )

        if force or self._request_count >= actual_interval:
            duration = random.uniform(self.macro_pause_min, self.macro_pause_max)
            logger.info(
                "Macro pause triggered",
                request_count=self._request_count,
                pause_duration=f"{duration:.0f}s",
                interval_threshold=actual_interval,
            )
            await asyncio.sleep(duration)
            self._request_count = 0  # Reset counter
            self._total_paused += duration
            return duration

        return 0.0

    async def check_and_pace(self) -> float:
        """
        Combined pacing call: applies micro delay + checks if macro pause needed.
        Returns total time spent waiting.
        """
        total = 0.0
        # Always apply micro delay
        total += await self.micro_delay()
        # Check for macro pause
        total += await self.macro_pause()
        return total

    def simulate_scroll_jitter(self) -> dict:
        """
        Generate randomized scroll/mouse movement parameters
        to inject into browser automation for naturalness.
        """
        return {
            "scroll_delta_y": random.randint(200, 800),
            "scroll_speed_ms": random.randint(300, 1200),
            "mouse_move_steps": random.randint(3, 12),
            "mouse_jitter_px": random.uniform(1.0, 5.0),
            "pause_after_scroll_ms": random.randint(500, 2000),
        }

    def is_rate_limited(self, status_code: int, response_text: str = "") -> bool:
        """
        Detect rate-limiting or ban signals from HTTP responses.
        Returns True if the account should be parked.
        """
        if status_code in (429, 503):
            return True

        rate_limit_signals = [
            "rate limit",
            "too many requests",
            "quota exhausted",
            "temporarily blocked",
            "please wait",
            "challenge_required",
            "login_required",
            "consent_required",
        ]

        text_lower = response_text.lower()
        for signal in rate_limit_signals:
            if signal in text_lower:
                logger.warning("Rate limit signal detected", signal=signal)
                return True

        return False

    def get_stats(self) -> dict:
        """Get pacing statistics for the current session."""
        elapsed = time.time() - self._session_start
        return {
            "requests_since_last_pause": self._request_count,
            "total_pause_time": f"{self._total_paused:.0f}s",
            "session_duration": f"{elapsed:.0f}s",
            "effective_rate": f"{self._request_count / max(elapsed - self._total_paused, 1):.2f} req/s",
        }

    def reset(self):
        """Reset all counters for a new session."""
        self._request_count = 0
        self._session_start = time.time()
        self._total_paused = 0.0
