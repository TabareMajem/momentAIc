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
        
        # === PHASE 2: PROACTIVE AGENT JOBS ===
        
        # Content Daily Post — auto-generate & schedule content (10 AM UTC)
        self.add_cron_job(
            job_id="content_daily_post",
            func=self._run_content_daily_post,
            cron="0 10 * * *",
            description="Auto-generate and schedule daily content for all startups",
        )
        
        # Competitor Weekly Scan — scan competitors for changes (Wed 7 AM UTC)
        self.add_cron_job(
            job_id="competitor_weekly_scan",
            func=self._run_competitor_weekly_scan,
            cron="0 7 * * 3",
            description="Weekly competitor intelligence scan for all startups",
        )
        
        # Growth Social Scan — find social opportunities every 4 hours
        self.add_interval_job(
            job_id="growth_social_scan",
            func=self._run_growth_social_scan,
            hours=4,
            description="Scan social platforms for growth opportunities",
        )
        
        # Overdue Goals Nag — alert founders on overdue goals (3 PM UTC daily)
        self.add_cron_job(
            job_id="overdue_goals_nag",
            func=self._run_overdue_goals_nag,
            cron="0 15 * * *",
            description="Alert founders about overdue goals",
        )
        
        # Reddit Sniper Scan — find high-intent threads every 4 hours
        self.add_interval_job(
            job_id="reddit_sniper_scan",
            func=self._run_reddit_sniper_scan,
            hours=4,
            description="Reddit Sniper: Find high-intent threads for narrative marketing",
        )
        
        # Morning Brief — real email to founders (6 AM UTC daily)
        self.add_cron_job(
            job_id="morning_brief",
            func=self._run_morning_brief,
            cron="0 6 * * *",
            description="Generate and send morning brief to all founders",
        )
        
        # QA Weekly Audit — auto-audit startup URLs (Sunday 2 AM UTC)
        self.add_cron_job(
            job_id="qa_weekly_audit",
            func=self._run_qa_weekly_audit,
            cron="0 2 * * 0",
            description="Weekly automated QA audit of startup websites",
        )
        
        # Autonomous System Loop - proactive agent scans (Every hour)
        self.add_interval_job(
            job_id="autonomous_loop",
            func=self._run_autonomous_loop,
            hours=1,
            description="Autonomous agent opportunity scan",
        )
        
        all_jobs = [
            "isp_daily_driver", "isp_weekly_reports",
            "evaluate_triggers", "sync_integrations", "daily_summary", "hourly_hunter",
            "content_daily_post", "competitor_weekly_scan", "growth_social_scan",
            "overdue_goals_nag", "reddit_sniper_scan", "morning_brief", "qa_weekly_audit",
            "autonomous_loop",
        ]
        logger.info("Default jobs registered", jobs=all_jobs, total=len(all_jobs))
    
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
        """Generate daily AI summaries and morning briefs for all startups"""
        logger.info("Starting daily summary + morning brief generation")
        
        try:
            from app.services.morning_brief import morning_brief_service
            
            await morning_brief_service.generate_daily_brief()
            
            logger.info("Daily summary generation complete (via MorningBriefService)")
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
                        # Phase 5: Check autonomy level
                        autonomy = await self._check_autonomy(startup.id, "sales", db)
                        if autonomy == 0:  # OBSERVER — skip
                            continue

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
                            
                            # Dedup check — skip if we've already found this lead
                            from app.services.agent_memory_service import agent_memory_service
                            is_dup = await agent_memory_service.is_duplicate_lead(
                                startup_id=str(startup.id),
                                company_name=lead_info.get("company_name", "Unknown"),
                                contact_email=lead_info.get("contact_email", ""),
                            )
                            if is_dup:
                                logger.info(f"Skipping duplicate lead: {lead_info.get('company_name')}")
                                continue
                            
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
                            
                            # Register fingerprint
                            await agent_memory_service.register_lead_fingerprint(
                                startup_id=str(startup.id),
                                company_name=lead_info.get("company_name", "Unknown"),
                                contact_email=lead_info.get("contact_email", ""),
                                source_agent="hourly_hunter",
                            )
                        
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

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 5: AUTONOMY LEVEL CHECKER
    # ═══════════════════════════════════════════════════════════════════════

    async def _check_autonomy(self, startup_id, category: str, db) -> int:
        """
        Check the startup's autonomy level for a given action category.
        
        Returns:
            0 = OBSERVER  — skip entirely (information only)
            1 = ADVISOR   — create pending ActionItem for human review
            2 = COPILOT   — act with confirmation (create + auto-approve)
            3 = AUTOPILOT — full autonomy (act immediately)
        
        Defaults to ADVISOR (1) if no settings configured.
        """
        try:
            from app.models.autonomy import StartupAutonomySettings, ActionCategory, AutonomyLevel
            from sqlalchemy import select

            result = await db.execute(
                select(StartupAutonomySettings).where(
                    StartupAutonomySettings.startup_id == startup_id
                )
            )
            settings = result.scalar_one_or_none()

            if not settings:
                return 1  # Default: ADVISOR

            # Emergency brake
            if settings.is_paused:
                logger.info(f"Autonomy PAUSED for startup {startup_id}: {settings.paused_reason}")
                return 0  # OBSERVER — skip all actions

            # Map string category to ActionCategory enum
            try:
                cat = ActionCategory(category)
                return settings.get_level_for_category(cat)
            except ValueError:
                return settings.global_level

        except Exception as e:
            logger.warning(f"Autonomy check failed, defaulting to ADVISOR", error=str(e))
            return 1  # Safe default

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 2: PROACTIVE AGENT JOB HANDLERS
    # ═══════════════════════════════════════════════════════════════════════

    async def _run_content_daily_post(self):
        """
        Auto-generate and schedule a daily content post for every active startup.
        Uses ContentAgent.auto_generate_daily() which finds trends and generates content.
        """
        logger.info("=== Content Daily Post Triggered ===")

        try:
            from app.models.startup import Startup
            from app.core.database import async_session
            from app.models.action_item import ActionItem
            from sqlalchemy import select
            from app.agents.content_agent import content_agent

            async with async_session() as db:
                result = await db.execute(select(Startup).where(Startup.is_active == True))
                startups = result.scalars().all()

                total_posts = 0
                for startup in startups:
                    try:
                        # Phase 5: Check autonomy level
                        autonomy = await self._check_autonomy(startup.id, "content", db)
                        if autonomy == 0:  # OBSERVER — skip
                            continue

                        ctx = {
                            "name": startup.name,
                            "description": startup.description,
                            "industry": startup.industry or "Technology",
                            "tagline": startup.tagline,
                        }

                        content_result = await content_agent.auto_generate_daily(ctx)

                        if content_result.get("success"):
                            body = content_result.get("full_body", "")
                            
                            # Quality gate: only auto-schedule if quality threshold met
                            from app.services.quality_gate import quality_gate
                            gate_result = await quality_gate.evaluate_content(
                                content=body,
                                goal=f"maximize engagement for {startup.industry or 'tech'} startup",
                                target_audience="startup founders and tech professionals",
                                gate_type="content_post",
                            )
                            
                            gate_passed = gate_result.get("approved", False)
                            
                            # Determine status based on autonomy level + quality gate
                            if autonomy >= 3 and gate_passed:  # AUTOPILOT + quality OK
                                item_status = "approved"
                            elif autonomy >= 2 and gate_passed:  # COPILOT + quality OK
                                item_status = "approved"
                            else:  # ADVISOR or gate failed
                                item_status = "pending"
                            
                            # Persist as action item
                            item = ActionItem(
                                startup_id=startup.id,
                                source_agent="ContentAgent",
                                title=f"Daily Post: {content_result.get('topic', 'New Content')}",
                                description=body[:500],
                                priority="medium",
                                payload={**content_result, "quality_gate": gate_result, "autonomy_level": autonomy},
                                status=item_status,
                            )
                            db.add(item)
                            total_posts += 1

                            # Only auto-schedule if quality gate passed
                            if item_status == "approved":
                                try:
                                    from app.services.social_scheduler import social_scheduler
                                    await social_scheduler.schedule_post(
                                        startup_id=str(startup.id),
                                        content=body,
                                        platforms=[content_result.get("platform", "linkedin")],
                                        scheduled_at=datetime.utcnow(),
                                    )
                                    logger.info(f"Content auto-approved (score: {gate_result.get('score')}, autonomy: {autonomy})")
                                except Exception as e:
                                    logger.warning("Content scheduling failed", error=str(e))
                            else:
                                logger.info(f"Content held for review (score: {gate_result.get('score')}, autonomy: {autonomy})")

                    except Exception as e:
                        logger.error(f"Content generation failed for {startup.name}", error=str(e))

                await db.commit()
                logger.info(f"Content Daily Post complete. Generated {total_posts} posts.")

        except Exception as e:
            logger.error("Content Daily Post failed", error=str(e))

    async def _run_competitor_weekly_scan(self):
        """
        Weekly competitor intelligence scan for all startups.
        Uses CompetitorIntelAgent.monitor_market() for discovery or surveillance.
        """
        logger.info("=== Competitor Weekly Scan Triggered ===")

        try:
            from app.models.startup import Startup
            from app.core.database import async_session
            from app.models.action_item import ActionItem
            from sqlalchemy import select
            from app.agents.competitor_intel_agent import competitor_intel_agent

            async with async_session() as db:
                result = await db.execute(select(Startup).where(Startup.is_active == True))
                startups = result.scalars().all()

                total_alerts = 0
                for startup in startups:
                    try:
                        # Phase 5: Check autonomy level
                        autonomy = await self._check_autonomy(startup.id, "competitive", db)
                        if autonomy == 0:
                            continue

                        ctx = {
                            "name": startup.name,
                            "description": startup.description,
                            "industry": startup.industry or "Technology",
                        }
                        settings = dict(startup.settings or {})
                        known_competitors = settings.get("competitors", [])

                        intel = await competitor_intel_agent.monitor_market(ctx, known_competitors)

                        if intel and not intel.get("error"):
                            # Discovery mode: persist new competitors
                            if intel.get("mode") == "discovery" and intel.get("new_competitors"):
                                settings["competitors"] = intel["new_competitors"]
                                startup.settings = settings

                                db.add(ActionItem(
                                    startup_id=startup.id,
                                    source_agent="CompetitorIntel",
                                    title=f"Discovered {len(intel['new_competitors'])} competitors",
                                    description=f"Found: {', '.join(intel['new_competitors'][:5])}",
                                    priority="high",
                                    payload=intel,
                                    status="pending",
                                ))
                                total_alerts += 1

                            # Surveillance mode: persist alerts
                            elif intel.get("mode") == "surveillance" and intel.get("updates"):
                                db.add(ActionItem(
                                    startup_id=startup.id,
                                    source_agent="CompetitorIntel",
                                    title=f"Competitor Alert: {len(intel['updates'])} updates",
                                    description="\n".join(intel["updates"][:5]),
                                    priority="high",
                                    payload=intel,
                                    status="pending",
                                ))
                                total_alerts += 1

                    except Exception as e:
                        logger.error(f"Competitor scan failed for {startup.name}", error=str(e))

                await db.commit()
                logger.info(f"Competitor Weekly Scan complete. {total_alerts} alerts generated.")

        except Exception as e:
            logger.error("Competitor Weekly Scan failed", error=str(e))

    async def _run_growth_social_scan(self):
        """
        Scan social platforms for growth opportunities for all startups.
        Uses GrowthHackerAgent.monitor_social() to find relevant discussions.
        """
        logger.info("=== Growth Social Scan Triggered ===")

        try:
            from app.models.startup import Startup
            from app.core.database import async_session
            from app.models.action_item import ActionItem
            from sqlalchemy import select
            from app.agents.growth_hacker_agent import growth_hacker_agent

            async with async_session() as db:
                result = await db.execute(select(Startup).where(Startup.is_active == True))
                startups = result.scalars().all()

                total_opps = 0
                for startup in startups:
                    try:
                        # Phase 5: Check autonomy level
                        autonomy = await self._check_autonomy(startup.id, "marketing", db)
                        if autonomy == 0:
                            continue
                        # Build keywords from startup context
                        keywords = [
                            startup.name,
                            startup.industry or "Technology",
                        ]
                        if startup.tagline:
                            keywords.extend(startup.tagline.split()[:3])

                        growth_result = await growth_hacker_agent.monitor_social(
                            keywords=keywords,
                            platform="reddit",
                            limit=3,
                        )

                        opportunities = growth_result.get("opportunities", [])
                        if opportunities:
                            db.add(ActionItem(
                                startup_id=startup.id,
                                source_agent="GrowthHacker",
                                title=f"Found {len(opportunities)} social opportunities",
                                description="\n".join(
                                    f"- {o.get('summary', 'Thread')} ({o.get('url', '')})"
                                    for o in opportunities[:5]
                                ),
                                priority="medium",
                                payload=growth_result,
                                status="pending",
                            ))
                            total_opps += len(opportunities)

                    except Exception as e:
                        logger.error(f"Growth scan failed for {startup.name}", error=str(e))

                await db.commit()
                logger.info(f"Growth Social Scan complete. {total_opps} opportunities found.")

        except Exception as e:
            logger.error("Growth Social Scan failed", error=str(e))

    async def _run_overdue_goals_nag(self):
        """
        Check all startups for overdue goals and notify founders.
        Uses GoalTracker.get_overdue_goals().
        """
        logger.info("=== Overdue Goals Nag Triggered ===")

        try:
            from app.models.startup import Startup
            from app.models.user import User
            from app.core.database import async_session
            from sqlalchemy import select
            from app.services.goal_tracker import goal_tracker
            from app.services.notification_service import notification_service

            async with async_session() as db:
                result = await db.execute(select(Startup).where(Startup.is_active == True))
                startups = result.scalars().all()

                nagged = 0
                for startup in startups:
                    try:
                        overdue = await goal_tracker.get_overdue_goals(str(startup.id))

                        if overdue:
                            user_result = await db.execute(
                                select(User).where(User.id == startup.owner_id)
                            )
                            owner = user_result.scalar_one_or_none()

                            if owner:
                                goal_names = ", ".join(g.name for g in overdue[:5])
                                await notification_service.notify_user(
                                    user=owner,
                                    subject=f"⚠️ {len(overdue)} Overdue Goals for {startup.name}",
                                    body=f"These goals are past their deadline: {goal_names}. Time to act!",
                                    action_url=f"https://app.momentaic.com/startups/{startup.id}/goals",
                                    db=db,
                                )
                                nagged += 1

                    except Exception as e:
                        logger.error(f"Goal nag failed for {startup.name}", error=str(e))

                logger.info(f"Overdue Goals Nag complete. Nagged {nagged} founders.")

        except Exception as e:
            logger.error("Overdue Goals Nag failed", error=str(e))

    async def _run_reddit_sniper_scan(self):
        """
        Reddit Sniper: Find high-intent threads for narrative marketing.
        Uses RedditSniperAgent.find_relationship_opportunities().
        """
        logger.info("=== Reddit Sniper Scan Triggered ===")

        try:
            from app.models.startup import Startup
            from app.core.database import async_session
            from app.models.action_item import ActionItem
            from sqlalchemy import select
            from app.agents.guerrilla.reddit_sniper_agent import reddit_sniper

            async with async_session() as db:
                result = await db.execute(select(Startup).where(Startup.is_active == True))
                startups = result.scalars().all()

                total_threads = 0
                for startup in startups:
                    try:
                        # Phase 5: Check autonomy level
                        autonomy = await self._check_autonomy(startup.id, "marketing", db)
                        if autonomy == 0:
                            continue
                        product_ctx = {
                            "name": startup.name,
                            "description": startup.description,
                            "industry": startup.industry or "Technology",
                        }

                        # Find opportunities
                        sniper_result = await reddit_sniper.find_relationship_opportunities(limit=3)

                        threads = []
                        if hasattr(sniper_result, 'threads'):
                            threads = sniper_result.threads
                        elif isinstance(sniper_result, dict):
                            threads = sniper_result.get("threads", [])

                        if threads:
                            # Draft value-first comments for top threads
                            drafts = []
                            for thread in threads[:2]:
                                try:
                                    draft = await reddit_sniper.draft_value_first_comment(
                                        thread=thread,
                                        product_context=product_ctx,
                                    )
                                    drafts.append(draft)
                                except Exception:
                                    pass

                            db.add(ActionItem(
                                startup_id=startup.id,
                                source_agent="RedditSniper",
                                title=f"Reddit: {len(threads)} high-intent threads found",
                                description="Threads ready for narrative marketing. Review drafts before posting.",
                                priority="medium",
                                payload={"threads": [t.__dict__ if hasattr(t, '__dict__') else t for t in threads], "drafts": drafts},
                                status="pending",
                            ))
                            total_threads += len(threads)

                    except Exception as e:
                        logger.error(f"Reddit scan failed for {startup.name}", error=str(e))

                await db.commit()
                logger.info(f"Reddit Sniper Scan complete. {total_threads} threads found.")

        except Exception as e:
            logger.error("Reddit Sniper Scan failed", error=str(e))

    async def _run_morning_brief(self):
        """
        Generate and send morning brief to all founders.
        Delegates to MorningBriefService which runs Sales, Marketing,
        CompetitorIntel, and Acquisition agents.
        """
        logger.info("=== Morning Brief Triggered ===")

        try:
            from app.services.morning_brief import morning_brief_service
            await morning_brief_service.generate_daily_brief()
            logger.info("Morning Brief complete")
        except Exception as e:
            logger.error("Morning Brief failed", error=str(e))

    async def _run_qa_weekly_audit(self):
        """
        Weekly automated QA audit of startup websites.
        Uses QATesterAgent.run_full_audit() to check for bugs, accessibility, UX.
        """
        logger.info("=== QA Weekly Audit Triggered ===")

        try:
            from app.models.startup import Startup
            from app.core.database import async_session
            from app.models.action_item import ActionItem
            from sqlalchemy import select
            from app.agents.qa_tester_agent import qa_tester_agent

            async with async_session() as db:
                result = await db.execute(select(Startup).where(Startup.is_active == True))
                startups = result.scalars().all()

                audited = 0
                for startup in startups:
                    try:
                        # Phase 5: Check autonomy level
                        autonomy = await self._check_autonomy(startup.id, "operations", db)
                        if autonomy == 0:
                            continue
                        # Get URL from settings or construct default
                        settings = dict(startup.settings or {})
                        url = settings.get("website_url") or settings.get("url")

                        if not url:
                            continue

                        # Run full audit
                        report = await qa_tester_agent.run_full_audit(
                            url=url,
                            mode="full",
                            personality="professional",
                        )

                        if report and not getattr(report, 'error', None):
                            report_dict = report.to_dict() if hasattr(report, 'to_dict') else report

                            db.add(ActionItem(
                                startup_id=startup.id,
                                source_agent="QATester",
                                title=f"QA Audit: Score {report_dict.get('overall_score', 'N/A')}/100",
                                description=f"Bugs: {report_dict.get('bugs_found', 0)}, Improvements: {report_dict.get('improvements_suggested', 0)}",
                                priority="high" if report_dict.get('overall_score', 100) < 70 else "medium",
                                payload=report_dict,
                                status="pending",
                            ))
                            audited += 1

                    except Exception as e:
                        logger.error(f"QA audit failed for {startup.name}", error=str(e))
                    finally:
                        # Always cleanup browser
                        try:
                            await qa_tester_agent.close()
                        except Exception:
                            pass

                await db.commit()
                logger.info(f"QA Weekly Audit complete. Audited {audited} websites.")

        except Exception as e:
            logger.error("QA Weekly Audit failed", error=str(e))

    async def _run_autonomous_loop(self):
        """
        Execute the Autonomous System Loop for proactive agent actions.
        """
        logger.info("=== Autonomous System Loop Triggered ===")
        try:
            from app.services.autonomous_loop import autonomous_loop
            await autonomous_loop.run_scan_cycle()
        except Exception as e:
            logger.error("Autonomous System Loop failed", error=str(e))


# Singleton instance
scheduler = SchedulerService()


def get_scheduler() -> SchedulerService:
    """Get the scheduler instance"""
    return scheduler
