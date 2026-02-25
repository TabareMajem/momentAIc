"""
VC Headhunter Agent
Identifies Active Investors (VCs) for Deal Flow using Serper API.

Architecture: 
  1. Phase 1: Programmatic Serper API search (Twitter, LinkedIn, Substack, News)
  2. Phase 2: LLM analysis to score "Investor Fit" and draft "Cold Pitch"
"""

from typing import Dict, Any, Optional, List
import asyncio
import json
import re
import structlog
import httpx

from pydantic import BaseModel, Field
from app.core.config import settings

logger = structlog.get_logger()


# ==================
# Models
# ==================

class VCProfile(BaseModel):
    """Represents a Venture Capitalist profile."""
    name: str = ""
    firm: str = ""
    role: str = ""  # Partner, Principal, Angel
    platform: str = ""
    handle: str = ""
    focus_area: List[str] = Field(default_factory=list)  # AI, SaaS, Creator Economy
    recent_investments: List[str] = Field(default_factory=list)
    thesis_match: str = ""  # Why they fit (e.g. "Invests in AI Agents")
    cold_pitch: str = ""
    priority_score: float = 0.0
    profile_url: str = ""
    source: str = ""


class DealFlowList(BaseModel):
    """Prioritized list of VC targets."""
    region: str = ""
    total_found: int = 0
    targets: List[VCProfile] = Field(default_factory=list)
    generated_at: str = ""
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


# ==================
# Serper API Helper
# ==================

async def _serper_search(query: str, num: int = 10) -> List[Dict]:
    """Execute a Google search via the Serper API."""
    if not settings.serper_api_key:
        logger.warning("Serper API key not configured")
        return []
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": num},
                headers={"X-API-KEY": settings.serper_api_key},
            )
            data = response.json()
            results = []
            for item in data.get("organic", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })
            return results
    except Exception as e:
        logger.error("Serper search failed", error=str(e))
        return []


async def _search_platform(keyword: str, platform: str) -> List[Dict]:
    """Search a specific platform for a keyword using Serper API."""
    
    site_filters = {
        "twitter": "site:twitter.com OR site:x.com",
        "linkedin": "site:linkedin.com/in/",
        "substack": "site:substack.com",
        "news": "site:techcrunch.com OR site:venturebeat.com"
    }
    
    site_filter = site_filters.get(platform, "")
    query = f"{site_filter} {keyword}"
    
    results = await _serper_search(query, num=10)
    
    investors = []
    for r in results:
        title = r.get("title", "")
        link = r.get("link", "")
        snippet = r.get("snippet", "")
        
        # Cleanup titles
        title = title.replace(" on X", "").replace(" | LinkedIn", "").replace(" - Substack", "")
        
        investors.append({
            "name": title.split("|")[0].split("-")[0].strip()[:60],
            "platform": platform.capitalize(),
            "link": link,
            "snippet": snippet[:250],
            "keyword_matched": keyword,
        })
    
    return investors


# ==================
# VC Headhunter Agent
# ==================

class VCHeadhunterAgent:
    """
    VC Headhunter Agent - Identifies investors for MomentAIc.
    """
    
    SEARCH_KEYWORDS = [
        "active AI investors 2025",
        "seed vc generative ai agents",
        "investing in bootstrap founder tools",
        "vc thesis creator economy 2025",
        "partners seeking ai deal flow"
    ]
    PLATFORMS = ["twitter", "linkedin", "substack"]
    
    def __init__(self):
        self.name = "VC Headhunter"
        self.description = "Identifies investors for deal flow"
    
    async def _gather_raw_results(self, keywords: List[str]) -> List[Dict]:
        """Phase 1: Search all platforms for investors."""
        tasks = []
        for keyword in keywords:
            for platform in self.PLATFORMS:
                tasks.append(_search_platform(keyword, platform))
        
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten and deduplicate
        seen_urls = set()
        unique_results = []
        for batch in all_results:
            if isinstance(batch, Exception):
                continue
            for item in batch:
                url = item.get("link", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(item)
        
        logger.info(f"Phase 1 complete: {len(unique_results)} raw investor profiles found")
        return unique_results
    
    async def _analyze_with_llm(
        self,
        raw_results: List[Dict],
        keywords: List[str],
        max_targets: int
    ) -> List[VCProfile]:
        """Phase 2: LLM analysis to identify REAL investors and draft pitches."""
        from app.agents.base import get_llm
        
        llm = get_llm("gpt-4o", temperature=0.3)
        
        # Cap input
        results_text = json.dumps(raw_results[:80], indent=2)
        
        prompt = f"""You are an expert Fundraising Consultant for MomentAIc (AI Operating System for Bootstrap Founders).

Your goal: Identify ACTIVE INVESTORS (VCs/Angels) from search results who would be interested in a high-traction, capital-efficient AI startup.
MomentAIc is an "Anti-YC" play: We help founders scale without employees.

Analyze these search results:
{results_text}

Task:
1. Identify REAL investors (Partners, Angels) - filter out newsletters or generic articles.
2. Determine their "Focus Area" (e.g. AI, Future of Work).
3. Draft a hyper-personalized "Cold Pitch" (Twitter DM or Email).
   - Hook: Mention their specific thesis or recent post.
   - Value: "Building the AI OS for bootstrap founders. Profitable growth. Not looking for hand-holding, just strategic capital."
4. Score them 0-100 on fit.

OUTPUT: JSON Array of top {max_targets} investors.
Fields: "name", "firm", "role", "platform", "handle", "focus_area" (list), "thesis_match", "recent_investments" (from snippets), "cold_pitch", "priority_score", "profile_url".

JSON ONLY:"""
        
        try:
            response = await llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON
            json_match = re.search(r'\[\s*\{.*?\}\s*\]', content, re.DOTALL)
            if json_match:
                raw_targets = json.loads(json_match.group())
                targets = []
                for t in raw_targets:
                    # Robust handling for list fields
                    recent_inv = t.get("recent_investments", [])
                    if isinstance(recent_inv, str):
                        recent_inv = [x.strip() for x in recent_inv.split(",")]
                    
                    focus = t.get("focus_area", [])
                    if isinstance(focus, str):
                        focus = [x.strip() for x in focus.split(",")]

                    targets.append(VCProfile(
                        name=str(t.get("name", "Unknown")),
                        firm=str(t.get("firm", "Unknown")),
                        role=str(t.get("role", "Investor")),
                        platform=str(t.get("platform", "Unknown")),
                        handle=str(t.get("handle", "")),
                        focus_area=focus,
                        recent_investments=recent_inv,
                        thesis_match=str(t.get("thesis_match", "")),
                        cold_pitch=str(t.get("cold_pitch", "")),
                        priority_score=float(t.get("priority_score", 0.0)),
                        profile_url=str(t.get("profile_url", "")),
                        source="Serper API + GPT-4o"
                    ))
                return targets
            else:
                logger.warning("LLM did not return valid JSON array")
                return []
                
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return []
    
    async def scan_for_investors(
        self,
        max_targets: int = 50,
        custom_keywords: List[str] = None
    ) -> DealFlowList:
        """Scan for investors."""
        from datetime import datetime
        
        keywords_to_use = custom_keywords if custom_keywords else self.SEARCH_KEYWORDS
        
        print(f"[Phase 1] Searching {len(keywords_to_use)} keywords × {len(self.PLATFORMS)} platforms for INVESTORS...")
        raw_results = await self._gather_raw_results(keywords_to_use)
        
        if not raw_results:
            return DealFlowList(total_found=0)
        
        print(f"[Phase 2] Analyzing {len(raw_results)} results for DEAL FLOW...")
        targets = await self._analyze_with_llm(raw_results, keywords_to_use, max_targets)
        print(f"[Phase 2] Identified {len(targets)} high-fit Investors")
        
        return DealFlowList(
            region="Global",
            total_found=len(targets),
            targets=targets,
            generated_at=datetime.utcnow().isoformat(),
            filters_applied={"keywords": keywords_to_use}
        )

# Instance
vc_headhunter = VCHeadhunterAgent()
