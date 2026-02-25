"""
A2A Protocol API Endpoints
REST interface for inter-agent messaging, heartbeat monitoring, and Company DNA.
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel

from app.core.database import get_db
from app.models.heartbeat_ledger import HeartbeatLedger, HeartbeatResult
from app.models.agent_message import AgentMessage, A2AMessageType, MessagePriority
from app.services.message_bus import MessageBus
from app.services.company_dna import CompanyDNAService

router = APIRouter(prefix="/a2a", tags=["A2A Protocol"])


# ═══════════════════════════════════════════════════════════════════
# Request/Response Schemas
# ═══════════════════════════════════════════════════════════════════

class PublishMessageRequest(BaseModel):
    startup_id: str
    from_agent: str
    topic: str
    message_type: str = "INSIGHT"
    payload: dict = {}
    to_agent: Optional[str] = None
    priority: str = "medium"
    requires_response: bool = False
    response_deadline_minutes: Optional[int] = None


class MessageResponse(BaseModel):
    id: str
    message_type: str
    from_agent: str
    to_agent: Optional[str]
    topic: str
    priority: str
    payload: dict
    status: str
    created_at: str

    class Config:
        from_attributes = True


class HeartbeatSummary(BaseModel):
    agent_id: str
    total_heartbeats: int
    ok_count: int
    insight_count: int
    action_count: int
    escalation_count: int
    last_heartbeat: Optional[str]


class PulseOverview(BaseModel):
    total_heartbeats_24h: int
    active_agents: int
    pending_escalations: int
    total_insights: int
    agents: list[HeartbeatSummary]


# ═══════════════════════════════════════════════════════════════════
# Message Endpoints
# ═══════════════════════════════════════════════════════════════════

@router.post("/messages", response_model=list[MessageResponse])
async def publish_message(
    req: PublishMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Publish an A2A message to the bus."""
    bus = MessageBus(db)
    messages = await bus.publish(
        startup_id=req.startup_id,
        from_agent=req.from_agent,
        topic=req.topic,
        message_type=req.message_type,
        payload=req.payload,
        to_agent=req.to_agent,
        priority=req.priority,
        requires_response=req.requires_response,
        response_deadline_minutes=req.response_deadline_minutes,
    )
    return [
        MessageResponse(
            id=str(m.id),
            message_type=m.message_type.value,
            from_agent=m.from_agent,
            to_agent=m.to_agent,
            topic=m.topic,
            priority=m.priority.value,
            payload=m.payload,
            status=m.status.value,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]


@router.get("/messages/inbox/{agent_id}")
async def get_inbox(
    agent_id: str,
    startup_id: str = Query(...),
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get the message inbox for an agent."""
    bus = MessageBus(db)
    messages = await bus.get_inbox(
        startup_id=startup_id,
        agent_id=agent_id,
        status=status,
        limit=limit,
    )
    return [
        {
            "id": str(m.id),
            "message_type": m.message_type.value,
            "from_agent": m.from_agent,
            "to_agent": m.to_agent,
            "topic": m.topic,
            "priority": m.priority.value,
            "payload": m.payload,
            "status": m.status.value,
            "thread_id": str(m.thread_id) if m.thread_id else None,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]

@router.get("/war-room/verdicts")
async def get_war_room_verdicts(
    startup_id: str = Query(...),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest War Room debate outputs for the founder dashboard."""
    query = (
        select(AgentMessage)
        .where(
            and_(
                AgentMessage.startup_id == UUID(startup_id),
                AgentMessage.topic == "war_room.verdict"
            )
        )
        .order_by(AgentMessage.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return [
        {
            "id": str(m.id),
            "payload": m.payload,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


@router.get("/messages/thread/{thread_id}")
async def get_thread(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all messages in a thread."""
    bus = MessageBus(db)
    messages = await bus.get_thread(thread_id)
    return [
        {
            "id": str(m.id),
            "message_type": m.message_type.value,
            "from_agent": m.from_agent,
            "to_agent": m.to_agent,
            "topic": m.topic,
            "payload": m.payload,
            "status": m.status.value,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


# ═══════════════════════════════════════════════════════════════════
# Heartbeat / Business Pulse Endpoints
# ═══════════════════════════════════════════════════════════════════

@router.get("/pulse/{startup_id}", response_model=PulseOverview)
async def get_business_pulse(
    startup_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the Business Pulse overview — real-time agent activity dashboard data."""
    from datetime import datetime, timedelta, timezone
    sid = UUID(startup_id)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    # Get all heartbeats in last 24h
    result = await db.execute(
        select(
            HeartbeatLedger.agent_id,
            HeartbeatLedger.result_type,
            func.count().label("count"),
            func.max(HeartbeatLedger.heartbeat_timestamp).label("last_ts"),
        )
        .where(
            and_(
                HeartbeatLedger.startup_id == sid,
                HeartbeatLedger.heartbeat_timestamp >= cutoff,
            )
        )
        .group_by(HeartbeatLedger.agent_id, HeartbeatLedger.result_type)
    )
    rows = result.all()

    # Aggregate per-agent stats
    agent_stats: dict[str, dict] = {}
    for row in rows:
        agent_id = row.agent_id
        if agent_id not in agent_stats:
            agent_stats[agent_id] = {
                "agent_id": agent_id,
                "total_heartbeats": 0,
                "ok_count": 0,
                "insight_count": 0,
                "action_count": 0,
                "escalation_count": 0,
                "last_heartbeat": None,
            }
        stats = agent_stats[agent_id]
        stats["total_heartbeats"] += row.count

        result_type = row.result_type
        if result_type == HeartbeatResult.OK:
            stats["ok_count"] += row.count
        elif result_type == HeartbeatResult.INSIGHT:
            stats["insight_count"] += row.count
        elif result_type == HeartbeatResult.ACTION:
            stats["action_count"] += row.count
        elif result_type == HeartbeatResult.ESCALATION:
            stats["escalation_count"] += row.count

        if row.last_ts:
            ts_str = row.last_ts.isoformat()
            if not stats["last_heartbeat"] or ts_str > stats["last_heartbeat"]:
                stats["last_heartbeat"] = ts_str

    agents = [HeartbeatSummary(**s) for s in agent_stats.values()]

    # Pending escalations
    esc_result = await db.execute(
        select(func.count())
        .select_from(HeartbeatLedger)
        .where(
            and_(
                HeartbeatLedger.startup_id == sid,
                HeartbeatLedger.result_type == HeartbeatResult.ESCALATION,
                HeartbeatLedger.founder_notified == True,
                HeartbeatLedger.founder_response.is_(None),
            )
        )
    )
    pending_esc = esc_result.scalar() or 0

    return PulseOverview(
        total_heartbeats_24h=sum(a.total_heartbeats for a in agents),
        active_agents=len(agents),
        pending_escalations=pending_esc,
        total_insights=sum(a.insight_count for a in agents),
        agents=agents,
    )


@router.get("/pulse/{startup_id}/timeline")
async def get_heartbeat_timeline(
    startup_id: str,
    limit: int = Query(50, le=200),
    result_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get chronological heartbeat timeline for a startup."""
    sid = UUID(startup_id)
    filters = [HeartbeatLedger.startup_id == sid]

    if result_type:
        try:
            rt = HeartbeatResult(result_type)
            filters.append(HeartbeatLedger.result_type == rt)
        except ValueError:
            pass

    result = await db.execute(
        select(HeartbeatLedger)
        .where(and_(*filters))
        .order_by(HeartbeatLedger.heartbeat_timestamp.desc())
        .limit(limit)
    )
    entries = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "agent_id": e.agent_id,
            "result_type": e.result_type.value,
            "checklist_item": e.checklist_item,
            "action_taken": e.action_taken,
            "tokens_used": e.tokens_used,
            "cost_usd": float(e.cost_usd),
            "latency_ms": e.latency_ms,
            "founder_notified": e.founder_notified,
            "timestamp": e.heartbeat_timestamp.isoformat(),
        }
        for e in entries
    ]


# ═══════════════════════════════════════════════════════════════════
# Company DNA Endpoint
# ═══════════════════════════════════════════════════════════════════

@router.get("/dna/{startup_id}")
async def get_company_dna(
    startup_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the Company DNA document for a startup."""
    service = CompanyDNAService()
    dna = await service.get_dna(db, startup_id)
    if not dna:
        raise HTTPException(status_code=404, detail="Startup not found")
    return {"startup_id": startup_id, "dna": dna}
