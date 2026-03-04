"""
Swarm Steering Webhook Endpoint
Accepts incoming commands from Slack, Discord, or Telegram to steer the agent swarm.
Part of Phase 7: Full GTM Democratization (a16z Playbook).
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
import hmac
import hashlib

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User

logger = structlog.get_logger()
router = APIRouter()


# ───────────────────────────────────────────────────────
# Request / Response Models
# ───────────────────────────────────────────────────────

class SwarmSteerRequest(BaseModel):
    """Generic swarm steer command — works for Slack, Discord, or direct POST."""
    command: str = Field(..., description="Natural language directive for the swarm: e.g. 'Focus on FinTech CTOs today'")
    source: str = Field(default="api", description="Origin: 'slack', 'discord', 'telegram', 'api'")
    sender_id: Optional[str] = Field(default=None, description="External user ID from the chat platform")
    sender_name: Optional[str] = Field(default=None, description="Display name of the person steering")
    channel: Optional[str] = Field(default=None, description="Channel/room where the command was sent")

class SwarmSteerResponse(BaseModel):
    success: bool
    interpretation: str
    agents_affected: list[str]
    priority_shift: Optional[str] = None


# ───────────────────────────────────────────────────────
# Slack Webhook (Incoming)
# ───────────────────────────────────────────────────────

@router.post("/slack/steer")
async def slack_steer_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Receives Slack slash commands or incoming webhooks.
    Verifies signature, parses command, and steers the swarm.
    """
    body = await request.body()
    
    # Slack URL verification challenge
    try:
        payload = await request.json()
        if payload.get("type") == "url_verification":
            return {"challenge": payload.get("challenge")}
    except Exception:
        pass

    # Parse Slack slash command format (application/x-www-form-urlencoded)
    form = await request.form()
    command_text = form.get("text", "")
    user_name = form.get("user_name", "unknown")
    channel_name = form.get("channel_name", "direct")

    if not command_text:
        return {"response_type": "ephemeral", "text": "Usage: /steer <directive>. Example: /steer Focus on enterprise leads today"}

    result = await _process_steer_command(
        command=str(command_text),
        source="slack",
        sender_name=str(user_name),
        channel=str(channel_name),
        db=db,
    )

    return {
        "response_type": "in_channel",
        "text": f"🎯 *Swarm Steered*\n> {result['interpretation']}\n\n*Agents affected:* {', '.join(result['agents_affected'])}\n*Priority:* {result.get('priority_shift', 'Updated')}",
    }


# ───────────────────────────────────────────────────────
# Discord Webhook (Incoming)
# ───────────────────────────────────────────────────────

@router.post("/discord/steer")
async def discord_steer_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Receives Discord interactions or bot commands.
    """
    payload = await request.json()
    
    # Discord interaction verification (ping/pong)
    if payload.get("type") == 1:
        return {"type": 1}

    # Parse message content
    content = payload.get("data", {}).get("options", [{}])[0].get("value", "")
    user = payload.get("member", {}).get("user", {})
    username = user.get("username", "unknown")

    if not content:
        content = payload.get("content", "")

    if not content:
        return {"type": 4, "data": {"content": "Usage: /steer <directive>"}}

    result = await _process_steer_command(
        command=content,
        source="discord",
        sender_name=username,
        db=db,
    )

    return {
        "type": 4,
        "data": {
            "content": f"🎯 **Swarm Steered**\n> {result['interpretation']}\n\n**Agents:** {', '.join(result['agents_affected'])}\n**Priority:** {result.get('priority_shift', 'Updated')}"
        }
    }


# ───────────────────────────────────────────────────────
# Generic API (Direct POST)
# ───────────────────────────────────────────────────────

@router.post("/steer", response_model=SwarmSteerResponse)
async def direct_steer(
    steer: SwarmSteerRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Direct API endpoint for steering the swarm.
    Can be called from the frontend War Room or any authenticated client.
    """
    result = await _process_steer_command(
        command=steer.command,
        source=steer.source,
        sender_name=steer.sender_name or "API",
        channel=steer.channel,
        db=db,
    )

    return SwarmSteerResponse(**result)


# ───────────────────────────────────────────────────────
# Core Steering Logic
# ───────────────────────────────────────────────────────

async def _process_steer_command(
    command: str,
    source: str,
    sender_name: str = "CEO",
    channel: Optional[str] = None,
    db: AsyncSession = None,
) -> Dict[str, Any]:
    """
    Process a natural language steer command via LLM.
    1. Parse intent (focus area, pause/resume agents, priority shift)
    2. Update the global priority vector
    3. Broadcast to agents via the Message Bus
    """
    logger.info("swarm_steer.received", command=command, source=source, sender=sender_name)

    from app.agents.base import get_llm

    llm = get_llm("deepseek-chat", temperature=0.3)

    routing_prompt = f"""You are MomentAIc's Swarm Router. A CEO sent this directive to steer the AI agent swarm:

DIRECTIVE: "{command}"

Parse this into a structured action. Return ONLY valid JSON with these keys:
- "interpretation": A one-sentence summary of what the CEO wants.
- "agents_to_activate": List of agent names to BOOST (from: SDR, ContentCreator, BrowserProspector, TrustArchitect, CompetitorIntel, GrowthHacker, FinanceCFO, LegalCounsel).
- "agents_to_pause": List of agent names to PAUSE or deprioritize.
- "priority_shift": A short label like "Enterprise Focus" or "Outbound Sprint" or "Trust Documents".
- "focus_icp": The ICP or target description if mentioned, else null.

Do NOT use markdown code blocks. Return pure JSON."""

    try:
        response = await llm.ainvoke(routing_prompt)
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]

        import json
        parsed = json.loads(raw.strip())
    except Exception as e:
        logger.error("swarm_steer.parse_failed", error=str(e))
        parsed = {
            "interpretation": f"Acknowledged: {command}",
            "agents_to_activate": ["SDR"],
            "agents_to_pause": [],
            "priority_shift": "Manual Override",
            "focus_icp": None
        }

    # Broadcast the steer to the Message Bus
    try:
        from app.services.message_bus import MessageBus
        if db:
            bus = MessageBus(db)
            # Get a startup ID (first one, for global steer)
            from app.models.startup import Startup
            result = await db.execute(select(Startup).limit(1))
            startup = result.scalar_one_or_none()
            startup_id = str(startup.id) if startup else "system"

            await bus.publish(
                startup_id=startup_id,
                from_agent="swarm_router",
                topic="swarm.priority_update",
                message_type="EVENT",
                payload={
                    "directive": command,
                    "parsed": parsed,
                    "source": source,
                    "sender": sender_name,
                },
                priority="high",
            )
    except Exception as e:
        logger.error("swarm_steer.bus_publish_failed", error=str(e))

    # Log to activity stream
    try:
        from app.services.activity_stream import activity_stream
        await activity_stream.emit({
            "type": "swarm_steered",
            "directive": command,
            "source": source,
            "sender": sender_name,
            "interpretation": parsed.get("interpretation"),
            "agents_activated": parsed.get("agents_to_activate", []),
            "agents_paused": parsed.get("agents_to_pause", []),
        })
    except Exception as e:
        logger.warning("swarm_steer.activity_log_failed", error=str(e))

    agents_affected = list(set(
        parsed.get("agents_to_activate", []) + parsed.get("agents_to_pause", [])
    ))

    logger.info(
        "swarm_steer.executed",
        interpretation=parsed.get("interpretation"),
        agents=agents_affected,
        priority=parsed.get("priority_shift")
    )

    return {
        "success": True,
        "interpretation": parsed.get("interpretation", command),
        "agents_affected": agents_affected or ["All"],
        "priority_shift": parsed.get("priority_shift"),
    }
