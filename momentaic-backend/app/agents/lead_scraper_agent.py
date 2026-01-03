"""
Lead Scraper Agent
Autonomous agent for finding B2B leads from various sources
Part of "The Hunter" Swarm
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import asyncio
import re

from app.agents.base import get_llm, get_agent_config, web_search
from app.models.conversation import AgentType

logger = structlog.get_logger()


class LeadScraperAgent:
    """
    Lead Scraper Agent - Discovers B2B leads from multiple sources
    
    Sources:
    - Google Maps (local businesses)
    - LinkedIn (company pages)
    - Web directories (industry-specific)
    
    Use Cases:
    - Find nursing homes in a specific region
    - Find cram schools (Juku) in Tokyo
    - Find HR managers at target companies
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.SALES_HUNTER)
        self.llm = get_llm("gemini-2.5-pro", temperature=0.3)
    
    async def scrape_google_maps(
        self,
        business_type: str,
        location: str,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Scrape businesses from Google Maps (via web search proxy)
        
        Args:
            business_type: e.g., "nursing homes", "cram schools", "juku"
            location: e.g., "Shibuya Tokyo", "Kanto region"
            limit: Maximum number of leads to return
        """
        logger.info(
            "Lead Scraper: Searching Google Maps",
            business_type=business_type,
            location=location,
        )
        
        try:
            # Use web search to find businesses
            search_query = f"{business_type} in {location} site:google.com/maps OR site:yelp.com"
            search_results = web_search.invoke(search_query)
            
            # Use LLM to extract business information
            if not self.llm:
                return {
                    "success": False,
                    "error": "AI Service Unavailable",
                    "leads": [],
                }
            
            prompt = f"""Extract business leads from these search results.

Search Query: {business_type} in {location}

Search Results:
{search_results}

For each business found, extract:
1. Business Name
2. Address (if available)
3. Phone Number (if available)
4. Website (if available)
5. Category/Type

Format each lead as:
NAME: [name]
ADDRESS: [address]
PHONE: [phone]
WEBSITE: [url]
CATEGORY: [category]
---

List up to {limit} leads."""

            response = await self.llm.ainvoke(prompt)
            leads = self._parse_leads(response.content)
            
            return {
                "success": True,
                "source": "google_maps",
                "query": f"{business_type} in {location}",
                "leads": leads[:limit],
                "total_found": len(leads),
                "scraped_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error("Lead scraping failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "leads": [],
            }
    
    async def scrape_linkedin(
        self,
        job_title: str,
        company_type: str,
        location: str,
        limit: int = 30,
    ) -> Dict[str, Any]:
        """
        Find people on LinkedIn by job title and company type
        
        Args:
            job_title: e.g., "HR Manager", "School Director"
            company_type: e.g., "nursing home", "education"
            location: e.g., "Tokyo, Japan"
        """
        logger.info(
            "Lead Scraper: Searching LinkedIn",
            job_title=job_title,
            company_type=company_type,
        )
        
        try:
            # LinkedIn search via web search proxy
            search_query = f'site:linkedin.com/in "{job_title}" "{company_type}" {location}'
            search_results = web_search.invoke(search_query)
            
            if not self.llm:
                return {
                    "success": False,
                    "error": "AI Service Unavailable",
                    "leads": [],
                }
            
            prompt = f"""Extract LinkedIn profiles from these search results.

Search Query: {job_title} at {company_type} companies in {location}

Search Results:
{search_results}

For each person found, extract:
1. Full Name
2. Job Title
3. Company Name
4. LinkedIn URL (if available)
5. Location

Format each lead as:
NAME: [name]
TITLE: [title]
COMPANY: [company]
LINKEDIN: [url]
LOCATION: [location]
---

List up to {limit} leads."""

            response = await self.llm.ainvoke(prompt)
            leads = self._parse_linkedin_leads(response.content)
            
            return {
                "success": True,
                "source": "linkedin",
                "query": f"{job_title} at {company_type}",
                "leads": leads[:limit],
                "total_found": len(leads),
                "scraped_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error("LinkedIn scraping failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "leads": [],
            }
    
    async def find_juku_leads(
        self,
        region: str = "Tokyo",
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Specialized method for finding Juku (cram school) leads in Japan
        """
        return await self.scrape_google_maps(
            business_type="学習塾 cram school juku",
            location=region,
            limit=limit,
        )
    
    async def find_nursing_home_leads(
        self,
        region: str = "Kanto",
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Specialized method for finding nursing home leads
        """
        return await self.scrape_google_maps(
            business_type="介護施設 nursing home elderly care",
            location=region,
            limit=limit,
        )
    
    async def bulk_scrape(
        self,
        targets: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Run multiple scraping jobs in parallel
        
        Args:
            targets: List of {"type": "google_maps"|"linkedin", ...params}
        """
        results = []
        
        for target in targets:
            target_type = target.get("type", "google_maps")
            
            if target_type == "google_maps":
                result = await self.scrape_google_maps(
                    business_type=target.get("business_type", ""),
                    location=target.get("location", ""),
                    limit=target.get("limit", 30),
                )
            elif target_type == "linkedin":
                result = await self.scrape_linkedin(
                    job_title=target.get("job_title", ""),
                    company_type=target.get("company_type", ""),
                    location=target.get("location", ""),
                    limit=target.get("limit", 20),
                )
            else:
                result = {"success": False, "error": f"Unknown type: {target_type}"}
            
            results.append(result)
        
        all_leads = []
        for r in results:
            if r.get("success"):
                all_leads.extend(r.get("leads", []))
        
        return {
            "success": True,
            "total_leads": len(all_leads),
            "leads": all_leads,
            "job_results": results,
        }
    
    def _parse_leads(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response into structured leads"""
        leads = []
        current_lead = {}
        
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("NAME:"):
                if current_lead:
                    leads.append(current_lead)
                current_lead = {"name": line.replace("NAME:", "").strip()}
            elif line.startswith("ADDRESS:"):
                current_lead["address"] = line.replace("ADDRESS:", "").strip()
            elif line.startswith("PHONE:"):
                current_lead["phone"] = line.replace("PHONE:", "").strip()
            elif line.startswith("WEBSITE:"):
                current_lead["website"] = line.replace("WEBSITE:", "").strip()
            elif line.startswith("CATEGORY:"):
                current_lead["category"] = line.replace("CATEGORY:", "").strip()
            elif line == "---" and current_lead:
                leads.append(current_lead)
                current_lead = {}
        
        if current_lead:
            leads.append(current_lead)
        
        return leads
    
    def _parse_linkedin_leads(self, response: str) -> List[Dict[str, str]]:
        """Parse LinkedIn leads from LLM response"""
        leads = []
        current_lead = {}
        
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("NAME:"):
                if current_lead:
                    leads.append(current_lead)
                current_lead = {"name": line.replace("NAME:", "").strip()}
            elif line.startswith("TITLE:"):
                current_lead["title"] = line.replace("TITLE:", "").strip()
            elif line.startswith("COMPANY:"):
                current_lead["company"] = line.replace("COMPANY:", "").strip()
            elif line.startswith("LINKEDIN:"):
                current_lead["linkedin_url"] = line.replace("LINKEDIN:", "").strip()
            elif line.startswith("LOCATION:"):
                current_lead["location"] = line.replace("LOCATION:", "").strip()
            elif line == "---" and current_lead:
                leads.append(current_lead)
                current_lead = {}
        
        if current_lead:
            leads.append(current_lead)
        
        return leads


# Singleton instance
lead_scraper_agent = LeadScraperAgent()
