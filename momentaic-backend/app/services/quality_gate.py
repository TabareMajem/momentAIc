"""
Quality Gate Service — Phase 4
Ensures autonomous agent outputs meet minimum quality before going live.
Uses JudgementAgent for content evaluation and hardcoded thresholds for metrics.
"""

from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()

# Minimum scores (0-100) required to auto-approve
THRESHOLDS = {
    "content_post":       65,   # Content must score ≥65 to auto-schedule
    "outreach_email":     70,   # Outreach drafts need higher bar
    "qa_audit":           50,   # QA reports just need basic coherence
    "reddit_comment":     60,   # Reddit comments (will be human-reviewed anyway)
}


class QualityGateService:
    """
    Gates autonomous agent outputs before they reach users or external platforms.
    
    Workflow:
    1. Agent generates output
    2. QualityGate.evaluate() scores it
    3. If score >= threshold → auto-approve (ActionItem status = "approved")
    4. If score < threshold → hold for human review (status stays "pending")
    """

    async def evaluate_content(
        self,
        content: str,
        goal: str = "maximize engagement",
        target_audience: str = "startup founders",
        gate_type: str = "content_post",
    ) -> Dict[str, Any]:
        """
        Score content through JudgementAgent and apply threshold.
        Returns: {"approved": bool, "score": int, "reasoning": str}
        """
        try:
            from app.agents.judgement_agent import judgement_agent

            threshold = THRESHOLDS.get(gate_type, 65)

            # Evaluate with JudgementAgent
            result = await judgement_agent.evaluate_content(
                goal=goal,
                target_audience=target_audience,
                variations=[content],
            )

            if result.get("error"):
                # LLM failed — default to human review
                logger.warning("QualityGate: JudgementAgent failed, defaulting to human review", error=result["error"])
                return {
                    "approved": False,
                    "score": 0,
                    "reasoning": f"Judgement failed: {result['error']}. Requires human review.",
                    "gate_type": gate_type,
                    "threshold": threshold,
                }

            scores = result.get("scores", [0])
            score = scores[0] if scores else 0
            approved = score >= threshold

            logger.info(
                "QualityGate: Evaluated",
                gate_type=gate_type,
                score=score,
                threshold=threshold,
                approved=approved,
            )

            return {
                "approved": approved,
                "score": score,
                "reasoning": result.get("reasoning", ""),
                "critique": result.get("critique", []),
                "gate_type": gate_type,
                "threshold": threshold,
            }

        except Exception as e:
            logger.error("QualityGate: Evaluation failed", error=str(e))
            return {
                "approved": False,
                "score": 0,
                "reasoning": f"Gate error: {str(e)}",
                "gate_type": gate_type,
            }

    async def gate_action_item(
        self,
        action_item_id: str,
        content: str,
        gate_type: str = "content_post",
        goal: str = "maximize engagement",
        target_audience: str = "startup founders",
    ) -> Dict[str, Any]:
        """
        Evaluate and auto-approve/hold an ActionItem based on quality score.
        Updates the ActionItem status in DB.
        """
        try:
            from app.core.database import async_session
            from app.models.action_item import ActionItem, ActionStatus
            from sqlalchemy import select
            from uuid import UUID

            evaluation = await self.evaluate_content(
                content=content,
                goal=goal,
                target_audience=target_audience,
                gate_type=gate_type,
            )

            async with async_session() as db:
                result = await db.execute(
                    select(ActionItem).where(ActionItem.id == UUID(action_item_id))
                )
                item = result.scalar_one_or_none()

                if item:
                    if evaluation["approved"]:
                        item.status = ActionStatus.approved
                    # else: stays pending for human review

                    # Store gate result in payload
                    payload = dict(item.payload or {})
                    payload["quality_gate"] = evaluation
                    item.payload = payload

                    await db.commit()

            return evaluation

        except Exception as e:
            logger.error("QualityGate: gate_action_item failed", error=str(e))
            return {"approved": False, "score": 0, "reasoning": str(e)}

    async def quick_check(
        self,
        text: str,
        min_length: int = 50,
        max_length: int = 5000,
    ) -> Dict[str, Any]:
        """
        Lightweight quality check without LLM — for fast pre-filtering.
        Checks: length, no placeholder text, no obviously broken content.
        """
        issues = []

        if len(text) < min_length:
            issues.append(f"Too short ({len(text)} chars, min {min_length})")
        if len(text) > max_length:
            issues.append(f"Too long ({len(text)} chars, max {max_length})")

        # Check for placeholder markers
        placeholders = ["[INSERT", "[TODO", "[PLACEHOLDER", "Lorem ipsum", "{{", "}}"]
        for p in placeholders:
            if p.lower() in text.lower():
                issues.append(f"Contains placeholder text: {p}")

        # Check for empty-ish content
        if text.strip().count("\n") > 0 and len(text.strip().replace("\n", "")) < 20:
            issues.append("Content appears to be mostly whitespace")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "char_count": len(text),
        }


# Singleton
quality_gate = QualityGateService()
