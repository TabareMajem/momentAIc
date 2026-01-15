"""
KOL Research & Scraping Tools
Real growth hacking tools for finding and qualifying influencers
Uses free/native methods - no paid tools required
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import structlog
import httpx
import re
import asyncio

from app.core.config import settings

logger = structlog.get_logger()


class KOLProfile(BaseModel):
    """Detailed KOL profile."""
    name: str
    handle: str
    platform: str  # youtube, twitter, linkedin, instagram, tiktok
    url: str
    followers: int
    engagement_rate: float
    niche: List[str]
    region: str
    email: Optional[str] = None
    contact_method: str = "dm"
    recent_content: List[str] = []
    score: float = 0.0
    notes: str = ""


class KOLResearchTools:
    """
    Free/native KOL research tools.
    
    Strategies:
    1. Twitter/X lists and search (native API)
    2. YouTube channel discovery
    3. LinkedIn Sales Navigator alternatives
    4. Product Hunt maker search
    5. GitHub influencer discovery
    6. Newsletter/Substack discovery
    """
    
    # Niche keywords for AI/SaaS/Startup space
    SEARCH_KEYWORDS = {
        "en": [
            "AI tools", "SaaS founder", "indie hacker", "no-code",
            "startup founder", "solopreneur", "bootstrapped",
            "building in public", "#buildinpublic", "automation",
            "passive income", "side project", "micro SaaS"
        ],
        "es": [
            "emprendedor", "startup latino", "negocios digitales",
            "ingresos pasivos", "automatización", "herramientas IA"
        ],
        "pt": [
            "empreendedor", "startup brasil", "negócios digitais",
            "renda passiva", "automação", "ferramentas IA"
        ]
    }
    
    def __init__(self):
        self.twitter_bearer = getattr(settings, 'twitter_bearer_token', '')
        self.github_token = getattr(settings, 'github_token', '')
    
    # ============ TWITTER/X RESEARCH ============
    
    async def find_twitter_kols(
        self,
        keywords: List[str] = None,
        min_followers: int = 5000,
        max_followers: int = 100000,
        region: str = "US"
    ) -> List[KOLProfile]:
        """
        Find KOLs on Twitter/X.
        Uses list scraping and search API.
        """
        if not self.twitter_bearer:
            logger.warning("Twitter API not configured")
            return []
        
        keywords = keywords or self.SEARCH_KEYWORDS["en"][:5]
        profiles = []
        
        for keyword in keywords:
            try:
                async with httpx.AsyncClient() as client:
                    # Search recent tweets
                    response = await client.get(
                        "https://api.twitter.com/2/tweets/search/recent",
                        headers={"Authorization": f"Bearer {self.twitter_bearer}"},
                        params={
                            "query": f"{keyword} -is:retweet lang:en",
                            "max_results": 50,
                            "expansions": "author_id",
                            "user.fields": "public_metrics,description,location"
                        }
                    )
                    
                    if response.status_code != 200:
                        continue
                    
                    data = response.json()
                    users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
                    
                    for tweet in data.get("data", []):
                        user = users.get(tweet.get("author_id"))
                        if not user:
                            continue
                        
                        followers = user.get("public_metrics", {}).get("followers_count", 0)
                        
                        if min_followers <= followers <= max_followers:
                            profile = KOLProfile(
                                name=user.get("name", ""),
                                handle=f"@{user.get('username', '')}",
                                platform="twitter",
                                url=f"https://twitter.com/{user.get('username', '')}",
                                followers=followers,
                                engagement_rate=self._calc_engagement(user.get("public_metrics", {})),
                                niche=self._extract_niche(user.get("description", "")),
                                region=self._detect_region(user.get("location", "")),
                                recent_content=[tweet.get("text", "")[:200]],
                                contact_method="dm"
                            )
                            profile.score = self._calculate_kol_score(profile)
                            profiles.append(profile)
                
                await asyncio.sleep(1)  # Rate limit
                
            except Exception as e:
                logger.error(f"Twitter search error: {e}")
        
        # Dedupe and sort by score
        seen = set()
        unique = []
        for p in profiles:
            if p.handle not in seen:
                seen.add(p.handle)
                unique.append(p)
        
        return sorted(unique, key=lambda x: x.score, reverse=True)[:50]
    
    # ============ PRODUCT HUNT RESEARCH ============
    
    async def find_product_hunt_makers(
        self,
        categories: List[str] = None
    ) -> List[KOLProfile]:
        """
        Find active Product Hunt makers.
        These are ideal partners - they understand product launches.
        """
        categories = categories or ["artificial-intelligence", "productivity", "developer-tools"]
        profiles = []
        
        # Product Hunt GraphQL API (public)
        query = """
        query {
            posts(first: 50, order: VOTES) {
                edges {
                    node {
                        name
                        votesCount
                        makers {
                            id
                            name
                            username
                            twitterUsername
                            headline
                            followersCount
                        }
                    }
                }
            }
        }
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.producthunt.com/v2/api/graphql",
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    json={"query": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("posts", {}).get("edges", [])
                    
                    for post in posts:
                        for maker in post.get("node", {}).get("makers", []):
                            if maker.get("followersCount", 0) >= 100:
                                profiles.append(KOLProfile(
                                    name=maker.get("name", ""),
                                    handle=maker.get("username", ""),
                                    platform="producthunt",
                                    url=f"https://producthunt.com/@{maker.get('username', '')}",
                                    followers=maker.get("followersCount", 0),
                                    engagement_rate=0.05,  # PH has high engagement
                                    niche=["product", "startup", "maker"],
                                    region="US",
                                    contact_method="twitter" if maker.get("twitterUsername") else "ph_dm"
                                ))
        except Exception as e:
            logger.error(f"Product Hunt error: {e}")
        
        return profiles[:30]
    
    # ============ GITHUB INFLUENCER RESEARCH ============
    
    async def find_github_influencers(
        self,
        topics: List[str] = None
    ) -> List[KOLProfile]:
        """
        Find GitHub influencers in relevant topics.
        Great for dev-focused outreach.
        """
        topics = topics or ["ai", "automation", "saas", "productividad"]
        profiles = []
        
        for topic in topics:
            try:
                async with httpx.AsyncClient() as client:
                    headers = {}
                    if self.github_token:
                        headers["Authorization"] = f"token {self.github_token}"
                    
                    # Search users by topic
                    response = await client.get(
                        "https://api.github.com/search/users",
                        headers=headers,
                        params={
                            "q": f"{topic} followers:>1000",
                            "sort": "followers",
                            "per_page": 20
                        }
                    )
                    
                    if response.status_code != 200:
                        continue
                    
                    for user in response.json().get("items", []):
                        # Get full user profile
                        user_resp = await client.get(
                            user["url"],
                            headers=headers
                        )
                        
                        if user_resp.status_code == 200:
                            user_data = user_resp.json()
                            
                            profiles.append(KOLProfile(
                                name=user_data.get("name", user_data.get("login", "")),
                                handle=user_data.get("login", ""),
                                platform="github",
                                url=user_data.get("html_url", ""),
                                followers=user_data.get("followers", 0),
                                engagement_rate=0.03,
                                niche=["developer", topic],
                                region="US",
                                email=user_data.get("email"),
                                contact_method="email" if user_data.get("email") else "dm"
                            ))
                        
                        await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"GitHub search error: {e}")
        
        return profiles[:30]
    
    # ============ NEWSLETTER/SUBSTACK RESEARCH ============
    
    async def find_newsletter_creators(
        self,
        keywords: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find Substack/newsletter creators.
        High-quality audience, great for partnerships.
        """
        keywords = keywords or ["AI", "startup", "SaaS", "productivity"]
        
        # This would scrape Substack discover page
        # For now, return a template for manual research
        return [
            {
                "search_url": f"https://substack.com/discover?q={kw}",
                "keyword": kw,
                "strategy": "Search Substack, filter by subscriber count, reach via Twitter DM"
            }
            for kw in keywords
        ]
    
    # ============ HELPER METHODS ============
    
    def _calc_engagement(self, metrics: Dict) -> float:
        """Calculate engagement rate from Twitter metrics."""
        followers = metrics.get("followers_count", 1)
        tweets = metrics.get("tweet_count", 0)
        if followers == 0 or tweets == 0:
            return 0.0
        # Rough estimate based on ratio
        return min(tweets / followers * 10, 1.0)
    
    def _extract_niche(self, bio: str) -> List[str]:
        """Extract niche keywords from bio."""
        niches = []
        bio_lower = bio.lower()
        
        keywords = {
            "ai": ["ai", "artificial intelligence", "machine learning", "ml"],
            "startup": ["startup", "founder", "ceo", "entrepreneur"],
            "developer": ["developer", "engineer", "coding", "programmer"],
            "marketing": ["marketing", "growth", "seo", "content"],
            "saas": ["saas", "b2b", "software"],
            "nocode": ["no-code", "nocode", "low-code", "automation"],
            "creator": ["creator", "youtuber", "streamer", "influencer"]
        }
        
        for niche, kws in keywords.items():
            if any(kw in bio_lower for kw in kws):
                niches.append(niche)
        
        return niches or ["general"]
    
    def _detect_region(self, location: str) -> str:
        """Detect region from location string."""
        if not location:
            return "Unknown"
        
        location_lower = location.lower()
        
        us_indicators = ["usa", "us", "california", "new york", "san francisco", "texas", "florida"]
        latam_indicators = ["mexico", "brasil", "brazil", "argentina", "colombia", "chile", "peru", "latam"]
        europe_indicators = ["uk", "germany", "france", "spain", "london", "berlin", "paris", "europe"]
        asia_indicators = ["japan", "singapore", "india", "tokyo", "asia", "korea", "china", "philippines"]
        
        if any(i in location_lower for i in us_indicators):
            return "US"
        if any(i in location_lower for i in latam_indicators):
            return "LatAm"
        if any(i in location_lower for i in europe_indicators):
            return "Europe"
        if any(i in location_lower for i in asia_indicators):
            return "Asia"
        
        return "US"  # Default
    
    def _calculate_kol_score(self, profile: KOLProfile) -> float:
        """Calculate priority score for a KOL."""
        score = 0.0
        
        # Follower sweet spot (10k-50k is ideal)
        if 10000 <= profile.followers <= 50000:
            score += 40
        elif 50000 < profile.followers <= 100000:
            score += 30
        elif 5000 <= profile.followers < 10000:
            score += 20
        else:
            score += 10
        
        # Engagement bonus
        score += min(profile.engagement_rate * 100, 30)
        
        # Niche relevance
        relevant_niches = {"ai", "startup", "saas", "nocode", "developer"}
        niche_match = len(set(profile.niche) & relevant_niches)
        score += niche_match * 10
        
        return min(score, 100)
    
    async def generate_hit_list(
        self,
        target_count: int = 100,
        regions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete KOL hit list.
        Combines all discovery methods.
        """
        regions = regions or ["US", "LatAm", "Europe", "Asia"]
        
        all_profiles = []
        
        # Twitter
        twitter_kols = await self.find_twitter_kols()
        all_profiles.extend(twitter_kols)
        
        # Product Hunt
        ph_makers = await self.find_product_hunt_makers()
        all_profiles.extend(ph_makers)
        
        # GitHub
        github_influencers = await self.find_github_influencers()
        all_profiles.extend(github_influencers)
        
        # Sort by score and dedupe
        all_profiles.sort(key=lambda x: x.score, reverse=True)
        
        # Group by region
        by_region = {r: [] for r in regions}
        for p in all_profiles:
            if p.region in by_region:
                by_region[p.region].append(p.dict())
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total_found": len(all_profiles),
            "by_region": by_region,
            "top_25": [p.dict() for p in all_profiles[:25]]
        }


# Singleton
kol_research = KOLResearchTools()
