"""
Agent Output Persistence Service
Saves super agent outputs to the database via the AgentOutcome model.
"""

import time
import json
import structlog
from typing import Dict, Any, Optional
from datetime import datetime

logger = structlog.get_logger()


async def save_agent_outcome(
    agent_name: str,
    action_type: str,
    input_context: Dict[str, Any],
    output_data: Dict[str, Any],
    startup_id: Optional[str] = None,
    user_id: Optional[str] = None,
    execution_time_ms: int = 0,
    tokens_used: int = 0,
):
    """
    Persist an agent's output to the database.
    Gracefully fails if DB is unavailable (agent continues working regardless).
    
    Args:
        agent_name: e.g. "GrowthSuperAgent"
        action_type: e.g. "viral_campaign", "sales_hunt"
        input_context: What was fed to the agent
        output_data: What the agent produced
        startup_id: UUID of the startup (optional)
        user_id: UUID of the user who triggered it (optional)
        execution_time_ms: How long it took
        tokens_used: Estimated token cost
    """
    try:
        from app.core.database import async_session_maker
        from app.models.agent_memory import AgentOutcome
        import uuid
        
        # Sanitize output_data — convert non-serializable objects
        clean_output = _sanitize_for_json(output_data)
        clean_input = _sanitize_for_json(input_context)
        
        async with async_session_maker() as db:
            outcome = AgentOutcome(
                startup_id=uuid.UUID(startup_id) if startup_id else uuid.uuid4(),
                agent_name=agent_name,
                action_type=action_type,
                input_context=clean_input,
                output_data=clean_output,
                execution_time_ms=execution_time_ms,
                tokens_used=tokens_used,
            )
            db.add(outcome)
            await db.commit()
            
        logger.info(
            "Agent outcome persisted",
            agent=agent_name,
            action=action_type,
            execution_ms=execution_time_ms,
        )
    except Exception as e:
        # Never let persistence failure crash the agent
        logger.warning(
            "Failed to persist agent outcome (non-fatal)",
            agent=agent_name,
            action=action_type,
            error=str(e),
        )


def _sanitize_for_json(data: Any) -> Any:
    """Convert non-serializable objects to JSON-safe types."""
    if isinstance(data, dict):
        return {k: _sanitize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_sanitize_for_json(v) for v in data]
    elif hasattr(data, 'content'):  # LangChain message objects
        return str(data.content)
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, (str, int, float, bool, type(None))):
        return data
    else:
        return str(data)
