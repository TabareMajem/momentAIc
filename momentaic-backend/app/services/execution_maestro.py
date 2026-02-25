"""
Execution Maestro — The 'God Mode' Executor (v2 — REAL EXECUTION)
Orchestrates the transition from Strategy → Action by calling REAL agents.
"""

from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime
import uuid
from pydantic import BaseModel
from enum import Enum

from app.models.conversation import AgentType

logger = structlog.get_logger()


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionTask(BaseModel):
    id: str
    agent_type: str
    action: str
    params: Dict[str, Any]
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.now()


class ExecutionPlan(BaseModel):
    id: str
    startup_id: str
    source_context: Dict[str, Any]
    tasks: List[ExecutionTask]
    created_at: datetime = datetime.now()


class ExecutionMaestro:
    """
    The 'God Mode' Executor.
    Converts strategies into executable tasks and dispatches them
    to REAL agents — no simulations, no fakes.
    """

    async def generate_plan_from_strategy(
        self, startup_id: str, strategy: Dict[str, Any], context: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        Converts a high-level Strategy (from GrowthHacker) into executable Tasks.
        Supports: sales hunting, content generation, competitor scanning,
        community engagement, product polish, and more.
        """
        tasks = []

        # 1. Sales Task — Hunt Leads
        if "target_audience" in strategy or "icp" in strategy:
            tasks.append(ExecutionTask(
                id=str(uuid.uuid4()),
                agent_type=AgentType.SALES.value,
                action="hunt_leads",
                params={
                    "target_audience": strategy.get("target_audience", strategy.get("icp", "")),
                    "count": strategy.get("lead_count", 5),
                },
                priority=10,
            ))

        # 2. Marketing Task — Generate Content
        if "viral_post_hook" in strategy or "content_topic" in strategy:
            tasks.append(ExecutionTask(
                id=str(uuid.uuid4()),
                agent_type=AgentType.MARKETING.value,
                action="generate_content",
                params={
                    "topic": strategy.get("viral_post_hook", strategy.get("content_topic", "")),
                    "platform": strategy.get("platform", "linkedin"),
                    "goal": strategy.get("content_goal", "thought_leadership"),
                },
                priority=8,
            ))

        # 3. Competitor Intelligence Scan
        if "competitors" in strategy or "monitor_competitors" in strategy:
            tasks.append(ExecutionTask(
                id=str(uuid.uuid4()),
                agent_type="competitor_intel",
                action="monitor_market",
                params={
                    "known_competitors": strategy.get("competitors", []),
                },
                priority=7,
            ))

        # 4. Growth Experiments
        if "growth_channels" in strategy or "experiment" in str(strategy).lower():
            tasks.append(ExecutionTask(
                id=str(uuid.uuid4()),
                agent_type=AgentType.GROWTH_HACKER.value,
                action="monitor_social",
                params={
                    "keywords": strategy.get("keywords", []),
                    "platform": strategy.get("social_platform", "reddit"),
                },
                priority=6,
            ))

        # 5. Community Outreach
        if "community" in strategy or "ambassador" in str(strategy).lower():
            tasks.append(ExecutionTask(
                id=str(uuid.uuid4()),
                agent_type="community",
                action="engage",
                params={
                    "channels": strategy.get("community_channels", ["discord", "reddit"]),
                },
                priority=5,
            ))

        # 6. QA / Product Polish
        if context.get("url") or strategy.get("audit_url"):
            tasks.append(ExecutionTask(
                id=str(uuid.uuid4()),
                agent_type="qa_tester",
                action="audit_website",
                params={
                    "url": strategy.get("audit_url", context.get("url", "")),
                },
                priority=4,
            ))

        # Sort by priority descending
        tasks.sort(key=lambda t: t.priority, reverse=True)

        return ExecutionPlan(
            id=str(uuid.uuid4()),
            startup_id=startup_id,
            source_context=context,
            tasks=tasks,
        )

    async def execute_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Dispatches tasks to REAL agents. No simulations.
        Tasks are executed sequentially by priority.
        """
        logger.info(
            "Maestro: Executing Plan",
            plan_id=plan.id,
            task_count=len(plan.tasks),
        )

        results = {}
        completed = 0
        failed = 0

        for task in plan.tasks:
            try:
                logger.info(
                    "Maestro: Dispatching Task",
                    task_id=task.id,
                    agent=task.agent_type,
                    action=task.action,
                )
                task.status = TaskStatus.IN_PROGRESS
                start_time = datetime.now()

                result = await self._dispatch_to_swarm(task, plan.startup_id, plan.source_context)

                execution_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                task.result = result
                task.status = TaskStatus.COMPLETED
                results[task.id] = result
                completed += 1

                # Track outcome
                try:
                    from app.services.agent_memory_service import agent_memory_service
                    await agent_memory_service.record_outcome(
                        startup_id=plan.startup_id,
                        agent_name=task.agent_type,
                        action_type=task.action,
                        input_context=task.params,
                        output_data=result,
                        execution_time_ms=execution_ms,
                    )
                except Exception:
                    pass  # Don't let tracking failures break execution

            except Exception as e:
                logger.error(
                    "Task Execution Failed",
                    task_id=task.id,
                    agent=task.agent_type,
                    error=str(e),
                )
                task.status = TaskStatus.FAILED
                task.result = {"error": str(e)}
                failed += 1

        return {
            "plan_id": plan.id,
            "total_tasks": len(plan.tasks),
            "completed": completed,
            "failed": failed,
            "results": results,
        }

    async def _dispatch_to_swarm(
        self, task: ExecutionTask, startup_id: str, source_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route to REAL agent capabilities. Every branch calls a live agent.
        """
        startup_context = source_context.get("startup_context", {})
        user_id = source_context.get("user_id", "system")

        # ─── SALES: Real Lead Hunting ───
        if task.agent_type == AgentType.SALES.value:
            from app.agents.sales_agent import sales_agent

            hunt_result = await sales_agent.auto_hunt(
                startup_context=startup_context or {"industry": "Technology"},
                user_id=user_id,
            )

            leads_found = len(hunt_result.get("leads", []))
            logger.info("Maestro: Sales Agent returned", leads=leads_found)

            # Persist leads to DB
            if leads_found > 0:
                await self._persist_leads(startup_id, hunt_result.get("leads", []))

            return {
                "status": "success",
                "agent": "sales_agent",
                "leads_found": leads_found,
                "leads": hunt_result.get("leads", []),
            }

        # ─── MARKETING: Real Content Generation ───
        elif task.agent_type == AgentType.MARKETING.value:
            from app.agents.marketing_agent import marketing_agent

            content_result = await marketing_agent.generate_daily_ideas(
                startup_context=startup_context or {"industry": "Technology"},
            )

            topic = content_result.get("topic", "N/A")
            logger.info("Maestro: Marketing Agent returned", topic=topic)

            # Schedule the generated content
            if content_result.get("full_draft") and not content_result.get("error"):
                await self._schedule_content(
                    startup_id, content_result, task.params.get("platform", "linkedin")
                )

            return {
                "status": "success",
                "agent": "marketing_agent",
                "topic": topic,
                "draft_preview": content_result.get("draft_preview", ""),
            }

        # ─── COMPETITOR INTEL: Real Market Monitoring ───
        elif task.agent_type == "competitor_intel":
            from app.agents.competitor_intel_agent import competitor_intel_agent

            intel_result = await competitor_intel_agent.monitor_market(
                startup_context=startup_context or {"industry": "Technology"},
                known_competitors=task.params.get("known_competitors", []),
            )

            mode = intel_result.get("mode", "unknown")
            logger.info("Maestro: CompetitorIntel returned", mode=mode)

            return {
                "status": "success",
                "agent": "competitor_intel",
                "mode": mode,
                "updates": intel_result.get("updates", []),
                "new_competitors": intel_result.get("new_competitors", []),
            }

        # ─── GROWTH HACKER: Real Social Monitoring ───
        elif task.agent_type == AgentType.GROWTH_HACKER.value:
            from app.agents.growth_hacker_agent import growth_hacker_agent

            growth_result = await growth_hacker_agent.monitor_social(
                keywords=task.params.get("keywords", ["AI", "startup"]),
                platform=task.params.get("platform", "reddit"),
            )

            opportunities = len(growth_result.get("opportunities", []))
            logger.info("Maestro: GrowthHacker returned", opportunities=opportunities)

            return {
                "status": "success",
                "agent": "growth_hacker",
                "opportunities_found": opportunities,
                "opportunities": growth_result.get("opportunities", []),
            }

        # ─── QA TESTER: Real Website Audit ───
        elif task.agent_type == "qa_tester":
            from app.agents.qa_tester_agent import qa_tester_agent

            url = task.params.get("url", "")
            if url:
                audit_result = await qa_tester_agent.full_audit(url)
                logger.info("Maestro: QATester audit complete", url=url)
                return {
                    "status": "success",
                    "agent": "qa_tester",
                    "url": url,
                    "audit": audit_result,
                }
            return {"status": "skipped", "reason": "No URL provided for audit"}

        # ─── CONTENT AGENT: Direct Content Generation ───
        elif task.agent_type == "content":
            from app.agents.content_agent import content_agent

            content_result = await content_agent.process(
                message=f"Create a {task.params.get('content_type', 'post')} about {task.params.get('topic', 'our product')}",
                startup_context=startup_context,
                user_id=user_id,
            )

            return {
                "status": "success",
                "agent": "content_agent",
                "content": content_result.get("response", ""),
            }

        # ─── COMMUNITY: Real Engagement ───
        elif task.agent_type == "community":
            from app.agents.community_agent import community_agent

            community_result = await community_agent.process(
                message=f"Plan community engagement for channels: {task.params.get('channels', ['discord'])}",
                startup_context=startup_context,
                user_id=user_id,
            )

            return {
                "status": "success",
                "agent": "community_agent",
                "plan": community_result.get("response", ""),
            }

        # ─── FALLBACK: Route through SwarmRouter ───
        else:
            from app.agents.swarm_router import swarm_router

            logger.info(
                "Maestro: Routing to SwarmRouter",
                agent_type=task.agent_type,
                action=task.action,
            )

            result = await swarm_router.route_task(
                task_description=f"{task.action}: {task.params}",
                context={
                    "startup_context": startup_context,
                    "user_id": user_id,
                },
            )

            return {
                "status": "success" if result.get("success") else "failed",
                "agent": "swarm_router",
                "result": result,
            }

    # ─── HELPER: Persist Leads to DB ───
    async def _persist_leads(self, startup_id: str, leads: list):
        """Persist discovered leads to the database."""
        try:
            from app.core.database import async_session
            from app.models.growth import Lead, LeadStatus
            from uuid import UUID

            async with async_session() as db:
                for item in leads:
                    lead_info = item.get("lead", {})
                    draft = item.get("draft", "")

                    new_lead = Lead(
                        startup_id=UUID(startup_id) if isinstance(startup_id, str) else startup_id,
                        company_name=lead_info.get("company_name", "Unknown"),
                        contact_name=lead_info.get("contact_name", "Unknown"),
                        contact_email=lead_info.get("contact_email"),
                        status=LeadStatus.NEW,
                        source="maestro_auto",
                        score=70,
                        notes=f"Pain: {lead_info.get('pain_point', 'N/A')}\n\nDraft:\n{draft}",
                    )
                    db.add(new_lead)

                await db.commit()
                logger.info("Maestro: Persisted leads", count=len(leads), startup=startup_id)

        except Exception as e:
            logger.error("Maestro: Failed to persist leads", error=str(e))

    # ─── HELPER: Schedule Generated Content ───
    async def _schedule_content(self, startup_id: str, content_result: Dict, platform: str):
        """Schedule generated content for posting."""
        try:
            from app.services.social_scheduler import social_scheduler

            draft = content_result.get("full_draft", [])
            content_text = draft[0] if isinstance(draft, list) and draft else str(draft)

            post = await social_scheduler.schedule_post(
                startup_id=startup_id,
                content=content_text,
                platforms=[platform],
                scheduled_at=datetime.utcnow(),
            )
            logger.info("Maestro: Scheduled content", post_id=str(post.id), platform=platform)

        except Exception as e:
            logger.error("Maestro: Failed to schedule content", error=str(e))


execution_maestro = ExecutionMaestro()
