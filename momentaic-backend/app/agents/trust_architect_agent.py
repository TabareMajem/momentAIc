"""
Trust Architect Agent
Specialized agent for enterprise compliance, security artifacts, and deal negotiations.
Fulfills the "Trust Architect" role from the a16z GTM Playbook.
"""

from typing import Dict, Any, List, Optional
import structlog
import asyncio
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.base import BaseAgent
from app.core.config import settings

logger = structlog.get_logger()

class TrustArchitectAgent(BaseAgent):
    """
    Trust Architect Agent.
    Creates compliance collateral (SOC 2 Summaries, Security Questionnaires, LOIs)
    to unblock enterprise deal cycles.
    """
    
    def __init__(self):
        super().__init__(
            name="Trust Architect",
            role="Head of Security & Deal Desk",
            goal="Remove friction from enterprise deals by instantly providing custom compliance architectures and legal intent documents.",
            capabilities=["security_questionnaires", "soc2_generation", "loi_drafting"]
        )

    async def generate_soc2_summary(self, startup_context: Dict[str, Any], target_company: str) -> Dict[str, Any]:
        """
        Dynamically generates a custom SOC2 Type II Executive Summary tailored
        to the specific objections or industry of the target company.
        """
        logger.info("Trust Architect: Generating SOC2 Summary", target=target_company)
        llm = self.get_llm("deepseek-chat")
        
        prompt = f"""Generate a polished, enterprise-grade SOC 2 Type II Executive Summary letter.
        
OUR STARTUP:
- Name: {startup_context.get('name', 'Our Company')}
- Architecture: {startup_context.get('description', 'Cloud-native SaaS')}

TARGET ENTERPRISE:
- Company: {target_company}

REQUIREMENTS:
1. Format as an official executive summary letter (markdown).
2. Detail our commitment to the Trust Services Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy).
3. Mention continuous monitoring, penetration testing, and AWS/GCP underlying infrastructure compliance.
4. Tone: Extremely professional, authoritative, zero fluff. Write it like an auditor's cover letter.
5. Tailor the emphasis subtly towards enterprise risk mitigation for a company like {target_company}.
"""
        try:
            response = await llm.ainvoke(prompt)
            return {
                "success": True,
                "document_type": "SOC2 Executive Summary",
                "markdown": response.content.strip(),
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("SOC2 summary generation failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def answer_security_questionnaire(
        self, 
        startup_context: Dict[str, Any], 
        questions: List[str]
    ) -> Dict[str, Any]:
        """
        Answers a list of security questions to unblock a procurement cycle.
        """
        logger.info("Trust Architect: Answering Security Questionnaire", question_count=len(questions))
        llm = self.get_llm()
        
        formatted_questions = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
        
        prompt = f"""You are the CISO for {startup_context.get('name', 'Our Company')} ({startup_context.get('description', 'SaaS')}).
We are filling out an enterprise security questionnaire to unblock a major deal.

Please answer the following questions clearly, confidently, and concisely. 
Assume we use standard modern secure infrastructure (AWS/GCP, TLS 1.3, AES-256 at rest, Role-Based Access Control, MFA enforced, automated vulnerability scanning).

QUESTIONS:
{formatted_questions}

Format the output strictly as a JSON array of objects, with keys: "question" and "answer". Do NOT wrap in markdown code blocks.
"""
        import json
        try:
            response = await llm.ainvoke(prompt)
            raw_content = response.content.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:-3]
            elif raw_content.startswith("```"):
                raw_content = raw_content[3:-3]
                
            answers = json.loads(raw_content)
            
            return {
                "success": True,
                "document_type": "Security Questionnaire",
                "answers": answers,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Security questionnaire generation failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def draft_loi(
        self, 
        startup_context: Dict[str, Any], 
        deal_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Drafts a custom Letter of Intent (LOI) or Enterprise Agreement summary.
        """
        logger.info("Trust Architect: Drafting LOI", target=deal_terms.get('target_company', 'Unknown'))
        llm = self.get_llm()
        
        prompt = f"""Draft a formal Letter of Intent (LOI) for an enterprise SaaS deployment.

PROVIDER:
{startup_context.get('name', 'Our Company')} - {startup_context.get('industry', 'Technology')}

CLIENT (TARGET):
{deal_terms.get('target_company', '[Client Company]')}

DEAL TERMS:
- Scope: {deal_terms.get('scope', 'Enterprise License for core platform')}
- Pricing: {deal_terms.get('pricing', 'TBD')}
- Timeline: {deal_terms.get('timeline', '90-day implementation')}
- Special Conditions: {deal_terms.get('special_conditions', 'Standard SLA applies')}

REQUIREMENTS:
1. Write a professional, non-binding LOI that outlines the proposed partnership.
2. Include sections for: Purpose, Proposed Transaction, Timing, Confidentiality, Non-Binding Nature, and Signatures.
3. Use formal legal/business language.
4. Output in clean Markdown.
"""
        try:
            response = await llm.ainvoke(prompt)
            return {
                "success": True,
                "document_type": "Letter of Intent (LOI)",
                "markdown": response.content.strip(),
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("LOI draft failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def process(self, message: str, startup_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Standard interaction loop via message bus or API"""
        llm = self.get_llm()
        
        router_prompt = f"""Given this request to the Trust Architect (Head of Security & Deal Desk), identify the core task.
        Request: "{message}"
        
        Return ONLY ONE of these task categories:
        - SOC2
        - QUESTIONNAIRE
        - LOI
        - OTHER
        """
        intent = (await llm.ainvoke(router_prompt)).content.strip().upper()
        
        if "SOC2" in intent:
            return await self.generate_soc2_summary(startup_context, "Target Enterprise")
            
        elif "LOI" in intent:
            return await self.draft_loi(startup_context, {"target_company": "Enterprise Client", "scope": "Based on recent conversations"})
            
        # Default response
        return {
            "success": True,
            "response": "I am the Trust Architect. I can generate SOC2 executive summaries, answer security questionnaires, and draft LOIs. How can I unblock your deal today?",
            "agent": self.name
        }

trust_architect = TrustArchitectAgent()
