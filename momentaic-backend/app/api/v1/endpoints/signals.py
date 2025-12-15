"""
Neural Signal Engine Endpoints
Startup health scoring and analytics
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access, require_credits
from app.core.config import settings
from app.models.user import User
from app.models.startup import Startup, Signal
from app.schemas.startup import SignalResponse, SignalRecalcRequest

logger = structlog.get_logger()
router = APIRouter()


async def calculate_signal(
    startup: Startup,
    db: AsyncSession,
    include_github: bool = True,
    include_metrics: bool = True,
) -> Signal:
    """
    Calculate startup health signal.
    
    Components:
    - Tech Velocity: GitHub commit activity
    - PMF Score: User engagement metrics
    - Growth Momentum: MRR/DAU growth rate
    - Runway Health: Burn rate vs runway
    """
    raw_data = {}
    
    # Tech Velocity (from GitHub if connected)
    tech_velocity = 50.0  # Default
    if include_github and startup.github_repo:
        # TODO: Fetch actual GitHub data
        # For now, use mock data
        commits_7d = 45
        commits_prev_7d = 30
        raw_data["commits_7d"] = commits_7d
        raw_data["commits_prev_7d"] = commits_prev_7d
        
        if commits_prev_7d > 0:
            velocity_ratio = commits_7d / commits_prev_7d
            tech_velocity = min(100, velocity_ratio * 50)
        else:
            tech_velocity = 75 if commits_7d > 0 else 25
    
    # PMF Score (from user metrics)
    pmf_score = 50.0
    if include_metrics and startup.metrics:
        dau = startup.metrics.get("dau", 0)
        mau = startup.metrics.get("mau", 0)
        nps = startup.metrics.get("nps", 0)
        
        raw_data["dau"] = dau
        raw_data["mau"] = mau
        raw_data["nps"] = nps
        
        # DAU/MAU ratio (stickiness)
        if mau > 0:
            stickiness = (dau / mau) * 100
            pmf_score = min(100, stickiness * 2 + (nps + 100) / 4)
    
    # Growth Momentum
    growth_momentum = 50.0
    if include_metrics and startup.metrics:
        mrr = startup.metrics.get("mrr", 0)
        mrr_prev = startup.metrics.get("mrr_prev_month", mrr)
        
        raw_data["mrr"] = mrr
        raw_data["mrr_prev_month"] = mrr_prev
        
        if mrr_prev > 0:
            mrr_growth = ((mrr - mrr_prev) / mrr_prev) * 100
            growth_momentum = min(100, 50 + mrr_growth * 2)
    
    # Runway Health
    runway_health = 50.0
    if include_metrics and startup.metrics:
        runway_months = startup.metrics.get("runway_months", 12)
        burn_rate = startup.metrics.get("burn_rate", 0)
        
        raw_data["runway_months"] = runway_months
        raw_data["burn_rate"] = burn_rate
        
        if runway_months >= 18:
            runway_health = 100
        elif runway_months >= 12:
            runway_health = 80
        elif runway_months >= 6:
            runway_health = 50
        else:
            runway_health = max(10, runway_months * 8)
    
    # Overall Score (weighted average)
    overall_score = (
        tech_velocity * 0.25 +
        pmf_score * 0.30 +
        growth_momentum * 0.30 +
        runway_health * 0.15
    )
    
    # AI Insights (would use LLM in production)
    ai_insights = generate_insights(
        tech_velocity, pmf_score, growth_momentum, runway_health, startup
    )
    
    # Recommendations
    recommendations = generate_recommendations(
        tech_velocity, pmf_score, growth_momentum, runway_health
    )
    
    # Create signal record
    signal = Signal(
        startup_id=startup.id,
        tech_velocity=round(tech_velocity, 2),
        pmf_score=round(pmf_score, 2),
        growth_momentum=round(growth_momentum, 2),
        runway_health=round(runway_health, 2),
        overall_score=round(overall_score, 2),
        raw_data=raw_data,
        ai_insights=ai_insights,
        recommendations=recommendations,
    )
    
    return signal


def generate_insights(
    tech_velocity: float,
    pmf_score: float,
    growth_momentum: float,
    runway_health: float,
    startup: Startup,
) -> str:
    """Generate AI insights based on scores"""
    
    insights = []
    
    if tech_velocity >= 75:
        insights.append(f"Strong development velocity - {startup.name} is shipping rapidly.")
    elif tech_velocity < 40:
        insights.append("Development pace has slowed. Consider reviewing sprint commitments.")
    
    if pmf_score >= 70:
        insights.append("Product-market fit indicators are healthy. Users are engaged.")
    elif pmf_score < 40:
        insights.append("User engagement metrics suggest PMF needs work. Focus on retention.")
    
    if growth_momentum >= 75:
        insights.append("Excellent growth trajectory! MRR is accelerating.")
    elif growth_momentum < 40:
        insights.append("Growth has stalled. Time to experiment with new channels.")
    
    if runway_health < 50:
        insights.append("⚠️ Runway is becoming a concern. Consider fundraising timeline.")
    
    return " ".join(insights) if insights else "Startup health is stable. Keep building!"


def generate_recommendations(
    tech_velocity: float,
    pmf_score: float,
    growth_momentum: float,
    runway_health: float,
) -> List[str]:
    """Generate actionable recommendations"""
    
    recs = []
    
    if tech_velocity < 50:
        recs.append("Increase shipping cadence - try weekly releases")
    
    if pmf_score < 50:
        recs.append("Schedule 10 customer interviews this week")
        recs.append("Analyze churned users for patterns")
    
    if growth_momentum < 50:
        recs.append("Test 3 new acquisition channels")
        recs.append("Review pricing strategy")
    
    if runway_health < 50:
        recs.append("Start fundraising conversations")
        recs.append("Identify 20% cost reduction opportunities")
    
    if not recs:
        recs.append("Continue current strategy - metrics look healthy")
        recs.append("Consider documenting what's working for future reference")
    
    return recs[:5]  # Max 5 recommendations


@router.get("/{startup_id}", response_model=SignalResponse)
async def get_signals(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """
    Get latest signal scores for a startup.
    
    If signals are stale (>24h), triggers background recalculation.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Get latest signal
    result = await db.execute(
        select(Signal)
        .where(Signal.startup_id == startup_id)
        .order_by(Signal.calculated_at.desc())
        .limit(1)
    )
    signal = result.scalar_one_or_none()
    
    # Check if stale or missing
    is_stale = (
        signal is None or
        (datetime.utcnow() - signal.calculated_at) > timedelta(hours=24)
    )
    
    if is_stale:
        # Get startup for recalculation
        result = await db.execute(
            select(Startup).where(Startup.id == startup_id)
        )
        startup = result.scalar_one()
        
        # Calculate new signal
        new_signal = await calculate_signal(startup, db)
        db.add(new_signal)
        await db.flush()
        
        signal = new_signal
        logger.info("Signal recalculated", startup_id=str(startup_id))
    
    return SignalResponse.model_validate(signal)


@router.get("/{startup_id}/history", response_model=List[SignalResponse])
async def get_signal_history(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    days: int = 30,
):
    """
    Get historical signal data for trend analysis.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    since = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(Signal)
        .where(
            Signal.startup_id == startup_id,
            Signal.calculated_at >= since
        )
        .order_by(Signal.calculated_at.desc())
    )
    signals = result.scalars().all()
    
    return [SignalResponse.model_validate(s) for s in signals]


@router.post("/{startup_id}/recalc", response_model=SignalResponse)
async def force_recalculation(
    startup_id: UUID,
    recalc_request: SignalRecalcRequest,
    current_user: User = Depends(require_credits(settings.credit_cost_signal_calc, "Signal recalculation")),
    db: AsyncSession = Depends(get_db),
):
    """
    Force immediate signal recalculation.
    
    Cost: 5 credits
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Get startup
    result = await db.execute(
        select(Startup).where(Startup.id == startup_id)
    )
    startup = result.scalar_one()
    
    # Calculate new signal
    signal = await calculate_signal(
        startup,
        db,
        include_github=recalc_request.include_github,
        include_metrics=recalc_request.include_metrics,
    )
    
    db.add(signal)
    await db.flush()
    
    logger.info(
        "Signal force recalculated",
        startup_id=str(startup_id),
        overall_score=signal.overall_score,
    )
    
    return SignalResponse.model_validate(signal)
