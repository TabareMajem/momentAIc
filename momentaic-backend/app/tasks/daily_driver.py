"""
Daily Driver - Autonomous Daily Execution Engine
Runs every day at 8 AM to execute action plans for all startups
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import asyncio

logger = structlog.get_logger()


async def run_daily_driver(startup_id: str, startup_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    THE MONEY MAKER - Runs automatically every day for a single startup
    
    Steps:
    1. Pull startup state from Brain
    2. Generate today's action plan
    3. Execute high-priority automated tasks
    4. Queue tasks needing approval
    5. Send founder morning briefing/notification
    """
    from app.agents.startup_brain import startup_brain
    from app.services.goal_tracker import goal_tracker
    
    logger.info("Daily Driver starting", startup_id=startup_id)
    
    try:
        # 1. Analyze current state
        state = await startup_brain.analyze_current_state(startup_id, startup_context)
        
        # 2. Generate action plan
        action_plan = await startup_brain.generate_daily_action_plan(
            startup_id=startup_id,
            max_hours=6.0,  # Focus on high-impact, achievable tasks
            include_non_automated=False  # Only automated tasks for daily driver
        )
        
        logger.info(
            "Action plan generated",
            startup_id=startup_id,
            tasks=len(action_plan.tasks),
            estimated_hours=action_plan.total_estimated_hours
        )
        
        # 3. Execute the plan
        if action_plan.tasks:
            execution_report = await startup_brain.execute_action_plan(
                plan=action_plan,
                startup_context=startup_context
            )
        else:
            execution_report = {
                "tasks_completed": 0,
                "tasks_failed": 0,
                "message": "No automated tasks available for today"
            }
        
        # 4. Generate morning briefing
        briefing = await startup_brain.generate_morning_briefing(
            startup_id=startup_id,
            startup_context=startup_context
        )
        
        # 5. Evaluate progress
        progress = await startup_brain.evaluate_progress(startup_id)
        
        result = {
            "success": True,
            "startup_id": startup_id,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "phase": state.current_phase.value,
            "health_score": state.health_score,
            "action_plan": action_plan.to_dict(),
            "execution_report": execution_report,
            "morning_briefing": briefing,
            "progress": progress
        }
        
        logger.info(
            "Daily Driver completed successfully",
            startup_id=startup_id,
            tasks_completed=execution_report.get("tasks_completed", 0),
            health_score=state.health_score
        )
        
        return result
        
    except Exception as e:
        logger.error("Daily Driver failed", startup_id=startup_id, error=str(e))
        return {
            "success": False,
            "startup_id": startup_id,
            "error": str(e)
        }


async def run_all_daily_drivers() -> Dict[str, Any]:
    """
    Run daily driver for ALL active startups
    
    This is called by the scheduler at 8 AM every day.
    """
    logger.info("=== Starting Daily Driver for ALL Startups ===")
    
    # Get all active startups from database
    try:
        from app.models.startup import Startup
        from app.core.deps import get_db_session
        from sqlalchemy import select
        
        async with get_db_session() as db:
            result = await db.execute(
                select(Startup).where(Startup.is_active == True)
            )
            startups = result.scalars().all()
            
        logger.info(f"Found {len(startups)} active startups")
        
    except Exception as e:
        # If database access fails, try with cached data or return empty
        logger.warning(f"Could not fetch startups from DB: {e}")
        startups = []
    
    results = []
    successful = 0
    failed = 0
    
    for startup in startups:
        try:
            startup_context = {
                "id": str(startup.id),
                "name": startup.name,
                "description": startup.description or "",
                "industry": startup.industry or "Technology",
                "stage": startup.stage or "idea",
                "founder_name": "Founder"  # Could pull from user relation
            }
            
            result = await run_daily_driver(str(startup.id), startup_context)
            results.append(result)
            
            if result.get("success"):
                successful += 1
            else:
                failed += 1
                
        except Exception as e:
            logger.error(f"Failed to run daily driver for startup {startup.id}: {e}")
            failed += 1
            results.append({
                "success": False,
                "startup_id": str(startup.id),
                "error": str(e)
            })
    
    summary = {
        "total_startups": len(startups),
        "successful": successful,
        "failed": failed,
        "timestamp": datetime.utcnow().isoformat(),
        "results": results
    }
    
    logger.info(
        "=== Daily Driver Complete ===",
        total=len(startups),
        successful=successful,
        failed=failed
    )
    
    return summary


async def generate_weekly_reports() -> Dict[str, Any]:
    """
    Generate weekly progress reports for all startups
    
    Called every Monday at 9 AM.
    """
    logger.info("=== Generating Weekly Reports ===")
    
    from app.agents.startup_brain import startup_brain
    
    try:
        from app.models.startup import Startup
        from app.core.deps import get_db_session
        from sqlalchemy import select
        
        async with get_db_session() as db:
            result = await db.execute(
                select(Startup).where(Startup.is_active == True)
            )
            startups = result.scalars().all()
            
    except Exception as e:
        logger.warning(f"Could not fetch startups: {e}")
        return {"success": False, "error": str(e)}
    
    reports = []
    
    for startup in startups:
        try:
            progress = await startup_brain.evaluate_progress(str(startup.id))
            
            reports.append({
                "startup_id": str(startup.id),
                "startup_name": startup.name,
                "progress": progress
            })
            
        except Exception as e:
            logger.error(f"Failed to generate report for {startup.id}: {e}")
    
    return {
        "success": True,
        "week": datetime.utcnow().strftime("%Y-W%W"),
        "reports_generated": len(reports),
        "reports": reports
    }


async def send_founder_notifications(startup_id: str, message: str) -> bool:
    """
    Send notifications to founders (email, Slack, etc.)
    
    This integrates with the notification system.
    """
    try:
        from app.core.deps import get_db_session
        from sqlalchemy import select
        from app.models.startup import Startup
        from app.models.user import User
        from app.services.notification_service import notification_service
        
        async with get_db_session() as db:
            # 1. Get Startup Owner
            result = await db.execute(
                select(Startup).where(Startup.id == startup_id)
            )
            startup = result.scalar_one_or_none()
            
            if not startup:
                logger.error("Notification failed: Startup not found", startup_id=startup_id)
                return False
                
            result = await db.execute(
                select(User).where(User.id == startup.owner_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error("Notification failed: Owner not found", user_id=startup.owner_id)
                return False

            # 2. Send Notification
            # Extract title if message has newlines
            lines = message.strip().split('\n')
            subject = lines[0].replace('**', '').strip()  # Use first line as subject
            
            await notification_service.notify_user(
                user=user,
                subject=subject,
                body=message,
                action_url=f"https://app.momentaic.com/startups/{startup_id}/dashboard",
                db=db
            )
            
            logger.info("Notification sent", user_email=user.email)
            return True
            
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False


# ==================
# Quick Action Helpers
# ==================

async def execute_quick_action(
    startup_id: str,
    action_id: str,
    startup_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a single action immediately (bypass daily driver)
    """
    from app.agents.startup_brain import startup_brain
    
    return await startup_brain.execute_single_action(
        startup_id=startup_id,
        action_id=action_id,
        startup_context=startup_context
    )


async def get_recommended_actions(
    startup_id: str,
    startup_context: Dict[str, Any],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Get recommended next actions for a startup
    """
    from app.agents.startup_brain import startup_brain
    
    state = await startup_brain.analyze_current_state(startup_id, startup_context)
    return state.next_actions[:limit]
