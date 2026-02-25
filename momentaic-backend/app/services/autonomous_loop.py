"""
Autonomous Loop Service
Runs in the background, allowing agents to proactively scan for opportunities 
and execute actions autonomously based on startup context.
"""

import asyncio
import structlog
from typing import Dict, Any, List
import datetime

from app.core.config import settings

logger = structlog.get_logger()

class AutonomousLoopService:
    """
    Manages the periodic triggering of agent proactivity.
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
        """The main periodic loop."""
        # Check every 60 minutes
        interval_seconds = 3600
        
        while self.is_running:
            try:
                await self.run_scan_cycle()
            except Exception as e:
                logger.error("Error in autonomous loop cycle", error=str(e))
                
            # Sleep until next cycle
            await asyncio.sleep(interval_seconds)
            
    async def run_scan_cycle(self):
        """
        Execute one cycle of proactive scanning across all eligible agents
        for active startups.
        
        In a real production app, this would query active workspaces/startups from DB.
        For now, we will simulate a single cycle.
        """
        logger.info("Running Autonomous Scan Cycle", time=datetime.datetime.utcnow().isoformat())
        
        # NOTE: Implement actual database query for active startups here.
        # This is a stub for the architecture.
        active_startups = [
            {"id": "demo_startup_1", "name": "MomentAIc Demo", "industry": "AI SaaS"}
        ]
        
        from app.agents import get_agent
        from app.models.conversation import AgentType
        
        # Consider a subset of truly autonomous agents
        autonomous_types = [
            AgentType.SALES_HUNTER,
            AgentType.CONTENT_CREATOR,
            AgentType.GROWTH_HACKER,
            AgentType.COMPETITOR_INTEL
        ]
        
        for startup in active_startups:
            logger.debug(f"Scanning opportunities for startup: {startup['name']}")
            
            for agent_type in autonomous_types:
                try:
                    agent = get_agent(agent_type.value)
                    if not agent:
                        continue
                        
                    # 1. Check if agent is allowed to act autonomously
                    can_act = await agent.can_act_autonomously()
                    if not can_act:
                        continue
                        
                    # 2. Ask agent to scan for opportunities
                    proposals = await agent.proactive_scan(startup_context=startup)
                    
                    if not proposals:
                        continue
                        
                    logger.info(f"Agent {agent_type} found {len(proposals)} proactive opportunities", startup=startup['name'])
                    
                    # 3. Execute approved actions
                    for attempt in proposals:
                        # In the future, check billing limits or human-in-the-loop approvals here
                        await agent.autonomous_action(attempt, startup_context=startup)
                        
                except Exception as e:
                    logger.error(f"Error during scan for {agent_type}", error=str(e))

# Singleton
autonomous_loop = AutonomousLoopService()
