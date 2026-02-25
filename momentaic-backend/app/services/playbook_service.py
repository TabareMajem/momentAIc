"""
Industry Playbook Service
Delivers pre-configured, high-converting agent strategies tailored to a startup's industry.
This drives bottom-up activation by solving the 'blank canvas' problem.
"""

from typing import Dict, List, Any
import structlog

logger = structlog.get_logger()

# Hardcoded playbooks for the MVP to ensure high quality "Wow" factor.
PLAYBOOK_DB = {
    "SaaS": [
        {
            "id": "saas_outbound_engine",
            "title": "B2B Outbound Engine",
            "description": "Have the Sales Rep draft targeted cold outreach sequences for tech decision makers.",
            "agent_type": "sales_agent",
            "initial_prompt": "I need a 3-step cold email sequence targeting VP of Engineering at mid-sized SaaS companies. Focus on how our tool saves 15 hours of developer time per week. Keep emails under 100 words, use a casual but professional tone, and include a clear call to action for a 15-minute sync."
        },
        {
            "id": "saas_onboarding_audit",
            "title": "Frictionless Onboarding Audit",
            "description": "Deploy the Onboarding Coach to review and optimize your user's first 5 minutes.",
            "agent_type": "onboarding_coach",
            "initial_prompt": "Review my standard SaaS onboarding flow: 1. Sign up with Google, 2. Invite team members, 3. Connect data source. Identify where users are most likely to drop off and give me 3 actionable ways to improve the 'Time to Value' (TTV) within the first session."
        }
    ],
    "E-commerce": [
        {
            "id": "ecom_bfcm_campaign",
            "title": "BFCM Promotion Strategy",
            "description": "Ask the Growth Hacker to design a multi-channel Black Friday/Cyber Monday campaign.",
            "agent_type": "growth_hacker",
            "initial_prompt": "Design a Black Friday/Cyber Monday promotional strategy for my e-commerce brand. Include timelines for teaser emails, VIP early access, main sale announcements, and cart abandonment SMS tactics. Aim for urgency without being overly aggressive."
        },
        {
            "id": "ecom_influencer_outreach",
            "title": "Micro-Influencer Sourcing",
            "description": "Have the Content Creator draft DM templates for TikTok/IG creators.",
            "agent_type": "content_creator",
            "initial_prompt": "Write a DM template to reach out to micro-influencers (10k-50k followers) on TikTok and Instagram. The goal is to offer them free product in exchange for an honest unboxing video. Keep it authentic, brief, and mention we love their specific style of content."
        }
    ],
    "Fintech": [
        {
            "id": "fintech_compliance_check",
            "title": "Marketing Compliance Review",
            "description": "Run landing page copy past the Legal Counsel to avoid regulatory red flags.",
            "agent_type": "legal_agent",
            "initial_prompt": "Review this landing page copy for a new consumer fintech investing app: 'Guaranteed 12% returns every year. Never lose money in the stock market again.' Rewrite this to be compliant with standard SEC/FINRA marketing guidelines while still sounding appealing to retail investors."
        },
        {
            "id": "fintech_viral_loop",
            "title": "Referral Program Design",
            "description": "Brainstorm high-K-factor referral mechanics with the Growth Hacker.",
            "agent_type": "growth_hacker",
            "initial_prompt": "I want to design a 'Give $20, Get $20' referral program for my fintech app. Outline the optimal user journey, edge cases to prevent fraud, and suggestions for the push notification strategy to remind users to refer friends after their first successful transaction."
        }
    ],
    "General": [
        {
            "id": "general_pitch_deck",
            "title": "Seed Deck Narrative",
            "description": "Let the Fundraising Coach refine your 10-slide story.",
            "agent_type": "fundraising_coach",
            "initial_prompt": "I'm raising a $2M Seed round. Help me structure the narrative flow for my 10-slide pitch deck. What should the 'Problem' and 'Solution' slides focus on to best capture a VC's attention in the first 3 minutes of a meeting?"
        },
        {
            "id": "general_competitor_teardown",
            "title": "Competitor Teardown",
            "description": "Get an immediate landscape analysis from the Competitor Intel agent.",
            "agent_type": "competitor_intel",
            "initial_prompt": "I am an early-stage startup. Tell me what information you need from me to perform a SWOT analysis against my top 3 competitors, and how you would structure that final report."
        }
    ]
}

class PlaybookService:
    """
    Returns relevant playbooks to bootstrap agent conversations.
    """
    
    def get_playbooks_for_industry(self, industry: str) -> List[Dict[str, Any]]:
        """
        Fetch playbooks. Falls back to 'General' if the exact industry isn't strongly typed.
        We do a fuzzy match on the key for better UX.
        """
        normalized_industry = industry.lower()
        
        # Try to find a specific match
        for key, playbooks in PLAYBOOK_DB.items():
            if key != "General" and key.lower() in normalized_industry:
                return playbooks + PLAYBOOK_DB["General"]
                
        # Fallback to general playbooks if no match
        return PLAYBOOK_DB["General"]

# Singleton
playbook_service = PlaybookService()
