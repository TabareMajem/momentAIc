"""
DeerFlow Scraper Orchestrator
Master agent that ingests CSV targets, batches them, and spawns
parallel sub-agent workers for distributed scraping.
"""

import asyncio
import csv
import io
import json
import uuid
import time
import structlog
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum

from app.core.config import settings
from app.services.scraper.scraper_worker import ScraperWorker
from app.services.scraper.account_pool import account_pool
from app.services.scraper.proxy_manager import proxy_manager
from app.services.scraper.result_aggregator import ResultAggregator
from app.services.scraper.extractors.base import ProfileData

logger = structlog.get_logger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class ScrapeJob:
    """Represents a scraping job with its state and results."""
    job_id: str
    startup_id: Optional[str] = None
    is_shared: bool = False
    status: JobStatus = JobStatus.PENDING
    total_targets: int = 0
    processed: int = 0
    errors: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    targets: List[Dict[str, str]] = field(default_factory=list)
    workers: List[ScraperWorker] = field(default_factory=list)
    aggregator: Optional[ResultAggregator] = None

    @property
    def progress_pct(self) -> float:
        return (self.processed / max(self.total_targets, 1)) * 100

    @property
    def elapsed(self) -> float:
        end = self.end_time or time.time()
        return end - self.start_time if self.start_time else 0

    @property
    def rate(self) -> float:
        return self.processed / max(self.elapsed, 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "total_targets": self.total_targets,
            "processed": self.processed,
            "errors": self.errors,
            "progress_pct": round(self.progress_pct, 1),
            "elapsed_seconds": round(self.elapsed, 0),
            "rate_per_second": round(self.rate, 3),
            "pool_status": account_pool.get_all_status(),
            "proxy_stats": proxy_manager.get_stats(),
        }


class InfluencerScraperOrchestrator:
    """
    DeerFlow Master Agent for distributed influencer scraping.

    Responsibilities:
    1. Ingest target CSV (handle, platform)
    2. Divide into batches
    3. Spawn parallel workers
    4. Stream real-time progress
    5. Aggregate and export results
    """

    def __init__(self):
        self.jobs: Dict[str, ScrapeJob] = {}
        self.max_workers = getattr(settings, "scraper_max_concurrent_workers", 10)
        self.batch_size = getattr(settings, "scraper_batch_size", 50)

    def ingest_csv(self, csv_content: str, startup_id: Optional[str] = None, is_shared: bool = False) -> tuple:
        """
        Parse a CSV of target profiles.
        Expected columns: handle, platform (instagram/twitter/tiktok)
        Returns: (targets_list, job_id)
        """
        job_id = f"scrape-{uuid.uuid4().hex[:12]}"
        targets = []

        reader = csv.DictReader(io.StringIO(csv_content))
        for row in reader:
            handle = row.get("handle", row.get("username", row.get("url", ""))).strip()
            platform = row.get("platform", "instagram").strip().lower()

            if not handle:
                continue

            # Detect platform from URL if not specified
            if "instagram.com" in handle:
                platform = "instagram"
                handle = handle.split("instagram.com/")[-1].strip("/").split("?")[0]
            elif "x.com" in handle or "twitter.com" in handle:
                platform = "twitter"
                handle = handle.split(".com/")[-1].strip("/").split("?")[0]
            elif "tiktok.com" in handle:
                platform = "tiktok"
                handle = handle.split("@")[-1].strip("/").split("?")[0]

            targets.append({"handle": handle, "platform": platform})

        job = ScrapeJob(
            job_id=job_id,
            startup_id=startup_id,
            is_shared=is_shared,
            total_targets=len(targets),
            targets=targets,
            aggregator=ResultAggregator(),
        )
        self.jobs[job_id] = job

        logger.info(
            "CSV ingested",
            job_id=job_id,
            total_targets=len(targets),
            platforms={p: sum(1 for t in targets if t["platform"] == p) for p in ["instagram", "twitter", "tiktok"]},
        )

        return targets, job_id

    def _create_batches(self, targets: List[Dict]) -> List[List[Dict]]:
        """Divide targets into batches for parallel processing."""
        batches = []
        for i in range(0, len(targets), self.batch_size):
            batches.append(targets[i:i + self.batch_size])
        return batches

    async def run_job(self, job_id: str) -> AsyncGenerator[str, None]:
        """
        Execute a scraping job, yielding SSE progress events.
        This is the main entry point — meant to be called from the API.
        """
        job = self.jobs.get(job_id)
        if not job:
            yield json.dumps({"error": "Job not found"})
            return

        job.status = JobStatus.RUNNING
        job.start_time = time.time()

        yield json.dumps({
            "event": "job_started",
            "job_id": job_id,
            "total_targets": job.total_targets,
            "max_workers": self.max_workers,
            "batch_size": self.batch_size,
        })

        # Group by platform for account efficiency
        platform_groups: Dict[str, List[str]] = {}
        for target in job.targets:
            platform = target["platform"]
            if platform not in platform_groups:
                platform_groups[platform] = []
            platform_groups[platform].append(target["handle"])

        # Process each platform
        for platform, handles in platform_groups.items():
            yield json.dumps({
                "event": "platform_started",
                "platform": platform,
                "count": len(handles),
            })

            batches = self._create_batches(
                [{"handle": h, "platform": platform} for h in handles]
            )

            # Spawn parallel workers (up to max_workers)
            semaphore = asyncio.Semaphore(self.max_workers)

            async def process_batch(batch_idx: int, batch_handles: List[str]):
                async with semaphore:
                    worker = ScraperWorker(
                        worker_id=f"{job_id}-{platform}-w{batch_idx}",
                        platform=platform,
                    )
                    job.workers.append(worker)
                    results = await worker.process_batch(batch_handles)

                    # Feed results to aggregator
                    for profile in results:
                        if job.aggregator:
                            job.aggregator.add_result(profile)
                        job.processed += 1
                        if profile.error:
                            job.errors += 1

            # Create tasks for all batches
            tasks = []
            for idx, batch in enumerate(batches):
                batch_handles = [item["handle"] for item in batch]
                tasks.append(process_batch(idx, batch_handles))

            # Run all workers
            await asyncio.gather(*tasks, return_exceptions=True)

            yield json.dumps({
                "event": "platform_completed",
                "platform": platform,
                "processed": len(handles),
            })

        # Finalize
        job.status = JobStatus.COMPLETED
        job.end_time = time.time()

        # Deduplicate and save to DB
        saved_count = 0
        if job.aggregator:
            job.aggregator.deduplicate()
            
            # Save to Database using a fresh session
            try:
                from app.core.database import async_session_maker
                async with async_session_maker() as db_session:
                    saved_count = await job.aggregator.save_to_database(
                        db_session=db_session,
                        startup_id=job.startup_id,
                        is_shared=job.is_shared,
                        job_id=job_id
                    )
            except Exception as e:
                logger.error("Failed to connect to database for saving scraping results", error=str(e))

        yield json.dumps({
            "event": "job_completed",
            "saved_to_db": saved_count,
            **job.to_dict(),
        })

        logger.info(
            "Scrape job completed",
            job_id=job_id,
            processed=job.processed,
            errors=job.errors,
            elapsed=f"{job.elapsed:.0f}s",
        )

    def stop_job(self, job_id: str) -> bool:
        """Gracefully stop all workers for a job."""
        job = self.jobs.get(job_id)
        if not job:
            return False

        for worker in job.workers:
            worker.stop()

        job.status = JobStatus.STOPPED
        job.end_time = time.time()
        logger.info("Job stopped", job_id=job_id)
        return True

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get current status of a job."""
        job = self.jobs.get(job_id)
        if not job:
            return None
        return job.to_dict()

    def get_results(self, job_id: str, format: str = "json") -> Optional[Any]:
        """Get aggregated results for a completed job."""
        job = self.jobs.get(job_id)
        if not job or not job.aggregator:
            return None

        if format == "csv":
            return job.aggregator.export_csv()
        return job.aggregator.export_json()


# Global singleton
scraper_orchestrator = InfluencerScraperOrchestrator()
