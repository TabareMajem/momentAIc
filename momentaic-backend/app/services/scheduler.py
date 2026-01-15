"""
Background Scheduler Service
APScheduler-based scheduler for cron triggers and background tasks
"""

from datetime import datetime
from typing import Dict, Any, Callable, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import structlog
import asyncio

logger = structlog.get_logger()


class SchedulerService:
    """
    Background scheduler for proactive triggers and data syncing
    
    Features:
    - Cron-based trigger evaluation
    - Periodic integration data syncing
    - Agent-initiated scheduled tasks
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone="UTC",
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 60,
            }
        )
        self._jobs: Dict[str, str] = {}  # job_id -> description
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
            
            # Add default jobs
            self._add_default_jobs()
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler shutdown")
    
    def _add_default_jobs(self):
        """Add default recurring jobs - including ISP (Inevitable Success Protocol) jobs"""
        
        # === ISP DAILY DRIVER - THE MONEY MAKER ===
        # Runs at 8 AM UTC every day to execute automated action plans
        self.add_cron_job(
            job_id="isp_daily_driver",
            func=self._run_daily_driver,
            cron="0 8 * * *",
            description="ISP: Execute daily action plans for all startups",
        )
        
        # === ISP WEEKLY PROGRESS REPORTS ===
        # Runs every Monday at 9 AM UTC
        self.add_cron_job(
            job_id="isp_weekly_reports",
            func=self._run_weekly_reports,
            cron="0 9 * * 1",
            description="ISP: Generate weekly progress reports",
        )
        
        # === EXISTING JOBS ===
        
        # Evaluate triggers every 5 minutes
        self.add_interval_job(
            job_id="evaluate_triggers",
            func=self._evaluate_all_triggers,
            minutes=5,
            description="Evaluate metric and time-based triggers",
        )
        
        # Sync integrations every hour
        self.add_interval_job(
            job_id="sync_integrations",
            func=self._sync_all_integrations,
            hours=1,
            description="Sync data from connected integrations",
        )
        
        # Daily summary at 9 AM UTC
        self.add_cron_job(
            job_id="daily_summary",
            func=self._generate_daily_summaries,
            cron="0 9 * * *",
            description="Generate daily AI summaries for startups",
        )
        
        # === HOURLY HUNTER ===
        self.add_interval_job(
            job_id="hourly_hunter",
            func=self._run_hourly_hunter,
            hours=1,
            description="Hourly Sales Hunter: Find new leads for all startups",
        )
        
        logger.info("Default jobs registered", 
                   jobs=["isp_daily_driver", "isp_weekly_reports", 
                         "evaluate_triggers", "sync_integrations", "daily_summary", "hourly_hunter"])
    
    def add_cron_job(
        self,
        job_id: str,
        func: Callable,
        cron: str,
        description: str = "",
        **kwargs,
    ):
        """Add a cron-based job"""
        # Parse cron expression (minute hour day month weekday)
        parts = cron.split()
        if len(parts) >= 5:
            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
            )
        else:
            logger.error("Invalid cron expression", cron=cron)
            return
        
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            **kwargs,
        )
        self._jobs[job_id] = description
        logger.info("Cron job added", job_id=job_id, cron=cron)
    
    def add_interval_job(
        self,
        job_id: str,
        func: Callable,
        description: str = "",
        **interval_kwargs,
    ):
        """Add an interval-based job"""
        trigger = IntervalTrigger(**interval_kwargs)
        
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
        )
        self._jobs[job_id] = description
        logger.info("Interval job added", job_id=job_id, interval=interval_kwargs)
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            self._jobs.pop(job_id, None)
            logger.info("Job removed", job_id=job_id)
        except Exception as e:
            logger.error("Failed to remove job", job_id=job_id, error=str(e))
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "description": self._jobs.get(job.id, ""),
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            })
        return jobs
    
    async def _evaluate_all_triggers(self):
        """Evaluate triggers for all startups"""
        logger.info("Starting trigger evaluation")
        
        try:
            # Import here to avoid circular imports
            from app.core.database import async_session
            from app.triggers.engine import TriggerEngine
            from app.models.startup import Startup
            from sqlalchemy import select
            
            async with async_session() as db:
                # Get all startups
                result = await db.execute(select(Startup.id))
                startup_ids = [row[0] for row in result.fetchall()]
                
                engine = TriggerEngine(db)
                total_triggered = 0
                
                for startup_id in startup_ids:
                    try:
                        logs = await engine.evaluate_startup_triggers(str(startup_id))
                        total_triggered += len(logs)
                    except Exception as e:
                        logger.error("Trigger evaluation failed", startup_id=str(startup_id), error=str(e))
                
                await db.commit()
                logger.info("Trigger evaluation complete", triggered=total_triggered)
        except Exception as e:
            logger.error("Trigger evaluation failed", error=str(e))
    
    async def _sync_all_integrations(self):
        """Sync data from all active integrations"""
        logger.info("Starting integration sync")
        
        try:
            from app.core.database import async_session
            from app.models.integration import Integration, IntegrationStatus
            from app.integrations import StripeIntegration, GitHubIntegration
            from app.integrations.base import IntegrationCredentials
            from sqlalchemy import select
            from datetime import datetime
            
            async with async_session() as db:
                # Get active integrations
                result = await db.execute(
                    select(Integration).where(
                        Integration.status == IntegrationStatus.ACTIVE
                    )
                )
                integrations = result.scalars().all()
                
                synced = 0
                for integration in integrations:
                    try:
                        # Create appropriate integration client
                        credentials = IntegrationCredentials(
                            access_token=integration.access_token,
                            api_key=integration.api_key,
                        )
                        
                        # Map provider to client (add more as implemented)
                        if integration.provider.value == "stripe":
                            client = StripeIntegration(credentials)
                        elif integration.provider.value == "github":
                            client = GitHubIntegration(credentials)
                        else:
                            continue
                        
                        # Sync
                        result = await client.sync_data()
                        
                        if result.success:
                            integration.last_sync_at = datetime.utcnow()
                            synced += 1
                        else:
                            integration.last_error = "; ".join(result.errors)
                        
                        await client.close()
                    except Exception as e:
                        logger.error("Integration sync failed", 
                                   provider=integration.provider.value, 
                                   error=str(e))
                
                await db.commit()
                logger.info("Integration sync complete", synced=synced)
        except Exception as e:
            logger.error("Integration sync failed", error=str(e))
    
    async def _generate_daily_summaries(self):
        """Generate daily AI summaries for all startups"""
        logger.info("Starting daily summary generation")
        
        try:
            # This would integrate with the Strategy agent to generate summaries
            # For now, just log
            logger.info("Daily summary generation complete")
        except Exception as e:
            logger.error("Daily summary failed", error=str(e))
    
    # === ISP HANDLER METHODS ===
    
    async def _run_daily_driver(self):
        """Execute the Inevitable Success Protocol Daily Driver"""
        logger.info("=== ISP Daily Driver Triggered ===")
        
        try:
            from app.tasks.daily_driver import run_all_daily_drivers
            
            result = await run_all_daily_drivers()
            
            logger.info(
                "ISP Daily Driver complete",
                total=result.get("total_startups", 0),
                successful=result.get("successful", 0),
                failed=result.get("failed", 0)
            )
            
            return result
            
        except Exception as e:
            logger.error("ISP Daily Driver failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _run_weekly_reports(self):
        """Generate ISP Weekly Progress Reports"""
        logger.info("=== ISP Weekly Reports Triggered ===")
        
        try:
            from app.tasks.daily_driver import generate_weekly_reports
            
            result = await generate_weekly_reports()
            
            logger.info(
                "ISP Weekly Reports complete",
                reports_generated=result.get("reports_generated", 0)
            )
            
            return result
            
        except Exception as e:
            logger.error("ISP Weekly Reports failed", error=str(e))
            return {"success": False, "error": str(e)}

    # === HOURLY HUNTER ===
    
    async def _run_hourly_hunter(self):
        """
        Run Sales Hunter agent for all active startups to find new leads.
        """
        logger.info("=== Hourly Sales Hunter Triggered ===")
        
        try:
            from app.models.startup import Startup
            from app.models.growth import Lead, LeadStatus
            from app.core.database import async_session
            from sqlalchemy import select
            from app.agents.sales_agent import sales_agent
            
            async with async_session() as db:
                # Get active startups
                result = await db.execute(select(Startup).where(Startup.is_active == True))
                startups = result.scalars().all()
                
                total_leads = 0
                
                for startup in startups:
                    new_leads_count = 0
                    try:
                        startup_context = {
                            "name": startup.name,
                            "description": startup.description,
                            "industry": startup.industry or "Technology",
                            "tagline": startup.tagline
                        }
                        
                        # Run hunter (limited to 1-2 leads per run to avoid spam/cost)
                        # We pass user_id as owner_id for context
                        hunter_result = await sales_agent.auto_hunt(
                            startup_context=startup_context,
                            user_id=str(startup.owner_id)
                        )
                        
                        leads_data = hunter_result.get("leads", [])
                        
                        for item in leads_data:
                            lead_info = item.get("lead", {})
                            draft = item.get("draft", "")
                            
                            # Create Lead in DB
                            new_lead = Lead(
                                startup_id=startup.id,
                                company_name=lead_info.get("company_name", "Unknown"),
                                contact_name=lead_info.get("contact_name", "Unknown"),
                                contact_email=lead_info.get("contact_email"),
                                status=LeadStatus.NEW,
                                source="ai_hunter",
                                score=70, # Initial score
                                notes=f"Pain point: {lead_info.get('pain_point')}\n\nDraft Outreach:\n{draft}"
                            )
                            db.add(new_lead)
                            total_leads += 1
                            new_leads_count += 1
                        
                        # Use Notification Service if leads found
                        if new_leads_count > 0:
                            from app.models.user import User
                            from app.services.notification_service import notification_service
                            
                            # Get Owner
                            user_result = await db.execute(select(User).where(User.id == startup.owner_id))
                            owner = user_result.scalar_one_or_none()
                            
                            if owner:
                                await notification_service.notify_user(
                                    user=owner,
                                    subject=f"Found {new_leads_count} New Leads",
                                    body=f"Sales Agent found {new_leads_count} potential leads for {startup.name}.",
                                    action_url=f"https://app.momentaic.com/startups/{startup.id}/growth",
                                    db=db
                                )
                                logger.info(f"Notified owner {owner.email} of {new_leads_count} new leads")
                            
                    except Exception as e:
                        logger.error(f"Hunter failed for {startup.name}: {e}")
                        
                await db.commit()
                logger.info(f"Hourly Hunter complete. Found {total_leads} new leads.")
                
        except Exception as e:
            logger.error("Hourly Hunter failed", error=str(e))


# Singleton instance
scheduler = SchedulerService()


def get_scheduler() -> SchedulerService:
    """Get the scheduler instance"""
    return scheduler
