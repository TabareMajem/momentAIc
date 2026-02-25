"""
Guerrilla Campaign Agent
Physical/Digital bridge campaigns for guerrilla marketing.

Campaigns:
1. Guerilla Amazon - Mock product placement images
2. Relationship Parking Tickets - Printable citations
3. Wedding Registry Embed - "Know the Couple" game iframe
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

class ProductMockupConcept(BaseModel):
    """Concept for a fake product placement image"""
    product_name: str = Field(description="Name on the box")
    tagline: str = Field(description="Box tagline")
    box_copy: List[str] = Field(description="Bullet points on box")
    visual_description: str = Field(description="What the box should look like")
    store_setting: str = Field(description="Where to photoshop it (Target, Walmart, etc)")
    reddit_caption: str = Field(description="r/gaming or r/mildlyinteresting caption")


class ParkingTicket(BaseModel):
    """A 'Relationship Parking Ticket' content"""
    violation_code: str = Field(description="Official-looking violation code")
    violation_type: str = Field(description="The relationship 'offense'")
    violation_description: str = Field(description="Detailed description")
    fine: str = Field(description="The 'penalty'")
    issuing_officer: str = Field(description="Fictional officer name")
    date_issued: str = Field(description="Date string")
    additional_notes: str = Field(description="Witty additional notes")


class WeddingEmbed(BaseModel):
    """Embeddable 'Know the Couple' game for weddings"""
    game_title: str = Field(description="Title for the game")
    questions: List[Dict[str, Any]] = Field(description="Trivia questions about the couple")
    result_messages: Dict[str, str] = Field(description="Messages for different score ranges")
    embed_code: str = Field(description="HTML iframe code snippet")
    cta_url: str = Field(description="CTA link to BondQuests")


# ═══════════════════════════════════════════════════════════════════════════════
# GUERRILLA CAMPAIGN AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class GuerrillaCampaignAgent:
    """
    Guerrilla Campaign Agent - Physical/Digital Bridge Marketing
    
    Creates content that bridges physical and digital worlds.
    Uses the "Nano Banana" aesthetic (playful, bright, gamified).
    
    Campaigns:
    1. Guerilla Amazon - Realistic fake product boxes
    2. Parking Tickets - Printable relationship citations
    3. Wedding Embed - Iframe game for wedding websites
    """
    
    @property
    def llm(self):
        return get_llm("gemini-flash", temperature=0.75)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CAMPAIGN 1: GUERILLA AMAZON (Fake Product Mockups)
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def generate_product_mockup_concept(
        self,
        product_type: str = "starter_pack",
        style: str = "nano_banana",
        target_store: str = "Target",
        context: Optional[Dict[str, Any]] = None,
    ) -> ProductMockupConcept:
        """
        Generate concept for a realistic fake product box.
        
        Args:
            product_type: starter_pack, expansion, dlc, collector
            style: nano_banana, retro, minimalist
            target_store: Target, Walmart, GameStop
            context: Startup context (name, description, etc.)
            
        Returns:
            ProductMockupConcept with all design specs
        """
        # Default context if not provided
        startup_name = context.get("name", "BondQuests") if context else "BondQuests"
        startup_desc = context.get("description", "relationship gamification app") if context else "relationship gamification app"
        
        if not self.llm:
            return ProductMockupConcept(
                product_name=f"{startup_name} Starter Pack",
                tagline="Relationship DLC for Real Life",
                box_copy=["100+ Quests", "2 Players Required"],
                visual_description="Colorful box with cartoon couple",
                store_setting=f"{target_store} gaming aisle",
                reddit_caption=f"Saw this '{startup_name}' at {target_store} today. Anyone tried it?"
            )
        
        prompt = f"""
Create a concept for a fake physical product box for {startup_name} ({startup_desc}).

GOAL: Make it look like a real product on store shelves.
When posted to social media, it should make people curious enough to search for it.

PRODUCT TYPE: {product_type}
VISUAL STYLE: {style}
TARGET STORE: {target_store}

GENERATE:

1. product_name: Catchy name for the box
   Examples: "{startup_name} Starter Pack", "Expansion Pack", "Collector's Edition"
2. tagline: Under 10 words, punchy
3. box_copy: 4-5 bullet points that would appear on the box
   - Make them sound like real product features
   - Mix humor with value props of the product
   - Return as a list of strings
4. visual_description: What the box should look like
   - Colors, characters, style
   - Should match actual {startup_name} branding ({style})
5. store_setting: Exact placement description for photoshop
   - Example: "{target_store} aisle, between relevant products"
6. reddit_caption: Caption for r/gaming or r/mildlyinteresting post
   - Should sound like genuine discovery, not marketing
   - Example: "Saw this at the store today. Has anyone used it?"

Return as JSON with these exact keys:
{{
    "product_name": "...",
    "tagline": "...",
    "box_copy": ["...", "..."],
    "visual_description": "...",
    "store_setting": "...",
    "reddit_caption": "..."
}}
"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are creating viral guerrilla marketing concepts. Make them realistic and shareable."),
                HumanMessage(content=prompt)
            ])
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return ProductMockupConcept(**data)
                
        except Exception as e:
            logger.error("Product mockup generation failed", error=str(e))
        
        return ProductMockupConcept(
            product_name=f"{startup_name} Starter Pack",
            tagline="Level Up Your Life",
            box_copy=[
                "Premium Features",
                "2 Players Required" if "relationship" in startup_desc else "Enterprise Ready",
                "Unlock Secret Endings" if "game" in startup_desc else "Optimize Workflow",
                "No Microtransactions",
            ],
            visual_description=f"Bright colorful box in {style} style",
            store_setting=f"{target_store} relevant section",
            reddit_caption=f"Found this '{startup_name}' thing at the store. Is this real? 😂"
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CAMPAIGN 2: RELATIONSHIP PARKING TICKETS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def generate_parking_ticket(
        self,
        violation_type: str = "missing_date_night",
        severity: str = "medium",
    ) -> ParkingTicket:
        """
        Generate a "Relationship Parking Ticket" content.
        
        Physical guerrilla marketing: Print official-looking tickets
        that are actually relationship-themed jokes.
        
        Distribution: Hand to Launch Ambassadors to leave on windshields,
        give to friends, etc.
        
        Args:
            violation_type: missing_date_night, doomscrolling, forgetting_anniversary, etc.
            severity: low, medium, high
            
        Returns:
            ParkingTicket with all content
        """
        if not self.llm:
            return ParkingTicket(
                violation_code="RV-420",
                violation_type="Failure to Date Night",
                violation_description="Vehicle owner has not planned a date night in 30+ days",
                fine="Must play 1 Level of BondQuests tonight",
                issuing_officer="Officer Cupid McLovinface",
                date_issued=datetime.datetime.now().strftime("%m/%d/%Y"),
                additional_notes="Repeated violations may result in couch sleeping"
            )
        
        violation_templates = {
            "missing_date_night": "Failure to schedule Date Night",
            "doomscrolling": "Excessive Phone Usage in Partner's Presence",
            "forgetting_anniversary": "Memory Violation: Significant Date Forgotten",
            "toilet_seat": "Restroom Protocol Violation",
            "thermostat": "Unauthorized Climate Control Adjustment",
            "snoring": "Noise Ordinance Violation: Nighttime",
            "blanket_hogging": "Bedding Resource Theft",
            "hangry": "Operating Relationship While Hungry",
        }
        
        violation_desc = violation_templates.get(violation_type, violation_type)
        
        prompt = f"""
Create a funny "Relationship Parking Ticket" that looks official but is actually a joke.

VIOLATION TYPE: {violation_desc}
SEVERITY: {severity}

The ticket should:
- Look official from a distance
- Be funny when read up close
- Include a "fine" that directs to BondQuests
- Include witty officer notes

GENERATE:

1. violation_code: Official-looking code (e.g., "RV-420", "BQ-001")
2. violation_type: The relationship "offense" (formal sounding)
3. violation_description: 1-2 sentences explaining the offense
   - Use official/legal language humorously
4. fine: The "penalty" - must involve BondQuests
   - Example: "Must complete 1 Quest on BondQuests tonight"
   - Example: "Mandatory Sync Test within 24 hours"
5. issuing_officer: Funny fictional name
   - Example: "Officer Cupid McLovinface"
6. additional_notes: Witty officer notes
   - Example: "Suspect appeared genuinely sorry. Still guilty."

Return as JSON with these exact keys:
{{
    "violation_code": "...",
    "violation_type": "...",
    "violation_description": "...",
    "fine": "...",
    "issuing_officer": "...",
    "additional_notes": "..."
}}
"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are writing humorous faux-official documents. Balance humor with official-sounding language."),
                HumanMessage(content=prompt)
            ])
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                data['date_issued'] = datetime.datetime.now().strftime("%m/%d/%Y")
                return ParkingTicket(**data)
                
        except Exception as e:
            logger.error("Parking ticket generation failed", error=str(e))
        
        return ParkingTicket(
            violation_code="RV-001",
            violation_type=violation_desc,
            violation_description=f"Owner observed {violation_type.replace('_', ' ')}. This is a Class A relationship misdemeanor.",
            fine="Complete 1 BondQuest within 24 hours",
            issuing_officer="Officer L. O'Vehard",
            date_issued=datetime.datetime.now().strftime("%m/%d/%Y"),
            additional_notes="Payment must be made in Quality Time."
        )
    
    async def generate_ticket_batch(
        self,
        count: int = 5,
    ) -> List[ParkingTicket]:
        """Generate a variety of parking tickets for printing."""
        violations = [
            "missing_date_night",
            "doomscrolling",
            "forgetting_anniversary",
            "thermostat",
            "blanket_hogging",
            "hangry",
        ]
        
        tickets = []
        for i, violation in enumerate(violations[:count]):
            ticket = await self.generate_parking_ticket(
                violation_type=violation,
                severity=["low", "medium", "high"][i % 3],
            )
            tickets.append(ticket)
        
        return tickets
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CAMPAIGN 3: WEDDING EMBED (Know the Couple Game)
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def generate_wedding_embed(
        self,
        couple_data: Dict[str, Any],
        question_count: int = 5,
    ) -> WeddingEmbed:
        """
        Generate embeddable "Know the Couple" game for wedding websites.
        
        Viral loop: Every wedding guest plays → sees BondQuests CTA at end.
        One wedding = 150+ potential users.
        
        Args:
            couple_data: Info about the couple
                - partner1_name: str
                - partner2_name: str
                - how_they_met: str
                - fun_facts: List[str]
                - wedding_date: str
            question_count: Number of trivia questions
            
        Returns:
            WeddingEmbed with questions and embed code
        """
        if not self.llm:
            return WeddingEmbed(
                game_title="How Well Do You Know Us?",
                questions=[],
                result_messages={},
                embed_code="<iframe src='https://bondquests.com/wedding-game'></iframe>",
                cta_url="https://bondquests.com"
            )
        
        data = couple_data or {
            "partner1_name": "Partner 1",
            "partner2_name": "Partner 2",
            "how_they_met": "At a coffee shop",
            "fun_facts": ["They both love hiking", "Met on vacation"],
            "wedding_date": "2026-06-15",
        }
        
        prompt = f"""
Create a "How Well Do You Know the Couple?" trivia game for a wedding website.

COUPLE INFO:
- Names: {data.get('partner1_name')} & {data.get('partner2_name')}
- How they met: {data.get('how_they_met')}
- Fun facts: {data.get('fun_facts', [])}

GENERATE {question_count} QUESTIONS:

Each question should:
- Be about the couple's relationship
- Have 4 multiple choice answers
- Be fun and reveal cute details about them
- Mix easy and hard questions

ALSO GENERATE:

1. GAME TITLE: Fun title for the trivia game

2. RESULT MESSAGES: Messages for different score ranges
   - 0-20%: "Better luck next time!"
   - 21-50%: "You know the basics!"
   - 51-80%: "Inner circle status!"
   - 81-100%: "Best friend material!"

Return as JSON:
{{
    "game_title": "...",
    "questions": [
        {{
            "question": "...",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }}
    ],
    "result_messages": {{
        "0-20": "...",
        "21-50": "...",
        "51-80": "...",
        "81-100": "..."
    }}
}}
"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are creating fun wedding content. Keep it celebratory and appropriate for all guests."),
                HumanMessage(content=prompt)
            ])
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                
                # Generate embed code
                game_id = f"wedding-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                embed_code = f'''<iframe 
    src="https://bondquests.com/wedding-game/{game_id}" 
    width="100%" 
    height="600" 
    frameborder="0" 
    style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
</iframe>
<p style="text-align: center; margin-top: 8px; font-size: 12px; color: #666;">
    Powered by <a href="https://bondquests.com" target="_blank">BondQuests</a>
</p>'''
                
                return WeddingEmbed(
                    game_title=data.get('game_title', 'How Well Do You Know Us?'),
                    questions=data.get('questions', []),
                    result_messages=data.get('result_messages', {}),
                    embed_code=embed_code,
                    cta_url="https://bondquests.com",
                )
                
        except Exception as e:
            logger.error("Wedding embed generation failed", error=str(e))
        
        return WeddingEmbed(
            game_title="How Well Do You Know Us?",
            questions=[],
            result_messages={},
            embed_code="<iframe src='https://bondquests.com/wedding-game'></iframe>",
            cta_url="https://bondquests.com"
        )
    
    def get_embed_installation_guide(self) -> str:
        """Get markdown guide for embedding on wedding websites."""
        return """
# Embedding BondQuests on Your Wedding Website

## For Zola, The Knot, or Similar Platforms:

1. Create a custom page on your wedding website
2. Look for "Add Custom HTML" or "Embed Code" option
3. Paste your embed code

## Direct HTML Embed:

```html
<iframe 
    src="https://bondquests.com/wedding-game/YOUR-GAME-ID" 
    width="100%" 
    height="600" 
    frameborder="0">
</iframe>
```

## WordPress:

1. Add a "Custom HTML" block
2. Paste the embed code
3. Preview and publish

## Tips:
- Works on mobile too!
- Guests can share their scores
- Results help break the ice at the reception

Questions? Email weddings@bondquests.com
"""


# Singleton instance
guerrilla_campaign_agent = GuerrillaCampaignAgent()
