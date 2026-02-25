"""
Agent Memory Service — Phase 3
Provides read/write access to persistent agent memory, outcome tracking,
and lead deduplication for all autonomous agents.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import time

logger = structlog.get_logger()


class AgentMemoryService:
    """
    Central service for agent memory operations.
    Agents use this to:
    - Record outcomes (what they did and whether it worked)
    - Read/write memories (persist context between runs)
    - Deduplicate leads (prevent re-contacting the same lead)
    """

    # ─── OUTCOME TRACKING ───

    async def record_outcome(
        self,
        startup_id: str,
        agent_name: str,
        action_type: str,
        input_context: Dict[str, Any],
        output_data: Dict[str, Any],
        tokens_used: int = 0,
        execution_time_ms: int = 0,
    ) -> str:
        """Record an agent action for outcome tracking. Returns outcome_id."""
        try:
            from app.core.database import async_session
            from app.models.agent_memory import AgentOutcome
            from uuid import UUID

            async with async_session() as db:
                outcome = AgentOutcome(
                    startup_id=UUID(startup_id) if isinstance(startup_id, str) else startup_id,
                    agent_name=agent_name,
                    action_type=action_type,
                    input_context=input_context,
                    output_data=output_data,
                    tokens_used=tokens_used,
                    execution_time_ms=execution_time_ms,
                )
                db.add(outcome)
                await db.commit()
                await db.refresh(outcome)

                logger.info(
                    "Outcome recorded",
                    agent=agent_name,
                    action=action_type,
                    outcome_id=str(outcome.id),
                )
                
                # Broadcast real-time activity
                from app.core.websocket import websocket_manager
                # We do not block the DB transaction on websocket delivery
                payload = {
                    "type": "agent_action",
                    "agent": agent_name,
                    "action": f"Executed action: {action_type}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                asyncio.create_task(websocket_manager.broadcast_to_startup(str(startup_id), payload))
                
                return str(outcome.id)

        except Exception as e:
            logger.error("Failed to record outcome", error=str(e))
            return ""

    async def resolve_outcome(
        self,
        outcome_id: str,
        status: str,  # "successful", "failed", "neutral"
        metric: str = "",
        value: float = 0.0,
        notes: str = "",
    ):
        """Mark an outcome as resolved with its result."""
        try:
            from app.core.database import async_session
            from app.models.agent_memory import AgentOutcome, OutcomeStatus
            from sqlalchemy import select
            from uuid import UUID

            async with async_session() as db:
                result = await db.execute(
                    select(AgentOutcome).where(AgentOutcome.id == UUID(outcome_id))
                )
                outcome = result.scalar_one_or_none()

                if outcome:
                    outcome.outcome_status = OutcomeStatus(status)
                    outcome.outcome_metric = metric
                    outcome.outcome_value = value
                    outcome.outcome_notes = notes
                    outcome.resolved_at = datetime.utcnow()
                    await db.commit()

                    logger.info("Outcome resolved", outcome_id=outcome_id, status=status)

        except Exception as e:
            logger.error("Failed to resolve outcome", error=str(e))

    async def get_agent_success_rate(
        self,
        startup_id: str,
        agent_name: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get success rate for an agent over the past N days."""
        try:
            from app.core.database import async_session
            from app.models.agent_memory import AgentOutcome, OutcomeStatus
            from sqlalchemy import select, func
            from datetime import timedelta
            from uuid import UUID

            async with async_session() as db:
                cutoff = datetime.utcnow() - timedelta(days=days)
                base_q = select(AgentOutcome).where(
                    AgentOutcome.startup_id == UUID(startup_id),
                    AgentOutcome.agent_name == agent_name,
                    AgentOutcome.created_at >= cutoff,
                )

                result = await db.execute(base_q)
                outcomes = result.scalars().all()

                total = len(outcomes)
                successful = sum(1 for o in outcomes if o.outcome_status == OutcomeStatus.successful)
                failed = sum(1 for o in outcomes if o.outcome_status == OutcomeStatus.failed)

                return {
                    "agent": agent_name,
                    "period_days": days,
                    "total_actions": total,
                    "successful": successful,
                    "failed": failed,
                    "success_rate": round(successful / total * 100, 1) if total > 0 else 0,
                }

        except Exception as e:
            logger.error("Failed to get success rate", error=str(e))
            return {"error": str(e)}

    # ─── AGENT MEMORY ───

    async def remember(
        self,
        startup_id: str,
        agent_name: str,
        key: str,
        value: str,
        memory_type: str = "fact",
        importance: int = 5,
        metadata: Dict[str, Any] = None,
    ):
        """Store or update a memory for an agent."""
        try:
            from app.core.database import async_session
            from app.models.agent_memory import AgentMemoryEntry, MemoryType
            from sqlalchemy import select
            from uuid import UUID

            async with async_session() as db:
                # Check if memory with this key already exists
                result = await db.execute(
                    select(AgentMemoryEntry).where(
                        AgentMemoryEntry.startup_id == UUID(startup_id),
                        AgentMemoryEntry.agent_name == agent_name,
                        AgentMemoryEntry.key == key,
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    existing.value = value
                    existing.importance = importance
                    existing.extra_metadata = metadata or {}
                    existing.updated_at = datetime.utcnow()
                else:
                    mem = AgentMemoryEntry(
                        startup_id=UUID(startup_id),
                        agent_name=agent_name,
                        memory_type=MemoryType(memory_type),
                        key=key,
                        value=value,
                        importance=importance,
                        extra_metadata=metadata or {},
                    )
                    db.add(mem)

                await db.commit()
                logger.debug("Memory stored", agent=agent_name, key=key)

        except Exception as e:
            logger.error("Failed to store memory", error=str(e))

    async def recall(
        self,
        startup_id: str,
        agent_name: str,
        key: str = None,
        memory_type: str = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Recall memories for an agent. Filter by key or type."""
        try:
            from app.core.database import async_session
            from app.models.agent_memory import AgentMemoryEntry, MemoryType
            from sqlalchemy import select, or_
            from uuid import UUID

            async with async_session() as db:
                query = select(AgentMemoryEntry).where(
                    AgentMemoryEntry.startup_id == UUID(startup_id),
                    or_(
                        AgentMemoryEntry.agent_name == agent_name,
                        AgentMemoryEntry.agent_name == "*",  # Global memories
                    ),
                )

                if key:
                    query = query.where(AgentMemoryEntry.key == key)
                if memory_type:
                    query = query.where(AgentMemoryEntry.memory_type == MemoryType(memory_type))

                query = query.order_by(AgentMemoryEntry.importance.desc()).limit(limit)

                result = await db.execute(query)
                memories = result.scalars().all()

                # Update access count
                for mem in memories:
                    mem.access_count += 1
                await db.commit()

                return [
                    {
                        "key": m.key,
                        "value": m.value,
                        "type": m.memory_type.value,
                        "importance": m.importance,
                        "metadata": m.extra_metadata,
                        "created_at": m.created_at.isoformat(),
                    }
                    for m in memories
                ]

        except Exception as e:
            logger.error("Failed to recall memories", error=str(e))
            return []

    async def recall_as_context(
        self,
        startup_id: str,
        agent_name: str,
        limit: int = 10,
    ) -> str:
        """Recall memories formatted as a context string for LLM prompts."""
        memories = await self.recall(startup_id, agent_name, limit=limit)

        if not memories:
            return ""

        lines = ["AGENT MEMORY (from previous runs):"]
        for m in memories:
            lines.append(f"- [{m['type'].upper()}] {m['key']}: {m['value']}")

        return "\n".join(lines)

    # ─── LEAD DEDUPLICATION ───

    async def is_duplicate_lead(
        self,
        startup_id: str,
        company_name: str,
        contact_email: str = "",
    ) -> bool:
        """Check if a lead has already been found for this startup."""
        try:
            from app.core.database import async_session
            from app.models.agent_memory import LeadFingerprint
            from sqlalchemy import select

            fp_hash = LeadFingerprint.compute_hash(startup_id, company_name, contact_email)

            async with async_session() as db:
                result = await db.execute(
                    select(LeadFingerprint).where(LeadFingerprint.fingerprint_hash == fp_hash)
                )
                return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error("Dedup check failed", error=str(e))
            return False  # Allow on error to avoid blocking

    async def register_lead_fingerprint(
        self,
        startup_id: str,
        company_name: str,
        contact_email: str = "",
        source_agent: str = "unknown",
    ):
        """Register a lead fingerprint to prevent future duplicates."""
        try:
            from app.core.database import async_session
            from app.models.agent_memory import LeadFingerprint
            from uuid import UUID

            fp_hash = LeadFingerprint.compute_hash(startup_id, company_name, contact_email)

            async with async_session() as db:
                fp = LeadFingerprint(
                    startup_id=UUID(startup_id),
                    fingerprint_hash=fp_hash,
                    source_agent=source_agent,
                )
                db.add(fp)

                try:
                    await db.commit()
                except Exception:
                    await db.rollback()  # Duplicate hash — already registered

        except Exception as e:
            logger.error("Fingerprint registration failed", error=str(e))


# Singleton
agent_memory_service = AgentMemoryService()
