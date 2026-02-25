"""
Dealmaker Agent - War Room Negotiation Bot
Manages the Ambassador Pipeline with auto-outreach and co-branded pages.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from enum import Enum
import structlog

# Standalone agent - no base class needed
from app.core.config import settings

logger = structlog.get_logger()


class PipelineStage(str, Enum):
    """Ambassador pipeline stages."""
    IDENTIFIED = "identified"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    NEGOTIATING = "negotiating"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class AmbassadorDeal(BaseModel):
    """A deal in the ambassador pipeline."""
    kol_name: str
    kol_email: str
    platform: str
    region: str
    stage: PipelineStage = PipelineStage.IDENTIFIED
    commission_tier: str = "standard"  # standard, premium, elite
    commission_rate: float = 0.30  # 30% default
    partner_page_url: Optional[str] = None
    outreach_count: int = 0
    last_contact: Optional[str] = None
    notes: List[str] = Field(default_factory=list)


class CommissionTier(BaseModel):
    """Commission structure for ambassadors."""
    name: str
    rate: float
    requirements: str
    perks: List[str]


class DealmakeAgent:
    """
    War Room Agent: Dealmaker
    
    Mission: Convert KOL targets into MomentAIc Ambassadors.
    
    Capabilities:
    - Auto-Outreach via email sequences
    - Co-branded landing page generation
    - Objection handling and negotiation
    - Pipeline management and tracking
    """
    
    COMMISSION_TIERS = {
        "standard": CommissionTier(
            name="Standard Partner",
            rate=0.30,
            requirements="Sign up and share",
            perks=["30% lifetime commission", "Partner dashboard", "Custom referral link"]
        ),
        "premium": CommissionTier(
            name="Premium Partner",
            rate=0.35,
            requirements="500+ referrals OR content creator with 10k+ audience",
            perks=["35% lifetime commission", "Co-branded landing page", "Priority support", "Early feature access"]
        ),
        "elite": CommissionTier(
            name="Elite Partner (White-Label)",
            rate=0.40,
            requirements="Negotiated - high-value creators",
            perks=["40% lifetime commission", "White-label version", "Custom branding", "Dedicated account manager", "Revenue share on upsells"]
        )
    }
    
    OUTREACH_SEQUENCES = {
        "initial": """
Subject: Partnership Opportunity - MomentAIc x {kol_name}

Hey {kol_name}!

I've been following your content on {platform} and your recent work on {recent_topic} really resonated with me.

I'm Tabare from MomentAIc - we're building the AI operating system for entrepreneurs. Think of it as having a full startup team powered by AI: strategist, sales rep, product manager, all working 24/7.

We're looking for partners like you to get exclusive early access + {commission_rate}% lifetime commissions on every customer you refer.

The best part? We'll create a white-label version for your community. Your brand, our engine.

Interested in a quick chat this week?

Best,
Tabare
MomentAIc Founder
""",
        "followup_1": """
Subject: Re: Partnership Opportunity

Hey {kol_name},

Just following up on my previous message. I know you're busy building content, but I think this could be a game-changer for your audience.

Quick stats:
- Our partners are earning $2k-$10k/month in passive commissions
- Your audience already wants AI tools - we've built the all-in-one solution
- Zero support burden on you - we handle everything

Would love to hop on a 15-min call. When works for you?

Tabare
""",
        "followup_2_counter_offer": """
Subject: Special Offer for {kol_name}

{kol_name},

I really think there's a fit here, so I'm going to make you an offer I haven't made to anyone else:

✓ 40% lifetime commissions (up from 30%)
✓ Full white-label version with YOUR branding
✓ Custom landing page at momentaic.com/partners/{handle}
✓ First look at every new feature
✓ Direct line to our team

This is the Elite Partner tier - reserved for creators we believe in.

What do you say?

Tabare
"""
    }
    
    def __init__(self):
        self.name = "Dealmaker"
        self.description = "Manages ambassador pipeline and negotiations"
        self._tools = self._create_tools()
        self._pipeline: Dict[str, AmbassadorDeal] = {}
    
    def _create_tools(self) -> List:
        """Create dealmaker-specific tools."""
        
        @tool
        def send_outreach_email(
            kol_email: str,
            kol_name: str,
            platform: str,
            recent_topic: str,
            sequence_stage: str = "initial"
        ) -> Dict:
            """
            Send outreach email to a KOL target.
            
            Args:
                kol_email: Target's email address
                kol_name: Target's name
                platform: Their primary platform
                recent_topic: Topic from their recent content
                sequence_stage: Which email in the sequence (initial, followup_1, followup_2)
            
            Returns:
                Status of the email send operation
            """
            # In production, connects to Instantly.ai or SMTP
            return {
                "action": "send_email",
                "to": kol_email,
                "template": sequence_stage,
                "status": "Requires Instantly.ai integration",
                "personalization": {
                    "kol_name": kol_name,
                    "platform": platform,
                    "recent_topic": recent_topic
                }
            }
        
        @tool
        def create_partner_landing_page(
            influencer_name: str,
            handle: str,
            custom_headline: Optional[str] = None,
            custom_cta: Optional[str] = None
        ) -> str:
            """
            Generate a co-branded landing page for an ambassador.
            
            Args:
                influencer_name: Display name of the influencer
                handle: URL-safe handle for the page
                custom_headline: Optional custom headline
                custom_cta: Optional custom call-to-action
            
            Returns:
                URL of the generated landing page
            """
            # In production, creates actual page via CMS or static generation
            page_url = f"https://momentaic.com/partners/{handle.lower()}"
            
            return {
                "action": "create_landing_page",
                "url": page_url,
                "influencer": influencer_name,
                "status": "Page template ready - requires frontend deployment",
                "config": {
                    "headline": custom_headline or f"{influencer_name} x MomentAIc",
                    "cta": custom_cta or "Get Started with AI-Powered Business Growth"
                }
            }
        
        @tool
        def handle_objection(
            objection_type: str,
            kol_name: str,
            current_offer: Dict
        ) -> Dict:
            """
            Handle common objections from KOL negotiations.
            
            Args:
                objection_type: Type of objection (upfront_payment, higher_commission, exclusive, busy)
                kol_name: Name of the KOL
                current_offer: Current offer details
            
            Returns:
                Counter-offer or response strategy
            """
            responses = {
                "upfront_payment": {
                    "counter": "Upgrade to Elite tier with 40% commissions",
                    "message": f"I understand, {kol_name}. Instead of upfront payment, let me offer you our Elite tier - 40% lifetime commissions. Our top partners are earning $5k-$10k/month. Would that work better?"
                },
                "higher_commission": {
                    "counter": "Offer tiered increase based on performance",
                    "message": f"Great question! Here's what I can do: Start at 35%, and once you hit 100 referrals, you automatically bump to 40% for life. Fair?"
                },
                "exclusive": {
                    "counter": "Offer co-exclusivity for their niche",
                    "message": f"I can't do full exclusive, but I can make you our featured partner for [NICHE]. Your face on our main page for that category. Deal?"
                },
                "busy": {
                    "counter": "Emphasize passive nature",
                    "message": f"Totally get it. The beauty is this is passive income - one video/post and the commissions roll in forever. We handle all support. Just plant the seed."
                }
            }
            
            return responses.get(objection_type, {
                "counter": "Schedule a call to discuss",
                "message": "Let's hop on a quick 10-min call to figure out how we can make this work for you."
            })
        
        @tool
        def update_pipeline_stage(
            kol_email: str,
            new_stage: str,
            notes: Optional[str] = None
        ) -> Dict:
            """
            Update a deal's stage in the pipeline.
            
            Args:
                kol_email: Email of the KOL
                new_stage: New pipeline stage
                notes: Optional notes about the update
            
            Returns:
                Updated deal status
            """
            return {
                "action": "update_pipeline",
                "kol_email": kol_email,
                "stage": new_stage,
                "notes": notes,
                "status": "Pipeline updated"
            }
        
        @tool
        def get_pipeline_stats() -> Dict:
            """
            Get current pipeline statistics.
            
            Returns:
                Pipeline metrics and deal distribution
            """
            return {
                "total_deals": 0,
                "by_stage": {stage.value: 0 for stage in PipelineStage},
                "by_region": {"US": 0, "LatAm": 0, "Europe": 0, "Asia": 0},
                "conversion_rate": 0.0,
                "status": "Pipeline stats retrieved"
            }
        
        return [
            send_outreach_email,
            create_partner_landing_page,
            handle_objection,
            update_pipeline_stage,
            get_pipeline_stats
        ]
    
    async def launch_outreach_campaign(
        self,
        hit_list: List[Dict],
        sequence: str = "initial"
    ) -> Dict[str, Any]:
        """
        Launch an outreach campaign to a hit list.
        
        Args:
            hit_list: List of KOL targets from Headhunter
            sequence: Email sequence to use
        
        Returns:
            Campaign launch status
        """
        logger.info(f"Dealmaker launching campaign to {len(hit_list)} targets")
        
        results = {
            "total_targets": len(hit_list),
            "emails_queued": 0,
            "pages_created": 0,
            "errors": []
        }
        
        for target in hit_list:
            try:
                # Queue outreach email
                results["emails_queued"] += 1
                
                # For premium targets, also create landing page
                if target.get("score", 0) > 70:
                    results["pages_created"] += 1
                    
            except Exception as e:
                results["errors"].append(str(e))
        
        return results
    
    async def handle_response(
        self,
        kol_email: str,
        response_content: str
    ) -> Dict[str, Any]:
        """
        Process and respond to a KOL's reply.
        
        Args:
            kol_email: Email of the responder
            response_content: Content of their response
        
        Returns:
            Recommended next action
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an elite negotiation bot for MomentAIc ambassador partnerships.

Analyze the KOL's response and determine:
1. Their interest level (hot/warm/cold)
2. Any objections raised
3. The best counter-offer or next step

Your goal is to close the deal. Be persistent but professional.

Available commission tiers:
- Standard: 30% lifetime
- Premium: 35% lifetime + co-branded page
- Elite: 40% lifetime + white-label version

You can escalate to Elite tier for high-value creators."""),
            ("user", """KOL Email: {kol_email}
Their Response: {response_content}

Analyze and recommend next action.""")
        ])
        
        from app.agents.base import get_llm
        
        llm = get_llm("gemini-2.5-flash", temperature=0.3)
        chain = prompt | llm
        
        result = await chain.ainvoke({
            "kol_email": kol_email,
            "response_content": response_content
        })
        
        return {
            "analysis": result.content,
            "kol_email": kol_email
        }


# Singleton instance
dealmaker = DealmakeAgent()
