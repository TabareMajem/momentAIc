"""
Viral Campaign Agent
Orchestrates viral growth hacks and shareable content generation.

Campaigns:
1. Exit Survey ("The Ex-Files") - Breakup feedback microgame content
2. Wedding Vow Generator - AI-powered personalized vows (SEO play)
3. Relationship Stats Cards - Shareable "character sheets"
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import structlog
import datetime
import json
import re

from app.agents.base import get_llm

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class ExitSurveyContent(BaseModel):
    """Content for the Exit Survey microgame"""
    intro_screen_text: str = Field(description="Opening screen copy")
    questions: List[Dict[str, Any]] = Field(description="Survey questions with options")
    result_categories: List[Dict[str, str]] = Field(description="Result archetypes")
    share_text: str = Field(description="Shareable result text")
    cta_text: str = Field(description="Call to action for BondQuests")


class WeddingVow(BaseModel):
    """Generated wedding vow content"""
    opening_line: str = Field(description="Attention-grabbing opener")
    body: str = Field(description="Main vow content")
    closing_promise: str = Field(description="Final memorable promise")
    full_vow: str = Field(description="Complete vow text")
    gaming_references: List[str] = Field(description="Gaming/gamification references used")


class RelationshipStatsCard(BaseModel):
    """Character sheet style relationship stats"""
    character_name: str = Field(description="User's 'character name'")
    level: int = Field(description="Overall relationship level")
    class_type: str = Field(description="Relationship archetype (e.g., 'The Romantic Tank')")
    stats: Dict[str, int] = Field(description="RPG-style stat values (1-99)")
    special_abilities: List[str] = Field(description="Unique relationship 'powers'")
    weaknesses: List[str] = Field(description="Areas for improvement")
    share_text: str = Field(description="Shareable summary")


# ═══════════════════════════════════════════════════════════════════════════════
# VIRAL CAMPAIGN AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class ViralCampaignAgent:
    """
    Viral Campaign Agent - Growth Hack Orchestrator
    
    Generates shareable, viral content that drives organic acquisition.
    All content uses the "Nano Banana" aesthetic (playful, gamified).
    
    Campaigns:
    1. Exit Survey - "What went wrong?" microgame for breakups
    2. Wedding Vows - AI-powered, gamified wedding vows
    3. Stats Cards - "Character sheets" for relationships
    """
    
    @property
    def llm(self):
        return get_llm("gemini-flash", temperature=0.8)
    
    @property
    def creative_llm(self):
        """Higher creativity for viral content"""
        return get_llm("gemini-flash", temperature=0.9)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CAMPAIGN 1: EXIT SURVEY ("THE EX-FILES")
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def generate_exit_survey_content(
        self,
        tone: str = "playful",
        include_categories: List[str] = None,
    ) -> ExitSurveyContent:
        """
        Generate content for the "Exit Survey" viral microgame.
        
        Hook: "Breaking up? Send them the BondQuests Exit Survey to find
        out what went wrong so you don't repeat it."
        
        Args:
            tone: playful, serious, sarcastic
            include_categories: Categories to rate (e.g., Communication, Intimacy)
            
        Returns:
            ExitSurveyContent with all game copy
        """
        if not self.llm:
            return ExitSurveyContent(
                intro_screen_text="",
                questions=[],
                result_categories=[],
                share_text="",
                cta_text=""
            )
        
        categories = include_categories or [
            "Communication",
            "Intimacy",
            "Humor",
            "Reliability",
            "Adventure",
            "Hygiene"
        ]
        
        prompt = f"""
Create content for a viral "Exit Interview" microgame for breakups.

CONCEPT:
- Someone sends this to their ex after a breakup
- The ex rates their partner on relationship categories
- Results generate a "Character Sheet" showing relationship stats
- Shareable, funny, slightly controversial

TONE: {tone}
CATEGORIES TO INCLUDE: {', '.join(categories)}

GENERATE:

1. INTRO SCREEN TEXT:
   - Hook that makes people curious
   - Explain what they're about to do
   - Keep it under 50 words

2. QUESTIONS (one per category):
   - Make them specific and amusing
   - Include 4 answer options each (1=bad, 4=great)
   - Example: "When we fought, my ex would:"
     a) Disappear for days
     b) Send passive-aggressive memes
     c) Actually talk it out
     d) Apologize with food

3. RESULT CATEGORIES (5 archetypes):
   - Based on total score ranges
   - Fun character class names
   - Example: "The Emotionally Unavailable Rogue", "The Love Bomber Mage"

4. SHARE TEXT:
   - Template for social sharing
   - Include stats highlights
   - Under 280 chars for Twitter

5. CTA TEXT:
   - Drive to BondQuests signup
   - "Level up for your next relationship"

Return as JSON with fields:
- intro_screen_text
- questions: [{{"category": "", "question": "", "options": ["a", "b", "c", "d"]}}]
- result_categories: [{{"name": "", "score_range": "", "description": ""}}]
- share_text
- cta_text
"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a viral content creator. Make it funny, shareable, and slightly edgy."),
                HumanMessage(content=prompt)
            ])
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return ExitSurveyContent(**data)
            
        except Exception as e:
            logger.error("Exit survey generation failed", error=str(e))
        
        return ExitSurveyContent(
            intro_screen_text="Your ex wants honest feedback. Ready to spill the tea?",
            questions=[],
            result_categories=[],
            share_text="Just got my Relationship Report Card 📊 Lvl 99 Humor, Lvl 2 Listening 😅",
            cta_text="Level up your stats for your next relationship with BondQuests"
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CAMPAIGN 2: WEDDING VOW GENERATOR
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def generate_wedding_vows(
        self,
        bond_stats: Dict[str, Any],
        style: str = "gamer",
        partner_name: str = "Partner",
    ) -> WeddingVow:
        """
        Generate AI-powered, gamified wedding vows.
        
        SEO Play: "AI Wedding Vow Generator" attracts engaged couples.
        Output includes gaming/relationship app references for virality.
        
        Args:
            bond_stats: Dict of relationship facts
                - shared_interests: List[str]
                - inside_jokes: List[str]
                - quirks: List[str]
                - love_story_highlight: str
            style: gamer, romantic, funny, nerdy
            partner_name: Partner's name for personalization
            
        Returns:
            WeddingVow with gamified vow content
        """
        if not self.creative_llm:
            return WeddingVow(
                opening_line="",
                body="",
                closing_promise="",
                full_vow="",
                gaming_references=[]
            )
        
        stats = bond_stats or {
            "shared_interests": ["gaming", "hiking", "cooking"],
            "inside_jokes": ["pizza debates", "IKEA adventures"],
            "quirks": ["steals blankets", "terrible at directions"],
            "love_story_highlight": "Met at a coffee shop"
        }
        
        style_guides = {
            "gamer": "Use gaming terminology (Player 2, respawn, co-op, buff/debuff, achievement unlocked)",
            "romantic": "Classic romantic with modern twists, heartfelt but not cliché",
            "funny": "Make guests laugh, self-deprecating humor, wholesome roasts",
            "nerdy": "References to movies, books, fantasy, or sci-fi fandoms",
        }
        
        prompt = f"""
Write gamified wedding vows for a couple.

PARTNER NAME: {partner_name}

RELATIONSHIP FACTS:
- Shared interests: {', '.join(stats.get('shared_interests', []))}
- Inside jokes: {', '.join(stats.get('inside_jokes', []))}
- Partner quirks: {', '.join(stats.get('quirks', []))}
- Love story highlight: {stats.get('love_story_highlight', 'We met and fell in love')}

STYLE: {style}
STYLE GUIDE: {style_guides.get(style, style_guides['gamer'])}

REQUIREMENTS:
1. OPENING LINE: Hook the audience (one impactful sentence)
2. BODY: 3-4 short paragraphs with specific references to their relationship
3. CLOSING PROMISE: Memorable, quotable final promise
4. GAMING REFERENCES: Weave in 3-5 gaming/gamification terms naturally

RULES:
- Keep total length under 250 words
- Make it personal using their specific facts
- Balance humor with genuine emotion
- Include at least one line that will make guests laugh
- End with something memorable they'll quote

Return JSON:
- opening_line
- body
- closing_promise
- full_vow (combined)
- gaming_references (list of terms used)
"""

        try:
            response = await self.creative_llm.ainvoke([
                SystemMessage(content="You are a creative writer specializing in heartfelt, personalized wedding content."),
                HumanMessage(content=prompt)
            ])
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return WeddingVow(**data)
            else:
                # Use raw response as vow
                return WeddingVow(
                    opening_line="I found my Player 2.",
                    body=content,
                    closing_promise="I promise to always respawn beside you.",
                    full_vow=content,
                    gaming_references=["Player 2", "respawn", "co-op mode"]
                )
                
        except Exception as e:
            logger.error("Wedding vow generation failed", error=str(e))
            return WeddingVow(
                opening_line="",
                body="",
                closing_promise="",
                full_vow="",
                gaming_references=[]
            )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CAMPAIGN 3: RELATIONSHIP STATS CARD
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def generate_relationship_stats_card(
        self,
        user_data: Dict[str, Any],
        visual_style: str = "nano_banana",
    ) -> RelationshipStatsCard:
        """
        Generate a shareable "Character Sheet" for relationships.
        
        Virality: People share their stats on social media.
        Style: Nano Banana playful aesthetic (bright, cute, gamified).
        
        Args:
            user_data: User's relationship data
                - name: str
                - relationship_history: List of key moments
                - strengths: List[str]
                - areas_to_improve: List[str]
                - personality_traits: List[str]
            visual_style: nano_banana, retro_rpg, minimalist
            
        Returns:
            RelationshipStatsCard ready for visualization
        """
        if not self.llm:
            return RelationshipStatsCard(
                character_name="",
                level=1,
                class_type="",
                stats={},
                special_abilities=[],
                weaknesses=[],
                share_text=""
            )
        
        data = user_data or {
            "name": "Player One",
            "relationship_history": ["3 year relationship"],
            "strengths": ["Good listener", "Makes great food"],
            "areas_to_improve": ["Expressing emotions", "Planning dates"],
            "personality_traits": ["Introvert", "Loyal", "Overthinker"]
        }
        
        prompt = f"""
Create a "Relationship Character Sheet" for sharing on social media.

USER DATA:
- Name: {data.get('name', 'Player')}
- History: {data.get('relationship_history', [])}
- Strengths: {data.get('strengths', [])}
- Improve: {data.get('areas_to_improve', [])}
- Traits: {data.get('personality_traits', [])}

VISUAL STYLE: {visual_style}

CREATE:

1. CHARACTER NAME: Fun variant of their name + title
   Example: "Sarah the Steadfast" or "Mike: Certified Cuddler"

2. LEVEL: 1-99 based on relationship experience

3. CLASS TYPE: Relationship archetype
   Examples: "Romantic Tank", "Support Main", "Chaos Healer", "Lone Wolf Converter"

4. STATS (each 1-99):
   - Communication
   - Affection
   - Humor
   - Reliability
   - Adventure
   - Patience
   - Romance
   - Domestic Skills

5. SPECIAL ABILITIES (2-3):
   - Unique relationship "powers" based on strengths
   - Example: "Midnight Snack Summoner", "Expert De-escalator"

6. WEAKNESSES (2):
   - Playful takes on areas to improve
   - Example: "Vulnerable to Silent Treatment", "-50% Date Planning"

7. SHARE TEXT:
   - Twitter-ready summary of their card
   - Include 2-3 highlight stats
   - Under 280 characters

Return as JSON with all fields.
"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are creating fun, shareable character sheets for relationships. Make it playful and positive."),
                HumanMessage(content=prompt)
            ])
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return RelationshipStatsCard(**data)
                
        except Exception as e:
            logger.error("Stats card generation failed", error=str(e))
        
        return RelationshipStatsCard(
            character_name=f"{user_data.get('name', 'Player')} the Adventurer",
            level=42,
            class_type="Romantic Support",
            stats={
                "Communication": 75,
                "Affection": 88,
                "Humor": 82,
                "Reliability": 90,
            },
            special_abilities=["Active Listener", "Comfort Food Chef"],
            weaknesses=["Overthinking Debuff", "Low Initiative on Date Planning"],
            share_text="Just got my Relationship Stats ⚔️ Lvl 42 Romantic Support | 90 Reliability | 88 Affection | Special: Comfort Food Chef 🍕"
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BATCH CAMPAIGN GENERATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def generate_campaign_assets(
        self,
        campaign_type: str,
        variations: int = 3,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple variations of campaign assets.
        
        Args:
            campaign_type: exit_survey, wedding_vows, stats_card
            variations: Number of variations to generate
            **kwargs: Campaign-specific parameters
            
        Returns:
            List of generated assets
        """
        assets = []
        
        if campaign_type == "exit_survey":
            tones = ["playful", "sarcastic", "serious"]
            for tone in tones[:variations]:
                content = await self.generate_exit_survey_content(tone=tone)
                assets.append({
                    "type": "exit_survey",
                    "tone": tone,
                    "content": content.model_dump() if hasattr(content, 'model_dump') else content.__dict__,
                })
                
        elif campaign_type == "wedding_vows":
            styles = ["gamer", "funny", "romantic", "nerdy"]
            for style in styles[:variations]:
                vow = await self.generate_wedding_vows(
                    bond_stats=kwargs.get('bond_stats'),
                    style=style,
                    partner_name=kwargs.get('partner_name', 'Partner'),
                )
                assets.append({
                    "type": "wedding_vows",
                    "style": style,
                    "content": vow.model_dump() if hasattr(vow, 'model_dump') else vow.__dict__,
                })
                
        elif campaign_type == "stats_card":
            styles = ["nano_banana", "retro_rpg", "minimalist"]
            for style in styles[:variations]:
                card = await self.generate_relationship_stats_card(
                    user_data=kwargs.get('user_data'),
                    visual_style=style,
                )
                assets.append({
                    "type": "stats_card",
                    "style": style,
                    "content": card.model_dump() if hasattr(card, 'model_dump') else card.__dict__,
                })
        
        logger.info(
            f"Generated {len(assets)} campaign assets",
            campaign_type=campaign_type,
        )
        
        return assets


# Singleton instance  
viral_campaign_agent = ViralCampaignAgent()
