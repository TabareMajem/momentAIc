"""
AI Character Factory Models
Virtual influencer characters + their content tracking.
"""

import uuid
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, String, DateTime, Text, Float, Integer, Boolean,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class CharacterStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class CharacterContentType(str, enum.Enum):
    VIDEO = "video"              # Talking-head UGC, B-roll
    IMAGE = "image"              # Static posts, hero shots
    CAROUSEL = "carousel"        # Multi-slide posts
    STORY = "story"              # Ephemeral stories
    TWEET = "tweet"              # Single tweets
    THREAD = "thread"            # Twitter/X threads
    ARTICLE = "article"          # LinkedIn long-form
    REEL = "reel"                # Instagram Reels
    SHORT = "short"              # YouTube Shorts


class CharacterContentStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"    # AI pipeline running
    REVIEW = "review"            # Awaiting founder approval
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class FunnelStage(str, enum.Enum):
    AWARENESS = "awareness"
    INTEREST = "interest"
    DESIRE = "desire"
    ACTION = "action"


class CharacterPlatform(str, enum.Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    YOUTUBE_SHORTS = "youtube_shorts"


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER MODEL — The Virtual Influencer
# ═══════════════════════════════════════════════════════════════════════════════

class Character(Base):
    """
    An AI-generated virtual influencer / character.
    Each character has a complete persona, visual identity, voice,
    platform strategy, and content funnel — managed autonomously by agents.
    """
    __tablename__ = "characters"
    __table_args__ = (
        Index("ix_char_startup", "startup_id"),
        Index("ix_char_status", "status"),
        Index("ix_char_startup_status", "startup_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"),
        nullable=False
    )

    # ─── Identity ───
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    handle: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tagline: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # ─── Persona (full personality matrix) ───
    persona: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Expected structure:
    # {
    #   "age": 24, "location": "Los Angeles",
    #   "occupation": "Freelance designer",
    #   "personality": "Warm, vulnerable, subtly funny",
    #   "humor_style": "Self-deprecating, observational",
    #   "vocabulary_level": "casual_gen_z",
    #   "emoji_usage": "moderate",
    #   "taboo_topics": ["hard sell", "clickbait"],
    #   "target_audience": { "demographics": "...", "psychographics": "..." },
    #   "voice_examples": ["ok but why...", "tried another..."]
    # }

    # ─── Visual Identity ───
    visual_identity: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Expected structure:
    # {
    #   "identity_anchor_url": "https://...",
    #   "scene_library": ["url1", "url2", ...],
    #   "kling_avatar_model_id": "kl_av_...",
    #   "style_guide": "Cozy minimalist, earth tones",
    #   "consistency_seed": "abc123"
    # }

    # ─── Voice Identity ───
    voice_identity: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Expected structure:
    # {
    #   "provider": "dashscope|elevenlabs|agentforge",
    #   "voice_id": "...",
    #   "settings": { "speed": 1.0, "pitch": 0, "emotion": "warm" }
    # }

    # ─── Character DNA (Markdown) ───
    character_dna: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ─── Platform Configuration ───
    platforms: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Expected structure:
    # {
    #   "tiktok": {
    #     "enabled": true, "posting_cadence": "2/day",
    #     "content_formats": ["video", "story"],
    #     "account_handle": "@MikaWellness"
    #   },
    #   "instagram": { ... },
    #   "twitter": { ... },
    #   "linkedin": { ... }
    # }

    # ─── Funnel Configuration (AIDA stages) ───
    funnel_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Expected structure:
    # {
    #   "awareness": { "content_ratio": 0.80, "types": ["trending", "relatable"] },
    #   "interest": { "content_ratio": 0.15, "types": ["how-to", "stories"] },
    #   "desire": { "content_ratio": 0.04, "types": ["product demos"] },
    #   "action": { "content_ratio": 0.01, "types": ["CTA", "promo codes"] }
    # }

    # ─── Content Guardrails ───
    content_rules: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # { "never": [...], "always": [...], "hashtag_strategy": "...", "content_ratio": "80/15/5" }

    # ─── Performance Metrics (rolling, updated by DataAnalystAgent) ───
    performance_metrics: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # {
    #   "tiktok": { "followers": 2400, "avg_views": 12000, "engagement_rate": 0.08 },
    #   "instagram": { ... },
    #   "total_content_pieces": 145,
    #   "total_conversions": 89,
    #   "cac_usd": 1.23
    # }

    # ─── Status & Autonomy ───
    status: Mapped[CharacterStatus] = mapped_column(
        SQLEnum(CharacterStatus), default=CharacterStatus.DRAFT, nullable=False
    )
    autonomy_level: Mapped[str] = mapped_column(
        String(5), default="L2", nullable=False
    )
    # L1 = manual approval for everything
    # L2 = auto-post low-risk, approval for high-risk
    # L3 = auto-post all, daily summary
    # L4 = fully autonomous with weekly brief

    # ─── Budget Controls ───
    daily_budget_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=10.0)
    monthly_budget_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=300.0)
    total_spent_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # ─── Timestamps ───
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ─── Relationships ───
    content_pieces = relationship("CharacterContent", back_populates="character", cascade="all, delete-orphan")


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER CONTENT — Individual Content Pieces
# ═══════════════════════════════════════════════════════════════════════════════

class CharacterContent(Base):
    """
    A single piece of content generated for a character.
    Tracks the full lifecycle: generation → scheduling → publishing → metrics.
    """
    __tablename__ = "character_content"
    __table_args__ = (
        Index("ix_cc_character_platform", "character_id", "platform"),
        Index("ix_cc_status", "status"),
        Index("ix_cc_funnel", "funnel_stage"),
        Index("ix_cc_created", "created_at"),
        Index("ix_cc_character_status", "character_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False
    )

    # ─── Content Details ───
    platform: Mapped[CharacterPlatform] = mapped_column(
        SQLEnum(CharacterPlatform), nullable=False
    )
    content_type: Mapped[CharacterContentType] = mapped_column(
        SQLEnum(CharacterContentType), nullable=False
    )

    # ─── Content Data ───
    content_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Expected structure:
    # {
    #   "script": "Full text/script",
    #   "caption": "Platform caption with #hashtags",
    #   "media_urls": ["image_url", "video_url"],
    #   "thumbnail_url": "...",
    #   "hashtags": ["#wellness", "#anxiety"],
    #   "trending_sound_id": "tiktok_sound_123",
    #   "hook_text": "First 1.5 seconds text",
    #   "cta": "Link in bio"
    # }

    # ─── Generation Pipeline (which AI tools were used) ───
    generation_pipeline: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # {
    #   "steps": [
    #     {"tool": "gemini", "action": "script_generation", "model": "gemini-2.5-pro"},
    #     {"tool": "imagen3", "action": "character_pose", "cost_usd": 0.04},
    #     {"tool": "kling", "action": "talking_head_video", "task_id": "...", "cost_usd": 0.25},
    #     {"tool": "dashscope_tts", "action": "voiceover", "cost_usd": 0.01}
    #   ],
    #   "total_cost_usd": 0.30,
    #   "total_time_ms": 45000
    # }

    # ─── Scheduling ───
    status: Mapped[CharacterContentStatus] = mapped_column(
        SQLEnum(CharacterContentStatus), default=CharacterContentStatus.DRAFT, nullable=False
    )
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ─── Funnel Tracking ───
    funnel_stage: Mapped[Optional[FunnelStage]] = mapped_column(
        SQLEnum(FunnelStage), nullable=True
    )

    # ─── Engagement Metrics (updated by DataAnalystAgent) ───
    engagement_metrics: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # {
    #   "views": 12000, "likes": 1400, "comments": 89,
    #   "shares": 234, "saves": 567, "clicks": 45,
    #   "watch_time_avg_sec": 12.5, "retention_1_5s": 0.78,
    #   "engagement_rate": 0.08
    # }

    # ─── Conversion Events ───
    conversion_events: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # { "app_installs": 5, "signups": 3, "purchases": 1, "attributed_revenue_usd": 29.99 }

    # ─── Cost ───
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # ─── A/B Testing ───
    variant_group: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    variant_label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # e.g., variant_group="hook_test_001", variant_label="question_hook"

    # ─── Virality Score (pre-publish prediction) ───
    virality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ─── Timestamps ───
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # ─── Relationships ───
    character = relationship("Character", back_populates="content_pieces")
