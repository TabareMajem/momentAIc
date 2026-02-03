"""
Proactive Agent Scheduler
APScheduler integration for proactive agent triggers
"""

import structlog
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings

logger = structlog.get_logger()

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def run_morning_briefing():
    """
    Run the Morning Briefing job for all active startups.
    Generates daily KPI reports and sends them via email.
    """
    logger.info("Running Morning Briefing job")
    
    # Import here to avoid circular imports
    from app.core.database import async_session_maker
    from sqlalchemy import select
    from app.models.startup import Startup
    from app.models.autonomy import StartupAutonomySettings, AutonomyLevel
    
    async with async_session_maker() as db:
        # Get all startups with autonomy settings that are not paused
        result = await db.execute(
            select(Startup, StartupAutonomySettings)
            .join(StartupAutonomySettings, Startup.id == StartupAutonomySettings.startup_id)
            .where(StartupAutonomySettings.is_paused == False)
        )
        startups_with_settings = result.all()
        
        for startup, settings in startups_with_settings:
            # Check if finance reporting is enabled (Level 0+ allows infomration)
            level = settings.get_level_for_category("finance")
            if level >= AutonomyLevel.OBSERVER:
                try:
                    await generate_morning_briefing(startup, settings, db)
                except Exception as e:
                    logger.error("Morning briefing failed", startup_id=str(startup.id), error=str(e))
        
        await db.commit()


async def generate_morning_briefing(startup, settings, db):
    """Generate and send a morning briefing for a startup"""
    from app.agents import finance_cfo_agent
    from app.models.autonomy import ProactiveActionLog, ActionCategory, ActionStatus
    import json
    
    # Create action log entry
    action = ProactiveActionLog(
        startup_id=startup.id,
        agent_type="finance_cfo",
        action_type="morning_briefing",
        category=ActionCategory.FINANCE,
        title=f"Daily KPI Report - {startup.name}",
        description="Automated morning briefing with key metrics",
        autonomy_level_used=settings.get_level_for_category(ActionCategory.FINANCE),
        status=ActionStatus.EXECUTED,
    )
    
    try:
        # Generate the briefing content
        startup_context = {
            "name": startup.name,
            "metrics": startup.metrics or {},
            "stage": startup.stage.value,
        }
        
        result = await finance_cfo_agent.process(
            message="Generate a daily morning briefing with key metrics and insights for today.",
            startup_context=startup_context,
            user_id=str(startup.owner_id),
        )
        
        action.result = json.dumps(result)
        
        # If notify_on_action is enabled, send email
        if settings.notify_on_action:
            from app.services.email_service import email_service
            from app.models.user import User
            from sqlalchemy import select
            
            user_result = await db.execute(select(User).where(User.id == startup.owner_id))
            user = user_result.scalar_one_or_none()
            if user:
                await email_service.send_notification_email(
                    to_email=user.email,
                    subject=f"☀️ Morning Briefing: {startup.name}",
                    body=result.get("response", "Your daily briefing is ready."),
                )
        
        logger.info("Morning briefing generated", startup_id=str(startup.id))
        
    except Exception as e:
        action.status = ActionStatus.FAILED
        action.error = str(e)
        raise
    finally:
        db.add(action)


async def run_trend_scan():
    """
    Run the Trend Scan job to identify viral topics.
    Runs every hour.
    """
    logger.info("Running Trend Scan job")
    
    from app.core.database import async_session_maker
    from sqlalchemy import select
    from app.models.startup import Startup
    from app.models.autonomy import StartupAutonomySettings, AutonomyLevel, ActionCategory
    
    async with async_session_maker() as db:
        result = await db.execute(
            select(Startup, StartupAutonomySettings)
            .join(StartupAutonomySettings, Startup.id == StartupAutonomySettings.startup_id)
            .where(StartupAutonomySettings.is_paused == False)
        )
        startups_with_settings = result.all()
        
        for startup, settings in startups_with_settings:
            level = settings.get_level_for_category(ActionCategory.MARKETING)
            if level >= AutonomyLevel.OBSERVER:
                try:
                    await scan_trends_for_startup(startup, settings, level, db)
                except Exception as e:
                    logger.error("Trend scan failed", startup_id=str(startup.id), error=str(e))
        
        await db.commit()


async def scan_trends_for_startup(startup, settings, level, db):
    """Scan trends and optionally draft content"""
    from app.agents import growth_hacker_agent
    from app.models.autonomy import ProactiveActionLog, ActionCategory, ActionStatus, AutonomyLevel
    import json
    
    action = ProactiveActionLog(
        startup_id=startup.id,
        agent_type="growth_hacker",
        action_type="trend_scan",
        category=ActionCategory.MARKETING,
        title=f"Trend Scan - {startup.industry}",
        autonomy_level_used=level,
    )
    
    try:
        startup_context = {
            "name": startup.name,
            "industry": startup.industry,
        }
        
        result = await growth_hacker_agent.process(
            message=f"Scan current trends in {startup.industry} and identify opportunities for content.",
            startup_context=startup_context,
            user_id=str(startup.owner_id),
        )
        
        action.result = json.dumps(result)
        action.status = ActionStatus.EXECUTED
        
        # If Level 1+, also draft content (but don't publish)
        if level >= AutonomyLevel.ADVISOR:
            action.description = "Trend identified. Content draft created."
        else:
            action.description = "Trends identified. Review available in dashboard."
        
        logger.info("Trend scan complete", startup_id=str(startup.id))
        
    except Exception as e:
        action.status = ActionStatus.FAILED
        action.error = str(e)
        raise
    finally:
        db.add(action)


def setup_scheduler():
    """Configure and start the scheduler"""
    # Morning Briefing - 8 AM daily
    scheduler.add_job(
        run_morning_briefing,
        trigger=CronTrigger(hour=8, minute=0),
        id="morning_briefing",
        name="Daily Morning Briefing",
        replace_existing=True,
    )
    
    # Trend Scan - Every hour
    scheduler.add_job(
        run_trend_scan,
        trigger=IntervalTrigger(hours=1),
        id="trend_scan",
        name="Hourly Trend Scan",
        replace_existing=True,
    )
    
    logger.info("Proactive scheduler configured", jobs=len(scheduler.get_jobs()))


def start_scheduler():
    """Start the scheduler"""
    if not scheduler.running:
        scheduler.start()
        logger.info("Proactive scheduler started")


def shutdown_scheduler():
    """Shutdown the scheduler gracefully"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Proactive scheduler stopped")


# FastAPI lifespan integration
@asynccontextmanager
async def scheduler_lifespan(app):
    """Context manager for scheduler lifecycle"""
    setup_scheduler()
    start_scheduler()
    yield
    shutdown_scheduler()
