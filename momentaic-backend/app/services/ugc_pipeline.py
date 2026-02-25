"""
UGC Content Generation Pipeline
ChatCut-style autonomous content generation: Script → Image → Video → Voice → Assembly.
Integrates Gemini (scripts), Imagen 3 (images), PiAPI/Kling (video), DashScope/AgentForge (voice).
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

from app.core.config import settings
from app.agents.base import get_llm
from app.models.character import Character, CharacterPlatform

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM-SPECIFIC CONTENT TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

PLATFORM_TEMPLATES = {
    "tiktok": {
        "video_duration": "15-60 seconds",
        "aspect_ratio": "9:16",
        "hook_time": "1.5 seconds",
        "features": ["trending sound", "text overlay", "fast cuts", "POV/storytime"],
        "caption_limit": 2200,
        "hashtag_limit": 10,
    },
    "instagram": {
        "reel_duration": "15-90 seconds",
        "story_duration": "15 seconds",
        "aspect_ratio": "9:16",
        "features": ["no TikTok watermark", "IG-native hashtags", "CTA in caption"],
        "caption_limit": 2200,
        "hashtag_limit": 30,
    },
    "twitter": {
        "tweet_limit": 280,
        "thread_tweets": "5-10",
        "features": ["hot takes", "quote tweets", "engagement replies", "memes"],
        "hashtag_limit": 3,
    },
    "linkedin": {
        "post_limit": 3000,
        "features": ["professional tone", "hook-heavy first line", "data-backed"],
        "hashtag_limit": 5,
    },
    "youtube_shorts": {
        "video_duration": "15-60 seconds",
        "aspect_ratio": "9:16",
        "features": ["subscribe CTA", "educational hook"],
        "caption_limit": 500,
    },
}

# Funnel stage → content style mapping
FUNNEL_CONTENT_STYLE = {
    "awareness": {
        "tone": "entertaining, relatable, trending",
        "cta": "none or very subtle",
        "product_mention": False,
    },
    "interest": {
        "tone": "educational, story-driven, valuable",
        "cta": "follow for more",
        "product_mention": False,
    },
    "desire": {
        "tone": "testimonial, before/after, demo",
        "cta": "link in bio",
        "product_mention": True,
    },
    "action": {
        "tone": "urgent, social proof, limited offer",
        "cta": "direct link, swipe up, download now",
        "product_mention": True,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# UGC PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

class UGCPipeline:
    """
    ChatCut-style UGC content generation pipeline.
    Generates platform-native content for AI characters.
    """

    def __init__(self):
        self.llm = get_llm()

    async def generate_ugc_content(
        self,
        character: Character,
        platform: str = "tiktok",
        funnel_stage: str = "awareness",
        script_override: Optional[str] = None,
        trend_brief: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Full UGC content generation pipeline.
        Returns content data + pipeline metadata + cost tracking.
        """
        pipeline_steps = []
        total_cost = 0.0
        start_time = datetime.utcnow()

        template = PLATFORM_TEMPLATES.get(platform, PLATFORM_TEMPLATES["tiktok"])
        funnel_style = FUNNEL_CONTENT_STYLE.get(funnel_stage, FUNNEL_CONTENT_STYLE["awareness"])

        # ── Step 1: Script Generation ──────────────────────────────────────
        if script_override:
            script = script_override
            pipeline_steps.append({"tool": "manual", "action": "script_provided", "cost_usd": 0})
        else:
            script = await self._generate_script(character, platform, funnel_stage, template, trend_brief)
            step_cost = 0.002  # ~2000 tokens
            total_cost += step_cost
            pipeline_steps.append({"tool": "gemini", "action": "script_generation", "cost_usd": step_cost})

        # ── Step 2: Caption + Hashtags ─────────────────────────────────────
        caption_data = await self._generate_caption(character, platform, script, funnel_stage, template)
        step_cost = 0.001
        total_cost += step_cost
        pipeline_steps.append({"tool": "gemini", "action": "caption_generation", "cost_usd": step_cost})

        # ── Step 3: Image Generation (Imagen 3) ───────────────────────────
        image_url = await self._generate_character_image(character, platform, script)
        step_cost = 0.06  # Imagen 3 pricing
        total_cost += step_cost
        pipeline_steps.append({
            "tool": "imagen3", "action": "character_image",
            "cost_usd": step_cost, "output_url": image_url,
        })

        # ── Step 4: Video Generation (PiAPI Kling) ─────────────────────────
        video_url = None
        if platform in ("tiktok", "instagram", "youtube_shorts"):
            video_url = await self._generate_video(character, script, platform)
            step_cost = 0.25  # Kling pricing
            total_cost += step_cost
            pipeline_steps.append({
                "tool": "kling", "action": "talking_head_video",
                "cost_usd": step_cost, "output_url": video_url,
            })

        # ── Step 5: Voice Generation (DashScope TTS) ──────────────────────
        voice_url = None
        if platform in ("tiktok", "instagram", "youtube_shorts"):
            voice_url = await self._generate_voice(character, script)
            step_cost = 0.01
            total_cost += step_cost
            pipeline_steps.append({
                "tool": "dashscope_tts", "action": "voiceover",
                "cost_usd": step_cost, "output_url": voice_url,
            })

        # ── Step 6: Virality Score ─────────────────────────────────────────
        virality_score = await self._predict_virality(script, platform, funnel_stage, trend_brief)

        elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return {
            "content_data": {
                "script": script,
                "caption": caption_data.get("caption", ""),
                "hashtags": caption_data.get("hashtags", []),
                "hook_text": caption_data.get("hook", ""),
                "cta": caption_data.get("cta", ""),
                "media_urls": [u for u in [image_url, video_url] if u],
                "voice_url": voice_url,
                "thumbnail_url": image_url,
                "platform": platform,
                "funnel_stage": funnel_stage,
            },
            "pipeline": {
                "steps": pipeline_steps,
                "total_cost_usd": round(total_cost, 4),
                "total_time_ms": elapsed_ms,
                "generated_at": start_time.isoformat(),
            },
            "total_cost_usd": round(total_cost, 4),
            "virality_score": virality_score,
        }

    # ─── Script Generation ───────────────────────────────────────────────────

    async def _generate_script(
        self,
        character: Character,
        platform: str,
        funnel_stage: str,
        template: Dict[str, Any],
        trend_brief: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a platform-native script in the character's voice."""
        from langchain_core.messages import HumanMessage, SystemMessage

        persona = character.persona or {}
        voice_examples = persona.get("voice_examples", [])
        dna = character.character_dna or ""

        trend_context = ""
        if trend_brief:
            trend_context = f"""
TRENDING RIGHT NOW:
- Sound/Topic: {trend_brief.get('topic', 'N/A')}
- Format: {trend_brief.get('format', 'N/A')}
- Virality Score: {trend_brief.get('score', 'N/A')}
Incorporate this trend naturally into the content."""

        system_prompt = f"""You are {character.name}, a virtual influencer.
Your Character DNA:
{dna[:2000]}

You write content in this voice:
{chr(10).join(f'- "{v}"' for v in voice_examples[:5])}

Platform: {platform.upper()}
Duration: {template.get('video_duration', 'N/A')}
Features: {', '.join(template.get('features', []))}

Content Rules:
- Hook must grab attention in first 1.5 seconds
- Funnel stage: {funnel_stage} — {FUNNEL_CONTENT_STYLE.get(funnel_stage, {}).get('tone', 'entertaining')}
- CTA: {FUNNEL_CONTENT_STYLE.get(funnel_stage, {}).get('cta', 'none')}
{trend_context}

Write a complete script. Include [HOOK], [BODY], and [CTA] markers.
Keep it conversational, authentic, and platform-native.
Return ONLY the script text."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Generate a {platform} {funnel_stage}-stage content script."),
            ])
            return response.content.strip()
        except Exception as e:
            logger.error("Script generation failed", error=str(e))
            return f"[HOOK] Hey, it's {character.name}!\n[BODY] Something amazing I want to share...\n[CTA] Follow for more!"

    # ─── Caption + Hashtags ──────────────────────────────────────────────────

    async def _generate_caption(
        self,
        character: Character,
        platform: str,
        script: str,
        funnel_stage: str,
        template: Dict[str, Any],
    ) -> Dict[str, str]:
        """Generate platform-optimized caption with hashtags."""
        from langchain_core.messages import HumanMessage, SystemMessage

        hashtag_limit = template.get("hashtag_limit", 10)
        caption_limit = template.get("caption_limit", 2200)

        system_prompt = f"""Generate a {platform} caption for this script by {character.name}.

Character voice: {character.persona.get('personality_traits', ['friendly'])}
Funnel stage: {funnel_stage}
Max caption length: {caption_limit} chars
Max hashtags: {hashtag_limit}

Return JSON with: hook (first line), caption (full text), hashtags (array), cta (call to action).
Return ONLY valid JSON."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Script:\n{script[:1000]}"),
            ])
            import json
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except Exception as e:
            logger.error("Caption generation failed", error=str(e))
            return {
                "hook": f"You need to see this 👀",
                "caption": script[:200],
                "hashtags": ["#ai", "#wellness", "#trending"],
                "cta": "Link in bio" if funnel_stage in ("desire", "action") else "",
            }

    # ─── Image Generation (Imagen 3) ─────────────────────────────────────────

    async def _generate_character_image(
        self,
        character: Character,
        platform: str,
        script: str,
    ) -> Optional[str]:
        """Generate character image using Gemini Imagen 3."""
        from app.agents.design_agent import design_agent

        style = character.visual_identity.get("style_guide", "modern aesthetic")
        persona = character.persona or {}

        prompt = (
            f"Social media content photo of {character.name}, "
            f"{persona.get('age', 25)}-year-old {persona.get('occupation', 'creator')}, "
            f"style: {style}, "
            f"platform: {platform}, UGC style, authentic feeling, "
            f"warm lighting, high quality, mobile-shot feel"
        )

        try:
            url = await design_agent.generate_card_image(
                archetype_name=f"{character.name}_ugc",
                anime_style=style,
                description=prompt,
            )
            return url
        except Exception as e:
            logger.warning("Image generation failed, continuing pipeline", error=str(e))
            return None

    # ─── Video Generation (PiAPI / Kling) ─────────────────────────────────────

    async def _generate_video(
        self,
        character: Character,
        script: str,
        platform: str,
    ) -> Optional[str]:
        """Generate talking-head video using PiAPI (Kling AI)."""
        from app.agents.design_agent import design_agent

        style = character.visual_identity.get("style_guide", "modern, aesthetic")
        persona = character.persona or {}

        # Describe the video for Kling
        video_prompt = (
            f"A {persona.get('age', 25)}-year-old {persona.get('occupation', 'content creator')} "
            f"talking to camera in UGC selfie style, {style}, "
            f"vertical 9:16 format, natural expressions, "
            f"warm lighting, authentic social media video feel, "
            f"talking about: {script[:150]}"
        )

        try:
            url = await design_agent.generate_video(
                prompt=video_prompt,
                model="kling",
            )
            return url
        except Exception as e:
            logger.warning("Video generation failed, continuing pipeline", error=str(e))
            return None

    # ─── Voice Generation (DashScope TTS) ─────────────────────────────────────

    async def _generate_voice(
        self,
        character: Character,
        script: str,
    ) -> Optional[str]:
        """Generate voiceover using DashScope TTS or AgentForge Voice."""
        voice_identity = character.voice_identity or {}
        provider = voice_identity.get("provider", "dashscope")

        # Clean script for TTS (remove markers)
        clean_script = script.replace("[HOOK]", "").replace("[BODY]", "").replace("[CTA]", "").strip()

        if provider == "agentforge" and settings.agentforge_voice_url:
            return await self._agentforge_tts(clean_script, voice_identity)
        else:
            return await self._dashscope_tts(clean_script, voice_identity)

    async def _dashscope_tts(self, text: str, voice_config: Dict) -> Optional[str]:
        """Generate voice using DashScope (Qwen TTS)."""
        try:
            import aiohttp
            api_key = settings.DASHSCOPE_API_KEY
            if not api_key:
                return None

            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "cosyvoice-v1",
                    "input": {"text": text[:3000]},
                    "parameters": {
                        "voice": voice_config.get("voice_id", "longxiaochun"),
                        "format": "mp3",
                        "sample_rate": 22050,
                    },
                }
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }

                async with session.post(
                    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2audio/generation",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("output", {}).get("audio_url")
                    else:
                        error = await resp.text()
                        logger.warning("DashScope TTS failed", error=error)
                        return None
        except Exception as e:
            logger.warning("DashScope TTS error", error=str(e))
            return None

    async def _agentforge_tts(self, text: str, voice_config: Dict) -> Optional[str]:
        """Generate voice using AgentForge Voice API."""
        try:
            import aiohttp
            base_url = settings.agentforge_voice_url
            if not base_url:
                return None

            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": text[:3000],
                    "voice_id": voice_config.get("voice_id", "default"),
                    "speed": voice_config.get("settings", {}).get("speed", 1.0),
                }
                headers = {
                    "x-api-key": settings.agentforge_api_key or "",
                    "Content-Type": "application/json",
                }

                async with session.post(
                    f"{base_url}/v1/tts",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("audio_url")
                    return None
        except Exception as e:
            logger.warning("AgentForge TTS error", error=str(e))
            return None

    # ─── Virality Prediction ─────────────────────────────────────────────────

    async def _predict_virality(
        self,
        script: str,
        platform: str,
        funnel_stage: str,
        trend_brief: Optional[Dict] = None,
    ) -> float:
        """
        Predict virality score (0-100) using the spec's formula:
        Hook strength (30%) + Trend alignment (25%) + Emotional trigger (20%)
        + Posting time (15%) + Visual quality (10%)
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        system_prompt = """You are a social media virality prediction engine.
Score this content on these factors (0-100 each):
1. hook_strength: How compelling is the first 1.5 seconds? Does it stop the scroll?
2. trend_alignment: Does it match current trending formats/topics?
3. emotional_trigger: Does it evoke surprise, humor, relatability, or controversy?
4. visual_quality: How polished yet authentic-feeling is it?

Return ONLY a JSON object: {"hook_strength": N, "trend_alignment": N, "emotional_trigger": N, "visual_quality": N}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Platform: {platform}\nFunnel: {funnel_stage}\nScript:\n{script[:500]}"),
            ])
            import json
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            scores = json.loads(text)

            # Apply weights from the spec
            weighted = (
                scores.get("hook_strength", 50) * 0.30
                + scores.get("trend_alignment", 30) * 0.25
                + scores.get("emotional_trigger", 50) * 0.20
                + 60 * 0.15  # Posting time score (assume optimal for now)
                + scores.get("visual_quality", 50) * 0.10
            )
            return round(min(100, max(0, weighted)), 1)
        except Exception as e:
            logger.warning("Virality prediction failed", error=str(e))
            return 50.0

    # ─── Multi-Platform Content Adaptation ────────────────────────────────────

    async def adapt_content_for_platform(
        self,
        character: Character,
        original_content: Dict[str, Any],
        source_platform: str,
        target_platform: str,
    ) -> Dict[str, Any]:
        """
        Adapt content from one platform to another.
        Never cross-posts directly — each platform gets native formatting.
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        target_template = PLATFORM_TEMPLATES.get(target_platform, {})

        system_prompt = f"""You are {character.name}. Adapt this {source_platform} content for {target_platform}.

Platform requirements: {target_template}

Rules:
- NEVER cross-post identical content
- Adapt tone, length, and format for {target_platform}
- Remove any platform-specific references (e.g., no TikTok watermarks for Instagram)
- Keep the character's voice consistent

Return JSON with: script, caption, hashtags, content_type (video/image/tweet/etc)"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Original script:\n{original_content.get('script', '')[:1500]}"),
            ])
            import json
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except Exception as e:
            logger.error("Content adaptation failed", error=str(e))
            return original_content


# Singleton
ugc_pipeline = UGCPipeline()
