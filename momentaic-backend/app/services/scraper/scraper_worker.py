"""
Scraper Worker
Individual sub-agent that processes a batch of profiles with
account rotation, pacing, and automatic failover on rate-limits.
"""

import asyncio
import json
import time
import structlog
from typing import Dict, Any, List, Optional, AsyncGenerator

from app.services.scraper.account_pool import account_pool, SocialAccount
from app.services.scraper.proxy_manager import proxy_manager
from app.services.scraper.pacing_engine import PacingEngine
from app.services.scraper.extractors.base import ProfileData
from app.services.scraper.extractors import EXTRACTORS
from app.integrations.camoufox_client import camoufox_client
from app.integrations.openclaw import OpenClawIntegration

logger = structlog.get_logger(__name__)


class ScraperWorker:
    """
    Individual sub-agent worker for processing a batch of profile URLs.
    Handles Camoufox session → OpenClaw browser → extraction → result streaming.
    """

    def __init__(self, worker_id: str, platform: str):
        self.worker_id = worker_id
        self.platform = platform
        self.pacing = PacingEngine()
        self.results: List[ProfileData] = []
        self.errors: List[Dict[str, Any]] = []
        self.retry_queue: List[str] = []  # Failed handles to retry once
        self.is_running = False
        self._current_account: Optional[SocialAccount] = None

    async def process_batch(
        self,
        handles: List[str],
        on_progress: Optional[callable] = None,
    ) -> List[ProfileData]:
        """
        Process a batch of profiles with full stealth pipeline.

        Flow per profile:
        1. Acquire account + proxy from pool
        2. Create Camoufox anti-detect session
        3. Open profile via OpenClaw
        4. Extract data with platform extractor
        5. Apply pacing delay
        6. Release resources / handle failover
        """
        self.is_running = True
        self.pacing.reset()
        extractor_cls = EXTRACTORS.get(self.platform)

        if not extractor_cls:
            logger.error("No extractor for platform", platform=self.platform)
            return []

        extractor = extractor_cls()
        processed = 0
        total = len(handles)

        logger.info(
            "Worker starting batch",
            worker_id=self.worker_id,
            platform=self.platform,
            batch_size=total,
        )

        for handle in handles:
            if not self.is_running:
                logger.info("Worker stopped", worker_id=self.worker_id)
                break

            try:
                profile = await self._scrape_single(handle, extractor)
                self.results.append(profile)
                processed += 1

                if on_progress:
                    try:
                        on_progress(self.worker_id, processed, total, profile)
                    except Exception:
                        pass

                # Apply pacing (micro delay + macro pause check)
                await self.pacing.check_and_pace()

            except Exception as e:
                logger.error(
                    "Worker profile error",
                    worker_id=self.worker_id,
                    handle=handle,
                    error=str(e),
                )
                # Queue for retry instead of permanent failure
                self.retry_queue.append(handle)

        # Retry pass: attempt failed profiles one more time
        if self.retry_queue and self.is_running:
            logger.info(
                "Worker retry pass starting",
                worker_id=self.worker_id,
                retry_count=len(self.retry_queue),
            )
            retry_handles = self.retry_queue.copy()
            self.retry_queue.clear()
            for handle in retry_handles:
                if not self.is_running:
                    break
                try:
                    profile = await self._scrape_single(handle, extractor)
                    self.results.append(profile)
                    processed += 1
                    await self.pacing.check_and_pace()
                except Exception as e:
                    error_profile = ProfileData(
                        platform=self.platform,
                        handle=handle,
                        error=f"Retry failed: {str(e)}",
                    )
                    self.results.append(error_profile)
                    self.errors.append({"handle": handle, "error": str(e)})

        self.is_running = False
        logger.info(
            "Worker batch complete",
            worker_id=self.worker_id,
            processed=processed,
            errors=len(self.errors),
        )
        return self.results

    async def _scrape_single(self, handle: str, extractor, _retry_depth: int = 0) -> ProfileData:
        """Scrape a single profile with full stealth pipeline."""
        MAX_RETRIES = 3
        if _retry_depth >= MAX_RETRIES:
            return ProfileData(
                platform=self.platform,
                handle=handle,
                error=f"Max retries ({MAX_RETRIES}) exceeded after rate limits",
            )
        # 1. Ensure we have a working account
        if not self._current_account or not self._current_account.is_available:
            self._current_account = await self._acquire_fresh_account()
            if not self._current_account:
                return ProfileData(
                    platform=self.platform,
                    handle=handle,
                    error="No accounts available (all in cooldown)",
                )

        account = self._current_account

        # 2. Get/rotate proxy
        proxy = proxy_manager.get_proxy(account.id)

        # 3. Create Camoufox session
        camo_session = await camoufox_client.create_session(
            account_id=account.id,
            proxy=proxy,
            platform=self.platform,
        )

        # 4. Navigate via OpenClaw
        profile_url = extractor.get_profile_url(handle)
        oc = OpenClawIntegration()

        try:
            result = await oc.execute_action("browser_navigate", {
                "url": profile_url,
                "wait_for": "body",
            })

            if not result.get("success"):
                error_msg = result.get("error", "Navigation failed")
                # Check for rate limiting
                if self.pacing.is_rate_limited(429, error_msg):
                    await self._handle_rate_limit(account)
                    # Retry with new account (bounded by max retries)
                    return await self._scrape_single(handle, extractor, _retry_depth + 1)

                return ProfileData(
                    platform=self.platform,
                    handle=handle,
                    error=error_msg,
                )

            # 5. Get page content
            page_content = ""
            snapshot = result.get("snapshot", {})
            if snapshot:
                content = snapshot.get("content", "")
                page_content = json.dumps(content) if isinstance(content, dict) else str(content)

            # 6. Extract profile data
            profile = await extractor.extract_profile(
                handle=handle,
                page_content=page_content,
                snapshot=snapshot,
            )

            # 7. Track request
            await account_pool.increment_request(account.id)

            return profile

        except Exception as e:
            error_str = str(e)

            # Check for rate limit in exception
            if self.pacing.is_rate_limited(0, error_str):
                await self._handle_rate_limit(account)
                return ProfileData(
                    platform=self.platform,
                    handle=handle,
                    error=f"Rate limited, account parked: {error_str}",
                )

            raise

        finally:
            # Cleanup Camoufox session
            await camoufox_client.destroy_session(camo_session.session_id)

    async def _acquire_fresh_account(self) -> Optional[SocialAccount]:
        """Acquire a fresh account from the pool."""
        account = await account_pool.acquire_account(self.platform)
        if account:
            logger.info(
                "Worker acquired account",
                worker_id=self.worker_id,
                account=account.username,
            )
        return account

    async def _handle_rate_limit(self, account: SocialAccount) -> None:
        """Handle rate limit: park account, acquire new one."""
        logger.warning(
            "Rate limit detected, hot-swapping account",
            worker_id=self.worker_id,
            parked_account=account.username,
        )
        await account_pool.release_account(
            account.id,
            error_code=429,
            error_msg="Rate limited during scraping",
        )
        proxy_manager.release(account.id)

        # Acquire replacement
        self._current_account = await self._acquire_fresh_account()

    def stop(self):
        """Signal the worker to stop processing."""
        self.is_running = False
        logger.info("Worker stop requested", worker_id=self.worker_id)
