
from typing import Dict, Any, List, Optional
import structlog
from app.agents.base import get_llm, get_agent_config
from app.models.conversation import AgentType
from langchain_core.messages import HumanMessage, SystemMessage

logger = structlog.get_logger()

class AmbassadorAgent:
    """
    Ambassador Agent - Handles High-Net-Worth Partnerships & Stripe Connect
    Focus: Revenue Sharing Models, Deal Structuring, "White Glove" Onboarding
    """
    
    def __init__(self):
        # We reuse the MARKETING config for now but with specialized prompts
        self.llm = get_llm("gemini-flash", temperature=0.4) # Lower temp for serious negotiation

    async def generate_partnership_proposal(self, prospect: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a dynamic Revenue Share proposal based on prospect data.
        """
        name = prospect.get('contact_name', 'Partner')
        company = prospect.get('company_name', 'Company')
        audience_size = prospect.get('audience_size', 50000) # Default assumption
        
        # 1. Calculate Projected Revenue (Mock Logic)
        conversion_rate = 0.02
        arpu = 29.0 # Average Revenue Per User
        monthly_earnings = (audience_size * conversion_rate) * arpu * 0.30 # 30% comms
        
        # 2. Draft the Proposal
        prompt = f"""
        Draft a high-end partnership proposal for {name} ({company}).
        
        The Deal:
        - Tech: Stripe Connect Split Payments
        - Commission: 30% Lifetime recurring
        - Projected Earnings: ${monthly_earnings:,.0f}/month (based on {audience_size:,} audience)
        
        Tone: "Peer-to-Peer", "Business-Casual", NOT "Salesy".
        
        Structure:
        1. Subject Line (Low friction)
        2. Permissionless Value (We already set up their dashboard)
        3. The Numbers (The projected earnings)
        4. The Ask (15 min strategy call)
        """
        
        response = await self.llm.ainvoke([
            SystemMessage(content="You are a Partnership Director at a $10M ARR startup."),
            HumanMessage(content=prompt)
        ])
        
        return {
            "prospect": name,
            "projected_revenue": monthly_earnings,
            "proposal_draft": response.content,
            "status": "ready_for_review"
        }

    async def send_proposal(self, prospect: Dict[str, Any], proposal_text: str) -> Dict[str, Any]:
        """
        [REAL ACTION] Sends the Revenue Share Proposal to the prospect.
        """
        email_address = prospect.get("email") or prospect.get("contact_email")
        # Fallback for demo if no email in dict
        if not email_address:
             email_address = f"{prospect.get('contact_name', 'partner').replace(' ', '.').lower()}@example.com"
        
        logger.info(f"Ambassador: Sending Proposal to {email_address}...")
        
        from app.integrations.gmail import gmail_integration
        
        # Subject line extraction (hacky but works for now)
        subject = "Partnership Proposal: Revenue Share Model"
        if "Subject:" in proposal_text:
             try:
                 subject = proposal_text.split("Subject:")[1].split("\n")[0].strip()
             except Exception:
                 pass

        try:
            result = await gmail_integration.execute_action("send_email", {
                "to": email_address,
                "subject": subject,
                "body": proposal_text,
                "sender_email": None 
            })
            return result
        except Exception as e:
            logger.error("Ambassador: Send Failed", error=str(e))
            return {"success": False, "error": str(e)}

ambassador_agent = AmbassadorAgent()
