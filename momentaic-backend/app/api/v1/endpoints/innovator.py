from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
import structlog

from app.agents.deep_research_agent import deep_research_agent
from app.agents.growth_hacker_agent import growth_hacker_agent
from app.agents.war_gaming_agent import war_gaming_agent
from app.core.database import get_db

router = APIRouter()
logger = structlog.get_logger()

# Request Models
class DeepResearchRequest(BaseModel):
    topic: str
    depth: int = 3

class GrowthMonitorRequest(BaseModel):
    keywords: List[str]
    platform: str = "reddit"

class WarGameRequest(BaseModel):
    name: str
    description: str
    industry: str
    pain_point: str
    value_prop: str
    price_point: str

# Endpoints

@router.post("/deep-research")
async def trigger_deep_research(request: DeepResearchRequest):
    """
    Trigger a deep research task.
    Note: This is a long-running task. In a real production app, 
    we would use Celery/BackgroundTasks and return a task_id.
    For this demo, we await it (might timeout if >60s) or use BackgroundTasks if we want async.
    Given the user wants to see the result, we'll try to await it but keep depth low, 
    OR better: return the result directly if it's fast enough, otherwise client needs polling.
    Deep Research takes time (reading URLs).
    Let's await it for now as a POC, client will show spinner.
    """
    logger.info("API: Triggering Deep Research", topic=request.topic)
    try:
        result = await deep_research_agent.research_topic(request.topic, depth=request.depth)
        return result
    except Exception as e:
        logger.error("Deep Research API failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/growth-monitor")
async def trigger_growth_monitor(request: GrowthMonitorRequest):
    """
    Trigger growth monitoring.
    """
    logger.info("API: Triggering Growth Monitor", keywords=request.keywords)
    try:
        result = await growth_hacker_agent.monitor_social(
            keywords=request.keywords, 
            platform=request.platform,
            limit=5
        )
        return result
    except Exception as e:
        logger.error("Growth Monitor API failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/war-game")
async def trigger_war_game(request: WarGameRequest):
    """
    Trigger war gaming simulation.
    """
    logger.info("API: Triggering War Game", name=request.name)
    try:
        # Construct context dictionary
        context = request.model_dump()
        result = await war_gaming_agent.simulate_launch(context)
        return result
    except Exception as e:
        logger.error("War Game API failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
