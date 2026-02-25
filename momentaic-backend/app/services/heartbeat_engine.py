"""
Heartbeat Engine — The Autonomic Nervous System
Loads per-agent YAML configs, assembles context, evaluates via LLM, and logs results.
OpenClaw-inspired: transforms agents from passive tools into active participants.
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional

import structlog
import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_maker
from app.models.heartbeat_ledger import HeartbeatLedger, HeartbeatResult
from app.models.startup import Startup

logger = structlog.get_logger()

# Path to heartbeat YAML configs
CONFIGS_DIR = Path(__file__).parent.parent / "heartbeat_configs"


def load_heartbeat_configs() -> list[dict]:
    """Load all heartbeat YAML configs from the configs directory."""
    configs = []
    if not CONFIGS_DIR.exists():
        logger.warning("Heartbeat configs directory not found", path=str(CONFIGS_DIR))
        return configs

    for yaml_file in CONFIGS_DIR.glob("*.yaml"):
        try:
            with open(yaml_file, "r") as f:
                config = yaml.safe_load(f)
            if config and config.get("heartbeat", {}).get("enabled", False):
                configs.append(config)
                logger.debug("Loaded heartbeat config", agent=config.get("agent_id"))
        except Exception as e:
            logger.error("Failed to load heartbeat config", file=str(yaml_file), error=str(e))

    return configs


def is_quiet_hours(config: dict) -> bool:
    """Check if the agent is in quiet hours based on its config."""
    quiet = config.get("heartbeat", {}).get("quiet_hours", {})
    if not quiet.get("enabled", False):
        return False

    tz_name = quiet.get("timezone", "UTC")
    start_str = quiet.get("start", "22:00")
    end_str = quiet.get("end", "07:00")

    now = datetime.now(timezone.utc)
    current_time = now.strftime("%H:%M")

    # Handle overnight quiet hours (e.g., 22:00 - 07:00)
    if start_str > end_str:
        return current_time >= start_str or current_time < end_str
    else:
        return start_str <= current_time < end_str


async def assemble_context(
    agent_id: str,
    checklist: list[dict],
    startup: Any,
    db: AsyncSession,
) -> dict:
    """
    Assemble minimal context for the heartbeat evaluation.
    Pulls startup metrics, recent agent memory, and Company DNA.
    """
    context = {
        "agent_id": agent_id,
        "startup_name": startup.name if startup else "Unknown",
        "startup_stage": startup.stage.value if startup and hasattr(startup, "stage") else "unknown",
        "metrics": startup.metrics if startup and hasattr(startup, "metrics") else {},
        "checklist": checklist,
        "evaluation_time": datetime.now(timezone.utc).isoformat(),
    }

    # Try to load Company DNA if it exists
    try:
        from app.services.company_dna import CompanyDNAService
        dna_service = CompanyDNAService()
        dna = await dna_service.get_dna(db, str(startup.id))
        if dna:
            context["company_dna"] = dna
    except Exception:
        pass  # Company DNA is optional in Phase 1

    return context


async def evaluate_heartbeat(
    agent_id: str,
    context: dict,
    config: dict,
) -> dict:
    """
    Call the LLM to evaluate the heartbeat checklist against context.
    Returns structured response with result_type plus any actions.
    """
    model = config.get("heartbeat", {}).get("budget", {}).get("model_override", "gemini-2.0-flash")

    checklist_text = "\n".join([
        f"- {c['check']}: {c.get('description', '')} "
        f"(threshold: {c.get('threshold', 'none')}, action: {c.get('action', 'none')}, "
        f"escalate_if: {c.get('escalate_if', 'never')})"
        for c in context.get("checklist", [])
    ])

    prompt = f"""You are the {agent_id} heartbeat daemon for startup "{context.get('startup_name', 'Unknown')}".

Current metrics: {json.dumps(context.get('metrics', {}), indent=2)}
Current time: {context.get('evaluation_time')}
Company stage: {context.get('startup_stage', 'unknown')}

Your checklist to evaluate:
{checklist_text}

Evaluate each checklist item against the current context.
Respond with a JSON object:
{{
  "result_type": "OK" | "INSIGHT" | "ACTION" | "ESCALATION",
  "triggered_check": "<which checklist item triggered, or null>",
  "summary": "<brief explanation of what you found>",
  "recommended_action": "<what to do, or null if OK>",
  "should_notify_founder": true/false
}}

If nothing requires attention, return result_type "OK".
If you detect something noteworthy but non-urgent, return "INSIGHT".
If immediate action is within standard guardrails, return "ACTION".
If founder decision is needed, return "ESCALATION".

Respond ONLY with valid JSON, no markdown fences."""

    try:
        from app.agents.base import get_llm
        from langchain_core.messages import HumanMessage

        llm = get_llm(model, temperature=0.2)
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        result_text = response.content.strip()

        # Parse JSON response
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        
        return json.loads(result_text)
    except Exception as e:
        logger.error("Heartbeat LLM evaluation failed", agent=agent_id, error=str(e))
        return {
            "result_type": "OK",
            "triggered_check": None,
            "summary": f"Heartbeat evaluation error: {str(e)}",
            "recommended_action": None,
            "should_notify_founder": False,
        }


async def run_heartbeat_for_agent(agent_config: dict) -> None:
    """
    Execute a full heartbeat cycle for a single agent across all active startups.
    1. Check quiet hours
    2. For each startup: assemble context → evaluate → log
    """
    agent_id = agent_config.get("agent_id", "unknown")
    hb = agent_config.get("heartbeat", {})
    checklist = hb.get("checklist", [])

    if is_quiet_hours(agent_config):
        logger.debug("Agent in quiet hours, skipping", agent=agent_id)
        return

    logger.info("Running heartbeat", agent=agent_id)

    async with async_session_maker() as db:
        # Get all active startups
        result = await db.execute(select(Startup).limit(100))
        startups = result.scalars().all()

        for startup in startups:
            start_time = time.time()
            try:
                # Assemble context
                context = await assemble_context(agent_id, checklist, startup, db)

                # Evaluate via LLM
                evaluation = await evaluate_heartbeat(agent_id, context, agent_config)

                latency_ms = int((time.time() - start_time) * 1000)

                # Map string result to enum
                result_type_str = evaluation.get("result_type", "OK")
                try:
                    result_type = HeartbeatResult(result_type_str)
                except ValueError:
                    result_type = HeartbeatResult.OK

                # Log to ledger
                ledger_entry = HeartbeatLedger(
                    startup_id=startup.id,
                    agent_id=agent_id,
                    result_type=result_type,
                    checklist_item=evaluation.get("triggered_check"),
                    context_snapshot={"metrics_snapshot": context.get("metrics", {})},
                    action_taken=evaluation.get("recommended_action"),
                    action_result=evaluation,
                    tokens_used=0,  # TODO: extract from response metadata
                    cost_usd=0.0,
                    model_used=hb.get("budget", {}).get("model_override", "gemini-2.0-flash"),
                    latency_ms=latency_ms,
                    founder_notified=evaluation.get("should_notify_founder", False),
                )
                db.add(ledger_entry)

                # If ESCALATION or INSIGHT with notify, publish A2A message
                if result_type in (HeartbeatResult.ESCALATION, HeartbeatResult.INSIGHT):
                    try:
                        from app.services.message_bus import MessageBus
                        bus = MessageBus(db)
                        await bus.publish(
                            startup_id=str(startup.id),
                            from_agent=agent_id,
                            topic=f"heartbeat.{result_type.value.lower()}",
                            message_type="INSIGHT" if result_type == HeartbeatResult.INSIGHT else "ALERT",
                            payload={
                                "summary": evaluation.get("summary", ""),
                                "check": evaluation.get("triggered_check", ""),
                                "action": evaluation.get("recommended_action", ""),
                            },
                            priority="high" if result_type == HeartbeatResult.ESCALATION else "medium",
                        )
                    except Exception as bus_err:
                        logger.warning("Failed to publish A2A message", error=str(bus_err))

                logger.info(
                    "Heartbeat complete",
                    agent=agent_id,
                    startup=startup.name,
                    result=result_type.value,
                    latency_ms=latency_ms,
                )

            except Exception as e:
                logger.error(
                    "Heartbeat failed for startup",
                    agent=agent_id,
                    startup_id=str(startup.id),
                    error=str(e),
                )

        await db.commit()


async def run_all_heartbeats() -> None:
    """
    Master heartbeat tick: loads all configs and runs heartbeats for due agents.
    Called by the scheduler on a fixed interval (e.g., every 30 seconds).
    """
    configs = load_heartbeat_configs()
    logger.info("Heartbeat tick", agent_count=len(configs))

    for config in configs:
        try:
            await run_heartbeat_for_agent(config)
        except Exception as e:
            logger.error(
                "Agent heartbeat crashed",
                agent=config.get("agent_id", "unknown"),
                error=str(e),
            )
