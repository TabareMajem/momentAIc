"""
Viral Campaign Endpoints
Soul Card Generator and other viral growth features
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.viral import (
    SoulCardGenerateRequest,
    SoulCardResponse,
    AnimeArchetype,
)
from app.agents.base import get_llm

import structlog

logger = structlog.get_logger()

router = APIRouter()


# Anime archetype mapping based on quiz patterns
ARCHETYPE_DATABASE = {
    "introvert_creative_observer": {
        "archetype_name": "The Depressed Eva Pilot",
        "archetype_title": "SHINJI-TYPE",
        "anime_reference": "Neon Genesis Evangelion",
        "trauma_type": "Existential Dread",
    },
    "extrovert_adventurous_leader": {
        "archetype_name": "The Chaotic Protagonist",
        "archetype_title": "NARUTO-TYPE",
        "anime_reference": "Naruto Shippuden",
        "trauma_type": "Abandonment Issues",
    },
    "introvert_analytical_observer": {
        "archetype_name": "The Cold Genius",
        "archetype_title": "L-TYPE",
        "anime_reference": "Death Note",
        "trauma_type": "Emotional Suppression",
    },
    "extrovert_social_mediator": {
        "archetype_name": "The Sunshine Friend",
        "archetype_title": "ZENITSU-TYPE",
        "anime_reference": "Demon Slayer",
        "trauma_type": "Imposter Syndrome",
    },
    "introvert_creative_leader": {
        "archetype_name": "The Brooding Antihero",
        "archetype_title": "SASUKE-TYPE",
        "anime_reference": "Naruto Shippuden",
        "trauma_type": "Revenge Obsession",
    },
    "default": {
        "archetype_name": "The Mysterious Wanderer",
        "archetype_title": "SPIKE-TYPE",
        "anime_reference": "Cowboy Bebop",
        "trauma_type": "Unresolved Past",
    },
}


def classify_personality(q1: str, q2: str, q3: str) -> str:
    """Simple personality classifier based on quiz answers"""
    q1_lower = q1.lower()
    q2_lower = q2.lower()
    q3_lower = q3.lower()
    
    # Introvert vs Extrovert
    introvert_keywords = ["alone", "quiet", "read", "think", "sleep", "home", "recharge"]
    extrovert_keywords = ["friends", "party", "talk", "out", "social", "people", "adventure"]
    
    intro_score = sum(1 for k in introvert_keywords if k in q1_lower + q2_lower)
    extro_score = sum(1 for k in extrovert_keywords if k in q1_lower + q2_lower)
    
    personality = "introvert" if intro_score >= extro_score else "extrovert"
    
    # Creative vs Analytical
    creative_keywords = ["create", "art", "music", "write", "imagine", "dream"]
    analytical_keywords = ["analyze", "plan", "logic", "think", "solve", "study"]
    
    creative_score = sum(1 for k in creative_keywords if k in q1_lower + q2_lower)
    analytical_score = sum(1 for k in analytical_keywords if k in q1_lower + q2_lower)
    
    style = "creative" if creative_score >= analytical_score else "analytical"
    
    # Leader vs Observer vs Mediator
    leader_keywords = ["lead", "decide", "charge", "front", "initiative"]
    mediator_keywords = ["help", "peace", "balance", "support", "harmony"]
    
    if any(k in q3_lower for k in leader_keywords):
        role = "leader"
    elif any(k in q3_lower for k in mediator_keywords):
        role = "mediator"
    else:
        role = "observer"
    
    key = f"{personality}_{style}_{role}"
    return key if key in ARCHETYPE_DATABASE else "default"


@router.post("/soul-card", response_model=SoulCardResponse)
async def generate_soul_card(
    request: SoulCardGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an Anime Soul Card based on personality quiz answers.
    PUBLIC ENDPOINT for viral growth.
    """
    try:
        # Classify personality based on quiz answers
        personality_key = classify_personality(
            request.quiz.question_1,
            request.quiz.question_2,
            request.quiz.question_3,
        )
        
        base_archetype = ARCHETYPE_DATABASE.get(personality_key, ARCHETYPE_DATABASE["default"])
        
        # Use LLM to generate personalized description and advice
        llm = get_llm("gemini-2.5-pro", temperature=0.8)
        
        if llm:
            prompt = f"""Generate a funny yet insightful "roast" for someone with this anime archetype:

Archetype: {base_archetype['archetype_name']} ({base_archetype['archetype_title']})
Anime Reference: {base_archetype['anime_reference']}
Trauma Type: {base_archetype['trauma_type']}

User's Quiz Answers:
1. When stressed: "{request.quiz.question_1}"
2. Ideal weekend: "{request.quiz.question_2}"
3. In a group: "{request.quiz.question_3}"

Write:
1. A 2-sentence "roast" that's funny but weirdly accurate (like an anime character analysis)
2. A 1-sentence healing advice from a "wise anime mentor" perspective

Keep it Gen-Z friendly, slightly unhinged, but ultimately supportive."""

            response = await llm.ainvoke(prompt)
            ai_text = response.content
            
            # Parse the AI response
            lines = ai_text.strip().split("\n")
            description = " ".join(lines[:2]) if len(lines) >= 2 else ai_text[:200]
            healing_advice = lines[-1] if len(lines) > 2 else "Your arc is just beginning. Believe it!"
        else:
            description = f"You have {base_archetype['trauma_type']}. Classic {base_archetype['archetype_title']}."
            healing_advice = "Your healing arc starts with the Yokaizen App. Download now."
        
        # Build the archetype response
        archetype = AnimeArchetype(
            archetype_name=base_archetype["archetype_name"],
            archetype_title=base_archetype["archetype_title"],
            description=description,
            anime_reference=base_archetype["anime_reference"],
            trauma_type=base_archetype["trauma_type"],
            healing_advice=healing_advice,
        )
        
        # Generate share text for social media
        user_display = request.quiz.user_name or "I"
        share_text = f"""🎴 {user_display} took the Anime Trauma Test and got:

**{archetype.archetype_name}** ({archetype.archetype_title})

{archetype.description}

What's YOUR anime trauma? 👉 https://yokaizen.app/soul

#AnimeTrauma #SoulCard #Yokaizen"""
        
        # TODO: Generate actual card image using DesignAgent when available
        card_image_url = None
        qr_code_url = None
        
        return SoulCardResponse(
            archetype=archetype,
            card_image_url=card_image_url,
            share_text=share_text,
            app_download_url="https://yokaizen.app/download",
            qr_code_url=qr_code_url,
        )
        
    except Exception as e:
        logger.error("Soul card generation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate soul card: {str(e)}"
        )


@router.get("/soul-card/archetypes")
async def list_archetypes():
    """
    List all available anime archetypes (for debugging/preview).
    """
    return {
        "archetypes": [
            {
                "key": key,
                "name": data["archetype_name"],
                "title": data["archetype_title"],
                "anime": data["anime_reference"],
            }
            for key, data in ARCHETYPE_DATABASE.items()
        ]
    }
