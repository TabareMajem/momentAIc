"""
Autonomous Loop Service (REAL EXECUTION)
Runs in the background, querying REAL startups from the database,
allowing agents to proactively scan for opportunities
and execute actions autonomously.
"""

import asyncio
import structlog
from typing import Dict, Any, List
import datetime

from app.core.config import settings
from app.services.activity_stream import activity_stream

logger = structlog.get_logger()


class AutonomousLoopService:
    """
    Manages the periodic triggering of agent proactivity.
    Queries REAL startups from the database and dispatches to REAL agents.
    """
    
    def __init__(self):
        self.is_running = False
        self._task = None
    
    async def start(self):
        """Start the background autonomous loop."""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("Starting Autonomous Loop Service")
        self._task = asyncio.create_task(self._loop())
        
    async def stop(self):
        """Stop the background loop."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped Autonomous Loop Service")
        
    async def _loop(self):
        """The main periodic loop. Runs every 2 hours."""
        interval_seconds = 7200  # 2 hours
        
        while self.is_running:
            try:
                await self.run_scan_cycle()
            except Exception as e:
                logger.error("Error in autonomous loop cycle", error=str(e))
                
            await asyncio.sleep(interval_seconds)
            
    async def run_scan_cycle(self):
        """
        Execute one cycle of proactive scanning across all eligible agents
        for REAL active startups from the database.
        """
        logger.info("🔄 Autonomous Scan Cycle: STARTING", time=datetime.datetime.utcnow().isoformat())
        
        # ── REAL DATABASE QUERY ──────────────────────────────────────────
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.startup import Startup
        from app.models.autonomy import StartupAutonomySettings
        
        active_startups = []
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Startup)
                .options(selectinload(Startup.autonomy_settings))
                .limit(100)
            )
            startups = result.scalars().all()
            
            for startup in startups:
                # Skip startups with paused autonomy
                if startup.autonomy_settings and startup.autonomy_settings.is_paused:
                    logger.debug("Skipping paused startup", startup_id=str(startup.id))
                    continue
                
                autonomy_level = 1  # Default: Advisor (suggest only)
                if startup.autonomy_settings:
                    autonomy_level = startup.autonomy_settings.global_level
                
                active_startups.append({
                    "id": str(startup.id),
                    "startup_id": str(startup.id),
                    "name": startup.name,
                    "description": startup.description or "",
                    "industry": startup.industry or "",
                    "target_audience": getattr(startup, "target_audience", ""),
                    "autonomy_level": autonomy_level,
                })
        
        logger.info(f"🔄 Autonomous Scan: Found {len(active_startups)} active startups")
        
        if not active_startups:
            logger.info("No active startups found. Skipping scan cycle.")
            return
        
        # ── REPORT TO ACTIVITY STREAM ────────────────────────────────────
        activity_id = await activity_stream.report_start(
            "AutonomousLoop", 
            f"Scanning {len(active_startups)} startups for proactive opportunities"
        )
        
        # ── AGENT DISPATCH ───────────────────────────────────────────────
        from app.agents import get_agent
        from app.models.conversation import AgentType
        
        autonomous_types = [
            AgentType.SALES_HUNTER,
            AgentType.CONTENT_CREATOR,
            AgentType.GROWTH_HACKER,
            AgentType.COMPETITOR_INTEL,
            AgentType.FINANCE_CFO,
            AgentType.CUSTOMER_SUCCESS,
            AgentType.DATA_ANALYST,
            AgentType.STRATEGY,
            AgentType.LEGAL_COUNSEL,
            AgentType.TECH_LEAD,
            AgentType.QA_TESTER,
            AgentType.HR_OPERATIONS,
            AgentType.PRODUCT_PM,
        ]
        
        total_proposals = 0
        total_executed = 0
        
        for startup in active_startups:
            logger.debug(f"Scanning opportunities for startup: {startup['name']}")
            
            for agent_type in autonomous_types:
                try:
                    agent = get_agent(agent_type.value)
                    if not agent:
                        continue
                    
                    # 1. Proactive scan for opportunities
                    proposals = await agent.proactive_scan(startup_context=startup)
                    
                    if not proposals:
                        continue
                    
                    total_proposals += len(proposals)
                    logger.info(
                        f"Agent {agent_type.value} found {len(proposals)} proactive opportunities",
                        startup=startup['name']
                    )
                    
                    # 2. Execute actions based on autonomy level
                    for proposal in proposals:
                        try:
                            # Autonomy Level Check:
                            # Level 1 (Advisor): Log only, don't execute
                            # Level 2 (Co-Pilot): Execute low-risk, queue high-risk for approval
                            # Level 3 (Autopilot): Execute everything
                            if startup["autonomy_level"] < 2:
                                # Advisor mode: just report the finding
                                await activity_stream.emit({
                                    "type": "agent_proposal",
                                    "agent": agent_type.value,
                                    "startup_id": startup["id"],
                                    "proposal": proposal,
                                    "status": "pending_approval",
                                    "timestamp": datetime.datetime.utcnow().isoformat(),
                                })
                                logger.info(f"[ADVISOR MODE] Proposal queued for approval: {proposal.get('action', 'unknown')}")
                                continue
                            
                            # Co-Pilot or Autopilot: Execute
                            logger.info(f"Executing autonomous action: {proposal}")
                            result = await agent.autonomous_action(proposal, startup_context=startup)
                            total_executed += 1
                            
                            # Log to activity stream
                            await activity_stream.emit({
                                "type": "autonomous_action",
                                "agent": agent_type.value,
                                "startup_id": startup["id"],
                                "action": proposal.get("action", "unknown"),
                                "result": str(result)[:200],
                                "timestamp": datetime.datetime.utcnow().isoformat(),
                            })
                            
                            logger.info(f"Action executed successfully: {result}")
                            
                        except Exception as e:
                            logger.error(f"Action execution failed: {proposal}", error=str(e))
                    
                except Exception as e:
                    logger.error(f"Error during scan for {agent_type}", error=str(e))
        
        # ── REPORT COMPLETION ────────────────────────────────────────────
        await activity_stream.report_complete(activity_id, {
            "startups_scanned": len(active_startups),
            "proposals_found": total_proposals,
            "actions_executed": total_executed,
        })
        
        logger.info(
            "🔄 Autonomous Scan Cycle: COMPLETE",
            startups=len(active_startups),
            proposals=total_proposals,
            executed=total_executed,
        )


# Singleton
autonomous_loop = AutonomousLoopService()
