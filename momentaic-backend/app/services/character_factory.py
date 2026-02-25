"""
AI Character Factory Service
Creates, configures, and manages AI virtual influencer characters.
Handles persona design, visual identity generation, voice setup, and DNA creation.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.agents.base import get_llm
from app.models.character import (
    Character, CharacterContent, CharacterStatus,
    CharacterContentType, CharacterContentStatus,
    CharacterPlatform, FunnelStage,
)

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

class CharacterFactory:
    """
    Creates and manages AI virtual influencer characters.
    Integrates with Gemini for persona design, Imagen 3 for visuals,
    PiAPI/Kling for video avatars, and DashScope/AgentForge for voice.
    """

    def __init__(self):
        self.llm = get_llm()

    # ─── Persona Design ─────────────────────────────────────────────────────

    async def create_character(
        self,
        db: AsyncSession,
        startup_id: str,
        name: str,
        target_audience: str,
        brand_personality: str,
        visual_direction: str = "",
        voice_direction: str = "",
        platform_focus: str = "tiktok,instagram",
        product_to_promote: str = "",
    ) -> Character:
        """
        Create a new AI character with LLM-enhanced persona design.
        The founder provides high-level direction; the LLM fills in the rest.
        """
        logger.info("CharacterFactory: Creating character", name=name, startup_id=startup_id)

        # 1. Generate full persona via LLM
        persona = await self._design_persona(
            name=name,
            target_audience=target_audience,
            brand_personality=brand_personality,
            visual_direction=visual_direction,
            product_to_promote=product_to_promote,
        )

        # 2. Generate platform strategy
        platforms_config = self._build_platform_config(platform_focus)

        # 3. Generate funnel config
        funnel_config = self._build_funnel_config(product_to_promote)

        # 4. Generate content rules
        content_rules = self._build_content_rules(brand_personality)

        # 5. Create the character record
        character = Character(
            startup_id=startup_id,
            name=name,
            handle=f"@{name.replace(' ', '').lower()}",
            tagline=persona.get("tagline", ""),
            persona=persona,
            visual_identity={"style_guide": visual_direction, "scene_library": []},
            voice_identity={"direction": voice_direction} if voice_direction else None,
            platforms=platforms_config,
            funnel_config=funnel_config,
            content_rules=content_rules,
            status=CharacterStatus.DRAFT,
        )

        db.add(character)
        await db.flush()

        # 6. Generate Character DNA document
        character.character_dna = self._generate_dna_document(character)

        await db.commit()
        await db.refresh(character)

        logger.info("CharacterFactory: Character created", character_id=str(character.id), name=name)
        return character

    async def _design_persona(
        self,
        name: str,
        target_audience: str,
        brand_personality: str,
        visual_direction: str,
        product_to_promote: str,
    ) -> Dict[str, Any]:
        """Use LLM to generate a full personality matrix from founder inputs."""
        from langchain_core.messages import HumanMessage, SystemMessage

        system_prompt = """You are an expert AI character designer for social media virtual influencers.
Given a founder's high-level direction, create a complete persona with detailed attributes.

Return a JSON object with these fields:
- tagline: A catchy one-liner for the character
- age: Number
- location: Fictional city/state
- occupation: Day job / identity
- backstory: 2-3 sentences about who they are
- personality_traits: Array of 5-8 traits
- humor_style: How they joke
- vocabulary_level: casual_gen_z | professional | academic | internet_native
- emoji_usage: none | minimal | moderate | heavy
- taboo_topics: Array of topics they never discuss
- target_audience: { demographics, psychographics, pain_points }
- voice_examples: Array of 5 example posts/tweets in their voice
- content_themes: Array of 5-8 recurring content themes
- engagement_style: How they interact with followers

Return ONLY valid JSON, no markdown formatting."""

        user_prompt = f"""Create a virtual influencer persona:

Name: {name}
Target Audience: {target_audience}
Brand Personality: {brand_personality}
Visual Direction: {visual_direction}
Product to Promote: {product_to_promote}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            import json
            # Clean response
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except Exception as e:
            logger.error("Persona design failed, using defaults", error=str(e))
            return {
                "tagline": f"AI-powered voice for {target_audience}",
                "age": 25,
                "location": "Los Angeles",
                "personality_traits": brand_personality.split(", "),
                "humor_style": "observational",
                "vocabulary_level": "casual_gen_z",
                "emoji_usage": "moderate",
                "taboo_topics": ["hard sell", "clickbait", "toxic positivity"],
                "target_audience": {"demographics": target_audience},
                "voice_examples": [],
                "content_themes": [],
                "engagement_style": "warm and authentic",
            }

    # ─── Visual Identity Generation ──────────────────────────────────────────

    async def generate_character_visuals(
        self,
        db: AsyncSession,
        character_id: str,
        num_scenes: int = 6,
    ) -> Dict[str, Any]:
        """
        Generate visual identity using Gemini Imagen 3.
        Creates identity anchor + scene library.
        """
        character = await db.get(Character, character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")

        from app.agents.design_agent import design_agent

        results = {"identity_anchor_url": None, "scene_library": []}

        # 1. Generate identity anchor (hero portrait)
        style = character.visual_identity.get("style_guide", "modern, aesthetic")
        persona = character.persona

        anchor_prompt = (
            f"Professional portrait photo of {character.name}, "
            f"a {persona.get('age', 25)}-year-old {persona.get('occupation', 'creator')}, "
            f"style: {style}, high quality, social media profile photo, "
            f"warm lighting, looking at camera, friendly expression"
        )

        try:
            anchor_url = await design_agent.generate_card_image(
                archetype_name=character.name,
                anime_style=style,
                description=anchor_prompt,
            )
            results["identity_anchor_url"] = anchor_url
        except Exception as e:
            logger.error("Identity anchor generation failed", error=str(e))

        # 2. Generate scene library
        scene_prompts = [
            f"{character.name} at a coffee shop, casual selfie, {style}",
            f"{character.name} working at a laptop, focused, {style}",
            f"{character.name} laughing with friends outdoors, candid, {style}",
            f"{character.name} holding a phone showing an app, product shot, {style}",
            f"{character.name} in a cozy room, relaxed, lifestyle shot, {style}",
            f"{character.name} at the gym, active lifestyle, {style}",
        ]

        for i, prompt in enumerate(scene_prompts[:num_scenes]):
            try:
                scene_url = await design_agent.generate_card_image(
                    archetype_name=f"{character.name}_scene_{i}",
                    anime_style=style,
                    description=prompt,
                )
                results["scene_library"].append(scene_url)
            except Exception as e:
                logger.warning(f"Scene {i} generation failed", error=str(e))

        # 3. Update character visual identity
        character.visual_identity = {
            **character.visual_identity,
            **results,
        }
        await db.commit()

        logger.info("Visuals generated", character_id=character_id, scenes=len(results["scene_library"]))
        return results

    # ─── Video Avatar (Kling via PiAPI) ──────────────────────────────────────

    async def generate_ugc_video(
        self,
        db: AsyncSession,
        character_id: str,
        script: str = "",
        platform: str = "tiktok",
        funnel_stage: str = "awareness",
    ) -> Dict[str, Any]:
        """
        Generate a ChatCut-style UGC talking-head video.
        Uses PiAPI (Kling) for video + DashScope/AgentForge for voice.
        """
        character = await db.get(Character, character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")

        from app.services.ugc_pipeline import ugc_pipeline
        result = await ugc_pipeline.generate_ugc_content(
            character=character,
            platform=platform,
            funnel_stage=funnel_stage,
            script_override=script or None,
        )

        # Store as CharacterContent
        content_piece = CharacterContent(
            character_id=character.id,
            platform=CharacterPlatform(platform),
            content_type=CharacterContentType.VIDEO,
            content_data=result.get("content_data", {}),
            generation_pipeline=result.get("pipeline", {}),
            status=CharacterContentStatus.REVIEW,
            funnel_stage=FunnelStage(funnel_stage) if funnel_stage else None,
            cost_usd=result.get("total_cost_usd", 0),
            virality_score=result.get("virality_score"),
        )
        db.add(content_piece)
        await db.commit()
        await db.refresh(content_piece)

        return {
            "content_id": str(content_piece.id),
            **result,
        }

    # ─── Character DNA Document ──────────────────────────────────────────────

    def _generate_dna_document(self, character: Character) -> str:
        """Generate the Character DNA markdown document."""
        persona = character.persona or {}
        platforms = character.platforms or {}
        rules = character.content_rules or {}
        funnel = character.funnel_config or {}

        voice_examples = persona.get("voice_examples", [])
        voice_section = "\n".join(f"- '{v}'" for v in voice_examples[:5])

        platform_section = ""
        for plat, config in platforms.items():
            if config.get("enabled"):
                cadence = config.get("posting_cadence", "daily")
                formats = ", ".join(config.get("content_formats", []))
                platform_section += f"- {plat.title()}: {cadence}, formats: {formats}\n"

        return f"""# Character DNA: {character.handle or character.name}

## Identity
- Name: {character.name}
- Age: {persona.get('age', 'N/A')} | Location: {persona.get('location', 'N/A')}
- Occupation: {persona.get('occupation', 'N/A')}
- Personality: {', '.join(persona.get('personality_traits', []))}
- Backstory: {persona.get('backstory', 'N/A')}

## Visual Identity
- Style: {character.visual_identity.get('style_guide', 'N/A')}
- Identity Anchor: {character.visual_identity.get('identity_anchor_url', 'Not generated')}

## Content Rules
- NEVER: {', '.join(rules.get('never', ['hard sell', 'clickbait']))}
- ALWAYS: {', '.join(rules.get('always', ['authentic', 'value-first']))}
- Ratio: {rules.get('content_ratio', '80% value, 15% soft mention, 5% CTA')}
- Humor: {persona.get('humor_style', 'observational')}

## Platform Strategy
{platform_section or '- Not configured'}

## Funnel
- Awareness: {funnel.get('awareness', {}).get('types', ['trending content'])}
- Interest: {funnel.get('interest', {}).get('types', ['how-tos, stories'])}
- Desire: {funnel.get('desire', {}).get('types', ['product demos'])}
- Action: {funnel.get('action', {}).get('types', ['CTA, promo codes'])}

## Voice Examples
{voice_section or '- No examples generated yet'}

## Engagement Style
- {persona.get('engagement_style', 'Warm and authentic')}
"""

    # ─── Helpers ─────────────────────────────────────────────────────────────

    def _build_platform_config(self, platform_focus: str) -> Dict[str, Any]:
        """Build platform configuration from comma-separated focus string."""
        platforms_list = [p.strip().lower() for p in platform_focus.split(",")]
        config = {}

        defaults = {
            "tiktok": {"posting_cadence": "2/day", "content_formats": ["video", "story"]},
            "instagram": {"posting_cadence": "1 Reel + 1 Story/day", "content_formats": ["reel", "story", "carousel", "image"]},
            "twitter": {"posting_cadence": "5-8/day", "content_formats": ["tweet", "thread"]},
            "linkedin": {"posting_cadence": "2/week", "content_formats": ["article", "video"]},
            "youtube_shorts": {"posting_cadence": "1/day", "content_formats": ["short"]},
        }

        for plat in platforms_list:
            d = defaults.get(plat, {"posting_cadence": "daily", "content_formats": ["video"]})
            config[plat] = {"enabled": True, **d}

        return config

    def _build_funnel_config(self, product: str) -> Dict[str, Any]:
        """Build AIDA funnel configuration."""
        return {
            "awareness": {"content_ratio": 0.80, "types": ["trending", "relatable", "entertainment"]},
            "interest": {"content_ratio": 0.15, "types": ["how-to", "personal stories", "educational"]},
            "desire": {"content_ratio": 0.04, "types": ["product demos", "testimonials", "before/after"]},
            "action": {"content_ratio": 0.01, "types": ["CTA", "link in bio", "limited offers"]},
            "product": product,
        }

    def _build_content_rules(self, personality: str) -> Dict[str, Any]:
        """Build content safety guardrails."""
        return {
            "never": ["hard sell", "clickbait", "toxic positivity", "medical claims", "harmful content"],
            "always": ["personal stories", "vulnerability", "genuine experience", "value-first"],
            "content_ratio": "80% value/entertainment, 15% soft product, 5% direct CTA",
            "hashtag_strategy": "mix trending + niche tags",
            "ai_disclosure": True,
            "max_daily_posts": {"tiktok": 3, "instagram": 5, "twitter": 10, "linkedin": 2},
        }

    # ─── CRUD Operations ────────────────────────────────────────────────────

    async def get_character(self, db: AsyncSession, character_id: str) -> Optional[Character]:
        result = await db.execute(
            select(Character).where(Character.id == character_id)
        )
        return result.scalar_one_or_none()

    async def list_characters(self, db: AsyncSession, startup_id: str) -> List[Character]:
        result = await db.execute(
            select(Character)
            .where(Character.startup_id == startup_id)
            .order_by(Character.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_character(
        self, db: AsyncSession, character_id: str, updates: Dict[str, Any]
    ) -> Character:
        character = await db.get(Character, character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")

        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)

        character.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(character)
        return character

    async def activate_character(self, db: AsyncSession, character_id: str) -> Character:
        return await self.update_character(db, character_id, {"status": CharacterStatus.ACTIVE})

    async def pause_character(self, db: AsyncSession, character_id: str) -> Character:
        return await self.update_character(db, character_id, {"status": CharacterStatus.PAUSED})

    async def get_character_content(
        self,
        db: AsyncSession,
        character_id: str,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[CharacterContent]:
        query = select(CharacterContent).where(CharacterContent.character_id == character_id)
        if platform:
            query = query.where(CharacterContent.platform == platform)
        if status:
            query = query.where(CharacterContent.status == status)
        query = query.order_by(CharacterContent.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_character_analytics(
        self, db: AsyncSession, character_id: str
    ) -> Dict[str, Any]:
        """Aggregate analytics for a character."""
        from sqlalchemy import func

        character = await db.get(Character, character_id)
        if not character:
            return {}

        # Count content by status
        content_stats = await db.execute(
            select(
                CharacterContent.status,
                func.count(CharacterContent.id)
            )
            .where(CharacterContent.character_id == character_id)
            .group_by(CharacterContent.status)
        )

        # Count by platform
        platform_stats = await db.execute(
            select(
                CharacterContent.platform,
                func.count(CharacterContent.id),
                func.sum(CharacterContent.cost_usd)
            )
            .where(CharacterContent.character_id == character_id)
            .group_by(CharacterContent.platform)
        )

        return {
            "character_id": str(character_id),
            "name": character.name,
            "status": character.status.value,
            "total_spent_usd": character.total_spent_usd,
            "performance_metrics": character.performance_metrics or {},
            "content_by_status": {
                row[0].value: row[1] for row in content_stats.all()
            },
            "content_by_platform": {
                row[0].value: {"count": row[1], "cost_usd": float(row[2] or 0)}
                for row in platform_stats.all()
            },
        }


# Singleton
character_factory = CharacterFactory()
