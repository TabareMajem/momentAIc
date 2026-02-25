"""
Viral Growth Engine
Trend detection, virality scoring, A/B variant generation,
and cross-character coordination via A2A protocol.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.core.config import settings
from app.agents.base import get_llm

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# VIRAL GROWTH ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class ViralGrowthEngine:
    """
    AI-powered viral growth system for character content.
    Detects trends, scores content virality, generates A/B variants,
    and coordinates multi-character strategies.
    """

    def __init__(self):
        self.llm = get_llm()

    # ─── Trend Detection ─────────────────────────────────────────────────────

    async def detect_trending_content(
        self,
        platform: str = "tiktok",
        industry: str = "wellness",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Detect current trending content patterns using LLM web search.
        Returns trending sounds, hashtags, formats, and challenges.
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        system_prompt = f"""You are a {platform} trend analyst. Identify what's trending RIGHT NOW.

For each trend, provide:
- topic: The trend name/description
- format: video style (POV, storytime, duet, greenscreen, etc.)
- sound: trending sound name if applicable
- hashtags: associated hashtags
- virality_score: estimated virality (0-100)
- relevance_to_industry: how well this fits {industry} (0-100)
- content_angle: How a {industry} influencer could use this trend

Return JSON array of {limit} trends. Return ONLY valid JSON."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"What's trending on {platform} right now for {industry} creators?"),
            ])
            import json
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            trends = json.loads(text)
            return trends[:limit] if isinstance(trends, list) else []
        except Exception as e:
            logger.error("Trend detection failed", error=str(e))
            return []

    # ─── Virality Scoring ────────────────────────────────────────────────────

    async def score_virality(
        self,
        content: Dict[str, Any],
        platform: str = "tiktok",
    ) -> Dict[str, Any]:
        """
        Score content virality using the spec's weighted formula:
        Hook (30%) + Trend (25%) + Emotion (20%) + Timing (15%) + Visual (10%)
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        script = content.get("script", "")
        caption = content.get("caption", "")

        system_prompt = """You are a viral content scoring engine. Analyze this content precisely.

Score each factor 0-100:
1. hook_strength: Does the first 1.5 seconds stop the scroll? Is it unexpected/intriguing?
2. trend_alignment: Does it match current trending formats, sounds, or topics?
3. emotional_trigger: Does it evoke surprise, humor, nostalgia, relatability, or mild controversy?
4. timing_score: Is this the right time to post this content? (consider day, season, current events)
5. visual_quality: How polished yet authentic does it feel? UGC > overproduced

Return JSON: {"hook_strength":N, "trend_alignment":N, "emotional_trigger":N, "timing_score":N, "visual_quality":N, "explanation": "brief analysis"}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Platform: {platform}\nScript: {script[:500]}\nCaption: {caption[:300]}"),
            ])
            import json
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            scores = json.loads(text)

            # Apply weights
            weighted_score = (
                scores.get("hook_strength", 50) * 0.30
                + scores.get("trend_alignment", 30) * 0.25
                + scores.get("emotional_trigger", 50) * 0.20
                + scores.get("timing_score", 60) * 0.15
                + scores.get("visual_quality", 50) * 0.10
            )

            return {
                "overall_score": round(min(100, max(0, weighted_score)), 1),
                "breakdown": scores,
                "recommendation": self._get_recommendation(weighted_score),
            }
        except Exception as e:
            logger.error("Virality scoring failed", error=str(e))
            return {"overall_score": 50.0, "breakdown": {}, "recommendation": "Unable to analyze"}

    def _get_recommendation(self, score: float) -> str:
        if score >= 80:
            return "🔥 HIGH VIRAL POTENTIAL — Post immediately during peak hours"
        elif score >= 65:
            return "⚡ GOOD POTENTIAL — Consider A/B testing hooks before posting"
        elif score >= 50:
            return "🎯 MODERATE — Strengthen hook or ride a trending sound"
        elif score >= 35:
            return "📝 NEEDS WORK — Rethink hook and emotional angle"
        else:
            return "🔄 REWORK — Content unlikely to perform; try a different approach"

    # ─── A/B Variant Generation ──────────────────────────────────────────────

    async def generate_variants(
        self,
        content: Dict[str, Any],
        character_name: str = "Creator",
        variant_count: int = 3,
        variant_type: str = "hook",
    ) -> List[Dict[str, Any]]:
        """
        Generate A/B test variants of content.
        Variant types: hook, caption, cta, full
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        system_prompt = f"""You are a content optimization AI. Generate {variant_count} variations of this content.

Variation type: {variant_type}
Character: {character_name}

Rules:
- Each variant should be meaningfully different, not just word swaps
- Vary the emotional angle: curiosity, humor, controversy, vulnerability, shock
- Keep the same core message, but change the {variant_type}
- Label each variant: A, B, C, etc.

Return JSON array of objects with: label, {variant_type}, predicted_engagement (adjective), reasoning (1 sentence)"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Original {variant_type}:\n{content.get(variant_type, content.get('script', ''))[:500]}"),
            ])
            import json
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except Exception as e:
            logger.error("Variant generation failed", error=str(e))
            return []

    # ─── Cross-Character Coordination ────────────────────────────────────────

    async def cross_character_coordinate(
        self,
        character_ids: List[str],
        campaign_type: str = "duet",
        topic: str = "",
    ) -> Dict[str, Any]:
        """
        Coordinate content across multiple characters using A2A Protocol.
        Campaign types: duet, quote_chain, collab_thread, debate
        """
        from app.services.message_bus import publish_message, MessagePriority

        coordination_plan = await self._plan_coordination(
            character_ids, campaign_type, topic
        )

        # Publish coordination messages via A2A
        for assignment in coordination_plan.get("assignments", []):
            try:
                from app.models.agent_message import AgentMessage, A2AMessageType, MessageStatus
                msg = AgentMessage(
                    startup_id=assignment.get("startup_id"),
                    message_type=A2AMessageType.REQUEST,
                    from_agent="viral_growth_engine",
                    to_agent=f"character_{assignment.get('character_id', 'unknown')}",
                    topic=f"campaign.{campaign_type}",
                    payload={
                        "campaign_type": campaign_type,
                        "script_instructions": assignment.get("instructions", ""),
                        "posting_order": assignment.get("order", 0),
                        "reference_content": assignment.get("reference", ""),
                    },
                    priority=MessagePriority.NORMAL,
                    status=MessageStatus.PENDING,
                )
                # In production: await publish_message(msg)
                logger.info("Cross-character assignment", character=assignment.get("character_id"))
            except Exception as e:
                logger.warning("A2A message failed", error=str(e))

        return coordination_plan

    async def _plan_coordination(
        self,
        character_ids: List[str],
        campaign_type: str,
        topic: str,
    ) -> Dict[str, Any]:
        """Plan multi-character coordination using LLM."""
        from langchain_core.messages import HumanMessage, SystemMessage

        system_prompt = f"""Plan a multi-character {campaign_type} campaign.

Characters: {len(character_ids)} characters
Topic: {topic or 'Trending content'}

Campaign type rules:
- duet: Character B reacts/replies to Character A's video
- quote_chain: Each character quotes the previous one, adding their take
- collab_thread: Characters co-author a Twitter thread
- debate: Characters take opposing friendly positions

Create a posting plan with timing, order, and script instructions for each character.
Return JSON: {{"campaign_name": "...", "assignments": [{{"character_id": "...", "order": N, "instructions": "...", "timing_delay_hours": N, "reference": "..."}}]}}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"IDs: {character_ids}\nType: {campaign_type}\nTopic: {topic}"),
            ])
            import json
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except Exception as e:
            logger.error("Coordination planning failed", error=str(e))
            return {"campaign_name": campaign_type, "assignments": []}


# Singleton
viral_growth_engine = ViralGrowthEngine()
