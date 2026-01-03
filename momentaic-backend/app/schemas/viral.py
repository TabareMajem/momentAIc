"""
Soul Card Generator Schemas
Viral campaign endpoint for "What is your Anime Trauma?" quiz
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class SoulCardQuizInput(BaseModel):
    """User's quiz answers for generating their Soul Card"""
    question_1: str = Field(..., description="Response to: 'When stressed, I typically...'")
    question_2: str = Field(..., description="Response to: 'My ideal weekend involves...'")
    question_3: str = Field(..., description="Response to: 'In a group, I am usually...'")
    user_name: Optional[str] = Field(None, description="Optional name to display on card")


class AnimeArchetype(BaseModel):
    """The generated anime archetype"""
    archetype_name: str = Field(..., example="The Depressed Eva Pilot")
    archetype_title: str = Field(..., example="SHINJI-TYPE")
    description: str = Field(..., description="2-3 sentence roast/description")
    anime_reference: str = Field(..., example="Neon Genesis Evangelion")
    trauma_type: str = Field(..., example="Existential Dread")
    healing_advice: str = Field(..., description="Yokaizen-specific advice")


class SoulCardResponse(BaseModel):
    """The complete Soul Card response"""
    archetype: AnimeArchetype
    card_image_url: Optional[str] = Field(None, description="URL to generated card image")
    share_text: str = Field(..., description="Pre-written share text for X/Twitter")
    app_download_url: str = Field(default="https://yokaizen.app/download")
    qr_code_url: Optional[str] = Field(None, description="URL to QR code for app download")


class SoulCardGenerateRequest(BaseModel):
    """Request to generate a Soul Card"""
    quiz: SoulCardQuizInput
    generate_image: bool = Field(default=True, description="Whether to generate the visual card")
    platform: str = Field(default="twitter", pattern="^(twitter|instagram|tiktok)$")
