"""
Character Agent
Heartbeat-driven agent team for AI virtual influencer characters.
Wraps existing ContentAgent, SocialScheduler, and GrowthHacker
with character-specific DNA context for autonomous operation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.character import (
    Character, CharacterContent, CharacterStatus,
    CharacterContentType, CharacterContentStatus,
    CharacterPlatform, FunnelStage,
)

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER CONTENT AGENT — Autonomous daily content generation
# ═══════════════════════════════════════════════════════════════════════════════

class CharacterContentAgent:
    """
    Wraps ContentAgent with character DNA context.
    Called by the heartbeat engine to generate daily content plans.
    """

    async def generate_daily_content_plan(
        self,
        character: Character,
    ) -> Dict[str, Any]:
        """
        Generate a day's worth of content across all enabled platforms.
        Respects character DNA, funnel ratios, and content rules.
        """
        from app.services.ugc_pipeline import ugc_pipeline
        from app.services.viral_growth_engine import viral_growth_engine

        platforms = character.platforms or {}
        funnel_config = character.funnel_config or {}
        content_plan = {"posts": [], "total_estimated_cost": 0}

        for platform_name, platform_config in platforms.items():
            if not platform_config.get("enabled"):
                continue

            # Detect trending content for this platform
            industry = character.persona.get("target_audience", {}).get("demographics", "general")
            trends = await viral_growth_engine.detect_trending_content(
                platform=platform_name,
                industry=industry,
                limit=3,
            )

            # Pick funnel stage based on ratio (80% awareness, 15% interest, etc.)
            funnel_stage = self._pick_funnel_stage(funnel_config)

            # Generate content via UGC pipeline
            trend_brief = trends[0] if trends else None

            try:
                result = await ugc_pipeline.generate_ugc_content(
                    character=character,
                    platform=platform_name,
                    funnel_stage=funnel_stage,
                    trend_brief=trend_brief,
                )

                content_plan["posts"].append({
                    "platform": platform_name,
                    "funnel_stage": funnel_stage,
                    "content": result.get("content_data", {}),
                    "virality_score": result.get("virality_score", 50),
                    "cost_usd": result.get("total_cost_usd", 0),
                    "trend_used": trend_brief.get("topic") if trend_brief else None,
                })
                content_plan["total_estimated_cost"] += result.get("total_cost_usd", 0)
            except Exception as e:
                logger.error(f"Content generation failed for {platform_name}", error=str(e))

        logger.info(
            "Daily content plan generated",
            character=character.name,
            posts=len(content_plan["posts"]),
            cost=content_plan["total_estimated_cost"],
        )
        return content_plan

    def _pick_funnel_stage(self, funnel_config: Dict[str, Any]) -> str:
        """Pick funnel stage based on configured ratios."""
        import random
        ratios = {
            "awareness": funnel_config.get("awareness", {}).get("content_ratio", 0.80),
            "interest": funnel_config.get("interest", {}).get("content_ratio", 0.15),
            "desire": funnel_config.get("desire", {}).get("content_ratio", 0.04),
            "action": funnel_config.get("action", {}).get("content_ratio", 0.01),
        }

        r = random.random()
        cumulative = 0
        for stage, ratio in ratios.items():
            cumulative += ratio
            if r <= cumulative:
                return stage
        return "awareness"


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER SOCIAL AGENT — Autonomous posting + engagement
# ═══════════════════════════════════════════════════════════════════════════════

class CharacterSocialAgent:
    """
    Wraps SocialScheduler with character-specific posting cadence.
    Handles scheduling, engagement automation, and performance tracking.
    """

    async def schedule_content(
        self,
        db: AsyncSession,
        character: Character,
        content_data: Dict[str, Any],
        platform: str,
        optimal_time: Optional[datetime] = None,
    ) -> CharacterContent:
        """Schedule content for publishing."""
        from datetime import timedelta

        # Auto-determine optimal time if not provided
        if not optimal_time:
            optimal_time = self._get_optimal_posting_time(platform, character)

        # Create CharacterContent record
        content_type = CharacterContentType.VIDEO
        if platform in ("twitter",):
            content_type = CharacterContentType.TWEET
        elif platform in ("linkedin",):
            content_type = CharacterContentType.ARTICLE

        content_piece = CharacterContent(
            character_id=character.id,
            platform=CharacterPlatform(platform),
            content_type=content_type,
            content_data=content_data,
            status=CharacterContentStatus.SCHEDULED,
            scheduled_at=optimal_time,
            funnel_stage=FunnelStage(content_data.get("funnel_stage", "awareness")),
            cost_usd=content_data.get("cost_usd", 0),
        )

        db.add(content_piece)
        await db.commit()
        await db.refresh(content_piece)

        logger.info(
            "Content scheduled",
            character=character.name,
            platform=platform,
            time=optimal_time.isoformat(),
        )
        return content_piece

    def _get_optimal_posting_time(self, platform: str, character: Character) -> datetime:
        """Calculate optimal posting time based on platform + audience data."""
        from datetime import timedelta
        import random

        # Base optimal hours per platform (UTC)
        optimal_hours = {
            "tiktok": [11, 14, 19, 21],     # 7am, 10am, 3pm, 5pm EST
            "instagram": [11, 17, 20],        # 7am, 1pm, 4pm EST
            "twitter": [12, 15, 17, 21],      # 8am, 11am, 1pm, 5pm EST
            "linkedin": [12, 14],              # 8am, 10am EST
            "youtube_shorts": [14, 18],        # 10am, 2pm EST
        }

        hours = optimal_hours.get(platform, [14, 18])
        selected_hour = random.choice(hours)

        # Schedule for today or tomorrow
        now = datetime.utcnow()
        target = now.replace(hour=selected_hour, minute=random.randint(0, 30), second=0, microsecond=0)

        if target <= now:
            target += timedelta(days=1)

        return target


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER HEARTBEAT RUNNER — Called by APScheduler
# ═══════════════════════════════════════════════════════════════════════════════

async def run_character_heartbeats():
    """
    Heartbeat function called by the scheduler.
    Iterates through all active characters and generates + schedules content.
    """
    from sqlalchemy import select

    logger.info("🎭 Character Heartbeat: Starting cycle...")

    async with AsyncSessionLocal() as db:
        # Get all active characters
        result = await db.execute(
            select(Character).where(Character.status == CharacterStatus.ACTIVE)
        )
        active_characters = result.scalars().all()

        if not active_characters:
            logger.info("Character Heartbeat: No active characters found")
            return

        logger.info(f"Character Heartbeat: Processing {len(active_characters)} characters")

        content_agent = CharacterContentAgent()
        social_agent = CharacterSocialAgent()

        for character in active_characters:
            try:
                # 1. Check budget
                if character.daily_budget_usd and character.total_spent_usd > 0:
                    # Simple daily budget check (could be refined)
                    days_active = max(1, (datetime.utcnow() - character.created_at).days)
                    daily_avg = character.total_spent_usd / days_active
                    if daily_avg > character.daily_budget_usd:
                        logger.warning(
                            f"Character {character.name} exceeded daily budget, skipping",
                            daily_avg=daily_avg,
                            budget=character.daily_budget_usd,
                        )
                        continue

                # 2. Generate content plan
                plan = await content_agent.generate_daily_content_plan(character)

                # 3. Schedule each post
                for post in plan.get("posts", []):
                    if character.autonomy_level >= "L2":
                        # Auto-schedule for L2+
                        await social_agent.schedule_content(
                            db=db,
                            character=character,
                            content_data=post.get("content", {}),
                            platform=post.get("platform", "tiktok"),
                        )
                    else:
                        # L1: Queue for review (don't auto-schedule)
                        content_piece = CharacterContent(
                            character_id=character.id,
                            platform=CharacterPlatform(post.get("platform", "tiktok")),
                            content_type=CharacterContentType.VIDEO,
                            content_data=post.get("content", {}),
                            status=CharacterContentStatus.REVIEW,
                            funnel_stage=FunnelStage(post.get("funnel_stage", "awareness")),
                            cost_usd=post.get("cost_usd", 0),
                        )
                        db.add(content_piece)

                # 4. Update total spent
                character.total_spent_usd += plan.get("total_estimated_cost", 0)
                await db.commit()

                logger.info(
                    f"Character heartbeat complete: {character.name}",
                    posts=len(plan.get("posts", [])),
                    cost=plan.get("total_estimated_cost", 0),
                )

            except Exception as e:
                logger.error(f"Character heartbeat failed: {character.name}", error=str(e))
                continue

    logger.info("🎭 Character Heartbeat: Cycle complete")
