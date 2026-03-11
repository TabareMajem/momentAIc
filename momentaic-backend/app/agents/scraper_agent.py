"""
Influencer Scraper Agent
Heartbeat-compatible agent for autonomous influencer scraping.
"""

import structlog
from typing import Dict, Any, Optional, List

logger = structlog.get_logger(__name__)


class InfluencerScraperAgent:
    """
    Heartbeat-compatible agent wrapper for the Influencer Scraper.
    Can be triggered by the OpenClaw heartbeat scheduler or manually via API.
    """

    name = "influencer_scraper"
    description = "Autonomous micro-influencer data harvester"
    schedule = "manual"  # Not on auto heartbeat by default
    cost_credits = 20  # Credits per scrape job

    def __init__(self):
        self.active_job_id: Optional[str] = None

    async def run(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a scraping job from context.
        Context must include 'csv_content' or 'targets' list.
        """
        from app.services.scraper.scraper_orchestrator import scraper_orchestrator

        context = context or {}

        csv_content = context.get("csv_content")
        if csv_content:
            targets, job_id = scraper_orchestrator.ingest_csv(csv_content)
        else:
            return {
                "success": False,
                "error": "No CSV content or targets provided",
            }

        self.active_job_id = job_id

        # Load accounts if provided
        accounts_config = context.get("accounts", {})
        from app.services.scraper.account_pool import account_pool

        for platform, accs in accounts_config.items():
            account_pool.load_accounts(platform, accs)

        # Load proxies if provided
        proxies = context.get("proxies", [])
        if proxies:
            from app.services.scraper.proxy_manager import proxy_manager
            proxy_manager.load_proxies(proxies)

        # Run the job (non-streaming version for heartbeat)
        results = []
        async for event_json in scraper_orchestrator.run_job(job_id):
            results.append(event_json)

        status = scraper_orchestrator.get_job_status(job_id)

        return {
            "success": True,
            "job_id": job_id,
            "status": status,
            "events": len(results),
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        from app.services.scraper.scraper_orchestrator import scraper_orchestrator

        if self.active_job_id:
            return scraper_orchestrator.get_job_status(self.active_job_id) or {
                "status": "no_job"
            }
        return {"status": "idle"}

    async def stop(self) -> bool:
        """Stop the current scraping job."""
        from app.services.scraper.scraper_orchestrator import scraper_orchestrator

        if self.active_job_id:
            return scraper_orchestrator.stop_job(self.active_job_id)
        return False


# Global singleton
scraper_agent = InfluencerScraperAgent()
