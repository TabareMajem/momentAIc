"""
Leaderboard Endpoint
Returns real startup rankings from the database using the Traction Score Engine.
"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.startup import Startup

router = APIRouter()


@router.get("", response_model=dict)
async def get_leaderboard(
    category: str = "all",
    time_period: str = "all",
    db: AsyncSession = Depends(get_db),
):
    """
    Get the Unfair Advantage Leaderboard.
    Pulls real startups from the database, sorted by traction score.
    """
    try:
        # Query startups from DB
        query = select(Startup).limit(50)
        
        result = await db.execute(query)
        startups = result.scalars().all()
        
        if not startups:
            return {"leaderboard": [], "message": "No startups registered yet. Be the first!"}
        
        # Build leaderboard entries from real data
        leaderboard = []
        for idx, startup in enumerate(startups, start=1):
            metrics = startup.metrics if hasattr(startup, "metrics") and startup.metrics else {}
            
            # Calculate a basic traction score from available metrics
            mrr = metrics.get("mrr", 0) or 0
            users = metrics.get("users", 0) or 0
            growth = metrics.get("mrr_growth", 0) or 0
            
            # Simple composite score (0-100)
            traction_score = min(100, int(
                (min(mrr, 50000) / 50000 * 40) +
                (min(users, 10000) / 10000 * 30) +
                (min(growth, 100) / 100 * 30)
            ))
            
            # Determine tier
            if traction_score >= 80:
                tier = "rocket"
            elif traction_score >= 50:
                tier = "scaling"
            elif traction_score >= 20:
                tier = "rising"
            else:
                tier = "building"
            
            leaderboard.append({
                "rank": idx,
                "startup_id": str(startup.id),
                "name": startup.name,
                "tagline": startup.tagline or startup.description or "",
                "traction_score": traction_score,
                "tier": tier,
                "verified": bool(metrics.get("_verified", False)),
                "category": startup.industry or "general",
                "public_metrics": {
                    "mrr": mrr,
                    "growth": growth,
                    "users": users,
                },
                "integrations_connected": metrics.get("integrations_count", 0),
            })
        
        # Sort by traction score descending
        leaderboard.sort(key=lambda x: x["traction_score"], reverse=True)
        
        # Re-rank after sorting
        for idx, entry in enumerate(leaderboard, start=1):
            entry["rank"] = idx
        
        return {"leaderboard": leaderboard}
        
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("Leaderboard query failed", error=str(e))
        return {"leaderboard": [], "error": "Failed to load leaderboard"}
