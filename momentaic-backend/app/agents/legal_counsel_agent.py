"""
Legal Counsel Agent
AI-powered legal advisor for startups
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import structlog

from app.agents.base import (
    AgentState,
    get_llm,
    get_agent_config,
    web_search,
)
from app.models.conversation import AgentType

logger = structlog.get_logger()


class LegalCounselAgent:
    """
    Legal Counsel Agent - Expert in startup legal matters
    
    Capabilities:
    - Contract review and analysis
    - Term sheet guidance
    - IP and trademark advice
    - Employment law basics
    - Compliance overview
    - Founder agreement insights
    
    DISCLAIMER: This agent provides general guidance only, not legal advice.
    Always consult a qualified attorney for legal matters.
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.LEGAL_COUNSEL)
        self.llm = get_llm("gemini-pro", temperature=0.3)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process a legal question or request
        """
        if not self.llm:
            return {"response": "AI Service Unavailable. Please configure keys.", "agent": AgentType.LEGAL_COUNSEL.value, "error": True}
        
        try:
            context_section = self._build_context(startup_context)
            
            prompt = f"""{context_section}

User Question: {message}

As a Legal Counsel AI, provide:
1. General guidance on this matter
2. Key considerations and risks
3. Common practices in the industry
4. Questions to ask a real lawyer
5. Relevant document templates to consider

IMPORTANT: Always include a disclaimer that this is general guidance, not legal advice."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": AgentType.LEGAL_COUNSEL.value,
                "disclaimer": "This is general guidance, not legal advice. Consult a qualified attorney.",
                "tools_used": [],
            }
            
        except Exception as e:
            logger.error("Legal Counsel agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": AgentType.LEGAL_COUNSEL.value, "error": True}
    
    async def review_contract(
        self,
        contract_type: str,
        contract_summary: str,
        key_terms: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Review a contract and identify key points
        """
        if not self.llm:
            return {"review": "AI Service Unavailable", "risk_level": "unknown", "agent": AgentType.LEGAL_COUNSEL.value, "error": True}
        
        prompt = f"""Review this {contract_type} contract:

Summary: {contract_summary}

Key Terms:
{self._format_terms(key_terms)}

Provide:
1. Assessment of terms (favorable/neutral/unfavorable)
2. Red flags or concerning clauses
3. Missing important clauses
4. Negotiation suggestions
5. Industry standard comparison
6. Questions to clarify with the other party"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "review": response.content,
                "risk_level": "medium",  # Would be calculated in production
                "agent": AgentType.LEGAL_COUNSEL.value,
                "disclaimer": "This is general guidance, not legal advice.",
            }
        except Exception as e:
            logger.error("Contract review failed", error=str(e))
            return {"review": f"Error: {str(e)}", "risk_level": "unknown", "agent": AgentType.LEGAL_COUNSEL.value, "error": True}
    
    async def term_sheet_analysis(
        self,
        terms: Dict[str, Any],
        round_type: str = "Seed",
    ) -> Dict[str, Any]:
        """
        Analyze investment term sheet
        """
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "founder_friendly_score": 0, "agent": AgentType.LEGAL_COUNSEL.value, "error": True}
        
        prompt = f"""Analyze this {round_type} round term sheet:

Terms:
- Valuation: ${terms.get('valuation', 0):,} ({terms.get('valuation_type', 'pre-money')})
- Investment Amount: ${terms.get('investment', 0):,}
- Liquidation Preference: {terms.get('liquidation_pref', '1x non-participating')}
- Board Seats: {terms.get('board_seats', 'Unknown')}
- Pro-rata Rights: {terms.get('pro_rata', 'Yes')}
- Anti-dilution: {terms.get('anti_dilution', 'Broad-based weighted average')}
- Vesting: {terms.get('vesting', '4 years, 1 year cliff')}

Provide:
1. Overall assessment (founder-friendly / balanced / investor-friendly)
2. Term-by-term analysis
3. Comparison to market standards
4. Negotiation priorities
5. Deal-breakers to watch for
6. Implications for future rounds"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "founder_friendly_score": self._calculate_founder_score(terms),
                "agent": AgentType.LEGAL_COUNSEL.value,
                "disclaimer": "This is general guidance, not legal advice.",
            }
        except Exception as e:
            logger.error("Term sheet analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "founder_friendly_score": 0, "agent": AgentType.LEGAL_COUNSEL.value, "error": True}
    
    async def compliance_check(
        self,
        industry: str,
        location: str,
        business_model: str,
    ) -> Dict[str, Any]:
        """
        Check basic compliance requirements
        """
        if not self.llm:
            return {"compliance_guide": "AI Service Unavailable", "agent": AgentType.LEGAL_COUNSEL.value, "error": True}
        
        prompt = f"""Outline compliance requirements for:

Industry: {industry}
Location: {location}
Business Model: {business_model}

Provide:
1. Key regulations to be aware of
2. Required registrations/licenses
3. Data privacy requirements (GDPR, CCPA, etc.)
4. Industry-specific compliance
5. Common compliance mistakes
6. Timeline for compliance activities"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "compliance_guide": response.content,
                "agent": AgentType.LEGAL_COUNSEL.value,
                "disclaimer": "This is general guidance. Verify requirements with local authorities.",
            }
        except Exception as e:
            logger.error("Compliance check failed", error=str(e))
            return {"compliance_guide": f"Error: {str(e)}", "agent": AgentType.LEGAL_COUNSEL.value, "error": True}
    
    def _get_system_prompt(self) -> str:
        """Get enhanced system prompt with disclaimers"""
        return """You are the Legal Counsel AI agent for MomentAIc.

Your role is to provide general guidance on legal matters for startups.

IMPORTANT RULES:
1. ALWAYS include a disclaimer that this is not legal advice
2. Recommend consulting a qualified attorney for specific matters
3. Focus on common practices and general principles
4. Highlight risks and considerations
5. Be conservative in your guidance

Areas of expertise:
- Startup incorporation and structure
- Founder agreements and equity
- Investment terms and fundraising documents
- Employment basics (offer letters, NDAs)
- IP and trademark basics
- Contract fundamentals
- Privacy and data protection overview

Never provide specific legal advice or guarantee outcomes."""
    
    def _build_context(self, startup_context: Dict[str, Any]) -> str:
        """Build startup context"""
        return f"""Startup Context:
- Name: {startup_context.get('name', 'Unknown')}
- Industry: {startup_context.get('industry', 'Technology')}
- Stage: {startup_context.get('stage', 'Early Stage')}
- Location: {startup_context.get('location', 'United States')}"""
    
    def _format_terms(self, terms: Dict[str, Any]) -> str:
        """Format contract terms for prompt"""
        return "\n".join(f"- {k}: {v}" for k, v in terms.items())
    
    def _calculate_founder_score(self, terms: Dict[str, Any]) -> int:
        """Calculate founder-friendly score (1-100)"""
        score = 50
        
        # Liquidation preference
        liq_pref = terms.get('liquidation_pref', '')
        if 'non-participating' in liq_pref.lower():
            score += 15
        elif 'participating' in liq_pref.lower():
            score -= 15
        
        # Anti-dilution
        anti_dil = terms.get('anti_dilution', '')
        if 'broad-based' in anti_dil.lower():
            score += 10
        elif 'full ratchet' in anti_dil.lower():
            score -= 20
        
        # Board
        board = terms.get('board_seats', '')
        if 'founder majority' in str(board).lower():
            score += 15
        
        return max(0, min(100, score))
    


# Singleton instance
legal_counsel_agent = LegalCounselAgent()
