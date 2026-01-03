"""
Lead Researcher Agent
Deep research agent for analyzing leads and finding pain points
Part of "The Hunter" Swarm
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.agents.base import get_llm, get_agent_config, web_search, company_research
from app.models.conversation import AgentType

logger = structlog.get_logger()


class LeadResearcherAgent:
    """
    Lead Researcher Agent - Deep analysis of leads for personalized outreach
    
    Capabilities:
    - Website analysis (pain points, technology stack)
    - News monitoring (recent events, press releases)
    - Competitive analysis
    - Decision maker identification
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.SALES_HUNTER)
        self.llm = get_llm("gemini-2.5-pro", temperature=0.4)
    
    async def research_company(
        self,
        company_name: str,
        company_website: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Deep research on a company to find pain points and opportunities
        """
        logger.info("Lead Researcher: Analyzing company", company=company_name)
        
        try:
            # Gather information from multiple sources
            research_data = {
                "company_info": company_research.invoke(company_name),
                "recent_news": web_search.invoke(f"{company_name} news 2024"),
                "job_postings": web_search.invoke(f"{company_name} hiring jobs"),
                "reviews": web_search.invoke(f"{company_name} employee reviews glassdoor"),
            }
            
            if not self.llm:
                return {
                    "success": False,
                    "error": "AI Service Unavailable",
                    "company": company_name,
                }
            
            # Analyze with LLM
            prompt = f"""Analyze this company for B2B sales opportunities.

Company: {company_name}
Website: {company_website or "Unknown"}
Industry: {industry or "Unknown"}

Research Data:
{research_data}

Provide a detailed analysis:

1. COMPANY OVERVIEW
   - What do they do?
   - Company size and stage
   - Key products/services

2. PAIN POINTS (CRITICAL)
   - What challenges are they likely facing?
   - What problems can we solve for them?
   - Evidence from reviews, news, job postings

3. DECISION MAKERS
   - Who would buy our solution?
   - Titles to target

4. OUTREACH HOOKS
   - 3 personalized conversation starters
   - Reference recent news or specific pain points

5. COMPETITIVE INTELLIGENCE
   - Current solutions they might be using
   - Why we're better

Format each section clearly with bullet points."""

            response = await self.llm.ainvoke(prompt)
            
            # Parse the analysis
            analysis = self._parse_analysis(response.content)
            
            return {
                "success": True,
                "company": company_name,
                "website": company_website,
                "industry": industry,
                "analysis": analysis,
                "raw_research": research_data,
                "researched_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error("Company research failed", error=str(e), company=company_name)
            return {
                "success": False,
                "error": str(e),
                "company": company_name,
            }
    
    async def research_contact(
        self,
        contact_name: str,
        company_name: str,
        job_title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Research a specific contact for personalized outreach
        """
        logger.info(
            "Lead Researcher: Analyzing contact",
            contact=contact_name,
            company=company_name,
        )
        
        try:
            # Search for contact information
            search_results = web_search.invoke(
                f'"{contact_name}" "{company_name}" linkedin OR twitter OR blog'
            )
            
            if not self.llm:
                return {
                    "success": False,
                    "error": "AI Service Unavailable",
                }
            
            prompt = f"""Research this business contact for personalized outreach.

Contact: {contact_name}
Company: {company_name}
Title: {job_title or "Unknown"}

Search Results:
{search_results}

Extract:

1. PROFESSIONAL BACKGROUND
   - Current role and responsibilities
   - Career history
   - Education

2. INTERESTS & ACTIVITY
   - Recent posts or articles
   - Speaking engagements
   - Industry involvement

3. COMMUNICATION STYLE
   - Formal or casual based on content?
   - Topics they care about

4. PERSONALIZATION HOOKS
   - 3 specific conversation starters
   - Shared connections or interests
   - Recent achievements to congratulate

5. BEST CONTACT METHOD
   - LinkedIn, Email, or Twitter?
   - Recommended approach"""

            response = await self.llm.ainvoke(prompt)
            
            return {
                "success": True,
                "contact_name": contact_name,
                "company": company_name,
                "title": job_title,
                "profile": response.content,
                "researched_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error("Contact research failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
    
    async def batch_research(
        self,
        leads: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Research multiple leads in batch
        """
        results = []
        
        for lead in leads:
            if lead.get("company_name"):
                result = await self.research_company(
                    company_name=lead.get("company_name"),
                    company_website=lead.get("website"),
                    industry=lead.get("industry"),
                )
                results.append(result)
        
        successful = [r for r in results if r.get("success")]
        
        return {
            "success": True,
            "total_processed": len(results),
            "successful": len(successful),
            "results": results,
        }
    
    async def find_pain_points_for_product(
        self,
        leads: List[Dict[str, str]],
        product_description: str,
    ) -> Dict[str, Any]:
        """
        Analyze leads specifically for pain points our product solves
        """
        if not self.llm:
            return {"success": False, "error": "AI Service Unavailable"}
        
        # Aggregate lead information
        lead_summary = "\n".join([
            f"- {l.get('company_name', l.get('name', 'Unknown'))}: {l.get('industry', 'N/A')}"
            for l in leads[:20]  # Limit to 20
        ])
        
        prompt = f"""Analyze these potential customers for our product.

OUR PRODUCT:
{product_description}

POTENTIAL CUSTOMERS:
{lead_summary}

For each customer type, identify:

1. Their likely pain points that our product solves
2. The business impact of those pain points
3. How to position our product as the solution
4. Objections they might have
5. ROI messaging that would resonate

Group similar customers and provide segment-specific strategies."""

        response = await self.llm.ainvoke(prompt)
        
        return {
            "success": True,
            "analysis": response.content,
            "leads_analyzed": len(leads),
        }
    
    def _parse_analysis(self, response: str) -> Dict[str, str]:
        """Parse structured analysis from LLM response"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.split("\n"):
            line_stripped = line.strip()
            
            # Check for section headers
            if line_stripped.startswith("1. ") or line_stripped.startswith("2. ") or \
               line_stripped.startswith("3. ") or line_stripped.startswith("4. ") or \
               line_stripped.startswith("5. "):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content)
                
                current_section = line_stripped[3:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content)
        
        return sections


# Singleton instance
lead_researcher_agent = LeadResearcherAgent()
