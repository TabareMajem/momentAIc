"""
KOL Headhunter Agent
Identifies high-leverage influencers for partnership using Serper API for real search.

Architecture: 
  1. scan_region() does the actual Serper API searches programmatically (no LLM needed for search)
  2. The LLM is used only for ANALYSIS: scoring relevance, generating outreach scripts
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

class KOLProfile(BaseModel):
    """Represents a Key Opinion Leader profile."""
    name: str = ""
    platform: str = ""
    handle: str = ""
    followers: int = 0
    engagement_rate: float = 0.0
    region: str = ""
    niche: List[str] = Field(default_factory=list)
    last_posts: List[str] = Field(default_factory=list)
    outreach_script: str = ""
    priority_score: float = 0.0
    profile_url: str = ""
    source: str = ""


class HitList(BaseModel):
    """Prioritized list of KOL targets."""
    region: str = ""
    total_found: int = 0
    targets: List[KOLProfile] = Field(default_factory=list)
    generated_at: str = ""
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


# ==================
# Serper API Helper
# ==================

async def _serper_search(query: str, num: int = 10) -> List[Dict]:
    """
    Execute a Google search via the Serper API.
    Returns a list of dicts with keys: title, link, snippet.
    """
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


async def _search_platform(keyword: str, platform: str, region: str) -> List[Dict]:
    """Search a specific platform for a keyword using Serper API."""
    
    site_filters = {
        "youtube": "site:youtube.com",
        "twitter": "site:twitter.com OR site:x.com",
        "linkedin": "site:linkedin.com/in/",
    }
    
    site_filter = site_filters.get(platform, "")
    query = f"{site_filter} {keyword} {region}"
    
    results = await _serper_search(query, num=10)
    
    creators = []
    for r in results:
        title = r.get("title", "")
        link = r.get("link", "")
        snippet = r.get("snippet", "")
        
        # Platform-specific filtering
        if platform == "youtube" and "/watch" in link:
            continue  # Skip individual videos
        if platform == "twitter" and "/status/" in link:
            continue  # Skip individual tweets
        
        # Clean up titles
        title = title.replace(" - YouTube", "").replace(" on X", "").replace(" | Twitter", "")
        
        creators.append({
            "name": title.split("|")[0].split("-")[0].strip()[:60],
            "platform": platform.capitalize(),
            "link": link,
            "snippet": snippet[:200],
            "keyword_matched": keyword,
        })
    
    return creators


# ==================
# KOL Headhunter Agent
# ==================

class KOLHeadhunterAgent:
    """
    KOL Headhunter Agent - Identifies high-leverage influencers for partnership.
    
    Uses a two-phase approach:
    Phase 1: Programmatic search via Serper API (fast, reliable)
    Phase 2: LLM analysis to score, deduplicate, and draft outreach
    """
    
    # Target profile parameters
    FOLLOWER_RANGE = (10000, 100000)
    MIN_ENGAGEMENT_RATE = 0.03
    SEARCH_KEYWORDS = [
        "indie maker", "bootstrapped founder", "no-code entrepreneur",
        "solopreneur", "AI tools review", "startup without funding"
    ]
    PLATFORMS = ["youtube", "twitter", "linkedin"]
    
    def __init__(self):
        self.name = "KOL Headhunter"
        self.description = "Identifies high-leverage influencers for partnership"
    
    async def _gather_raw_results(
        self, 
        keywords: List[str], 
        region: str
    ) -> List[Dict]:
        """
        Phase 1: Search all platforms for all keywords concurrently.
        Returns a deduplicated list of raw search results.
        """
        tasks = []
        for keyword in keywords:
            for platform in self.PLATFORMS:
                tasks.append(_search_platform(keyword, platform, region))
        
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten and deduplicate by URL
        seen_urls = set()
        unique_results = []
        for batch in all_results:
            if isinstance(batch, Exception):
                logger.warning("Search task failed", error=str(batch))
                continue
            for item in batch:
                url = item.get("link", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(item)
        
        logger.info(
            f"Phase 1 complete: {len(unique_results)} unique results "
            f"from {len(tasks)} searches across {len(keywords)} keywords × {len(self.PLATFORMS)} platforms"
        )
        return unique_results
    
    async def _analyze_with_llm(
        self,
        raw_results: List[Dict],
        region: str,
        keywords: List[str],
        max_targets: int
    ) -> List[KOLProfile]:
        """
        Phase 2: Use LLM to analyze and score raw search results.
        Returns structured KOLProfile objects.
        """
        from app.agents.base import get_llm
        
        llm = get_llm("gpt-4o", temperature=0.3)
        
        # Format results for the LLM
        results_text = json.dumps(raw_results[:80], indent=2)  # Cap input to avoid token limits
        
        prompt = f"""You are an elite KOL Headhunter for MomentAIc, an AI Operating System for bootstrap founders.

I searched Google for people critical of Y Combinator and VC funding. Below are the raw search results.

Your job:
1. Identify REAL people/creators from these results
2. Estimate their follower count (use context clues from snippets)
3. Score their relevance to our "anti-YC/VC" campaign (0-100)
4. Draft a brief, personalized outreach message for each

Target profile: Independent creators, 10k-100k followers, critical of traditional VC/accelerator models.

Region: {region}
Keywords used: {', '.join(keywords)}

RAW SEARCH RESULTS:
{results_text}

OUTPUT RULES:
- Return a JSON array of the top {max_targets} most relevant targets
- Each object MUST have these exact fields:
  "name", "platform", "handle", "followers" (integer estimate), 
  "engagement_rate" (float estimate), "niche" (array of strings),
  "last_posts" (array of topic strings from snippets), 
  "outreach_script" (personalized message string),
  "priority_score" (float 0-100), "profile_url" (string)
- Output ONLY the JSON array, no other text
- If fewer than {max_targets} quality targets exist, return fewer

JSON:"""
        
        try:
            response = await llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            json_match = re.search(r'\[\s*\{.*?\}\s*\]', content, re.DOTALL)
            if json_match:
                raw_targets = json.loads(json_match.group())
                targets = []
                for t in raw_targets:
                    targets.append(KOLProfile(
                        name=str(t.get("name", "Unknown")),
                        platform=str(t.get("platform", "Unknown")),
                        handle=str(t.get("handle", "")),
                        followers=int(t.get("followers", 0)),
                        engagement_rate=float(t.get("engagement_rate", 0.0)),
                        region=region,
                        niche=t.get("niche", []),
                        last_posts=t.get("last_posts", []),
                        outreach_script=str(t.get("outreach_script", "")),
                        priority_score=float(t.get("priority_score", 0.0)),
                        profile_url=str(t.get("profile_url", "")),
                        source="Serper API + GPT-4o"
                    ))
                logger.info(f"Phase 2 complete: LLM identified {len(targets)} targets")
                return targets
            else:
                logger.warning("LLM did not return valid JSON array")
                return []
                
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return []
    
    async def scan_region(
        self,
        region: str,
        max_targets: int = 50,
        custom_keywords: List[str] = None
    ) -> HitList:
        """
        Scan a region for KOL targets using a two-phase approach.
        
        Phase 1: Programmatic Serper API search (fast, concurrent)
        Phase 2: LLM analysis for scoring and outreach generation
        """
        from datetime import datetime
        
        logger.info(f"KOL Headhunter scanning region: {region}")
        keywords_to_use = custom_keywords if custom_keywords else self.SEARCH_KEYWORDS
        
        # Phase 1: Gather raw search results
        print(f"[Phase 1] Searching {len(keywords_to_use)} keywords × {len(self.PLATFORMS)} platforms...")
        raw_results = await self._gather_raw_results(keywords_to_use, region)
        print(f"[Phase 1] Found {len(raw_results)} unique results across all searches")
        
        if not raw_results:
            logger.warning("No search results from Serper API. Check API key or network.")
            return HitList(
                region=region,
                total_found=0,
                targets=[],
                generated_at=datetime.utcnow().isoformat(),
                filters_applied={"keywords": keywords_to_use}
            )
        
        # Phase 2: LLM analysis
        print(f"[Phase 2] Analyzing {len(raw_results)} results with GPT-4o...")
        targets = await self._analyze_with_llm(raw_results, region, keywords_to_use, max_targets)
        print(f"[Phase 2] Identified {len(targets)} high-quality targets")
        
        return HitList(
            region=region,
            total_found=len(targets),
            targets=targets[:max_targets],
            generated_at=datetime.utcnow().isoformat(),
            filters_applied={
                "follower_range": self.FOLLOWER_RANGE,
                "min_engagement": self.MIN_ENGAGEMENT_RATE,
                "keywords": keywords_to_use
            }
        )
    
    async def scan_all_regions(self) -> Dict[str, HitList]:
        """Scan all target regions in parallel."""
        regions = ["US", "LatAm", "Europe", "Asia"]
        
        tasks = [self.scan_region(region) for region in regions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            region: result 
            for region, result in zip(regions, results)
            if not isinstance(result, Exception)
        }


# Singleton instance
kol_headhunter = KOLHeadhunterAgent()
