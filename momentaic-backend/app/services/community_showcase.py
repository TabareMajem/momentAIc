"""
Community & Showcase Features
Agent-managed community with "Show, Not Tell" philosophy
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import structlog

logger = structlog.get_logger()


class ShowcaseType(str, Enum):
    """Types of showcases"""
    DEMO = "demo"              # Product demo video
    MILESTONE = "milestone"    # Achievement (10K users, etc.)
    LAUNCH = "launch"          # Product launch
    PIVOT = "pivot"            # Strategic pivot story
    FUNDING = "funding"        # Funding announcement
    GROWTH = "growth"          # Growth metrics showcase


@dataclass
class StartupShowcase:
    """Public startup showcase profile"""
    startup_id: str
    name: str
    tagline: str
    traction_score: float
    tier: str
    verified: bool
    
    # Public metrics (only what founder chooses)
    public_metrics: Dict[str, Any]
    
    # Showcase content
    showcases: List[Dict[str, Any]]
    
    # Social proof
    integrations_connected: int
    days_active: int
    
    # Rankings
    rank_overall: int
    rank_category: int
    category: str


class CommunityShowcaseService:
    """
    Community-managed showcase system
    
    Philosophy: "Show, Not Tell"
    - Let startups showcase REAL demos, metrics, milestones
    - AI agents curate and highlight best performers
    - No manual demo days - async, always-on showcases
    """
    
    def __init__(self):
        self._showcases: Dict[str, StartupShowcase] = {}
        self._seed_mock_data()
        
    def _seed_mock_data(self):
        """Seed with initial data for launch"""
        startups = [
            {
                "id": "startup-1", "name": "NeuralPay", "tagline": "AI-powered payments",
                "traction": 92, "metrics": {"mrr": 85000, "growth": 28, "users": 12500},
                "category": "fintech", "verified": True
            },
            {
                "id": "startup-2", "name": "HealthSync", "tagline": "Remote patient monitoring",
                "traction": 87, "metrics": {"mrr": 62000, "growth": 35, "users": 8500},
                "category": "health", "verified": True
            },
            {
                "id": "startup-3", "name": "CodeShip", "tagline": "Ship code 10x faster",
                "traction": 81, "metrics": {"mrr": 45000, "growth": 42, "users": 5200},
                "category": "ai", "verified": True
            },
            {
                "id": "startup-4", "name": "RetailGenius", "tagline": "AI inventory optimization",
                "traction": 74, "metrics": {"mrr": 32000, "growth": 22, "users": 950},
                "category": "ecommerce", "verified": True
            },
            {
                "id": "startup-5", "name": "TeamFlow", "tagline": "Async collaboration",
                "traction": 68, "metrics": {"mrr": 18000, "growth": 18, "users": 3200},
                "category": "saas", "verified": False
            }
        ]
        
        for s in startups:
            self._showcases[s["id"]] = StartupShowcase(
                startup_id=s["id"],
                name=s["name"],
                tagline=s["tagline"],
                traction_score=s["traction"],
                tier=self._get_tier(s["traction"]),
                verified=s["verified"],
                public_metrics=s["metrics"],
                showcases=[],
                integrations_connected=10 if s["verified"] else 5,
                days_active=120,
                rank_overall=0,
                rank_category=0,
                category=s["category"]
            )
    
    async def create_showcase(
        self,
        startup_id: str,
        startup_data: Dict[str, Any],
        traction_score: float = None
    ) -> StartupShowcase:
        """Create or update startup showcase profile"""
        
        # Get traction score if not provided
        if traction_score is None:
            from app.services.traction_score import get_traction_engine
            engine = get_traction_engine()
            metrics = startup_data.get("metrics", {})
            score = engine.calculate_score(metrics)
            traction_score = score.overall_score
            tier = score.tier
        else:
            tier = self._get_tier(traction_score)
        
        showcase = StartupShowcase(
            startup_id=startup_id,
            name=startup_data.get("name", "Unnamed Startup"),
            tagline=startup_data.get("tagline", ""),
            traction_score=traction_score,
            tier=tier,
            verified=startup_data.get("verified", False),
            public_metrics=startup_data.get("public_metrics", {}),
            showcases=[],
            integrations_connected=startup_data.get("integrations_count", 0),
            days_active=startup_data.get("days_active", 0),
            rank_overall=0,
            rank_category=0,
            category=startup_data.get("category", "other")
        )
        
        self._showcases[startup_id] = showcase
        return showcase
    
    async def add_showcase_item(
        self,
        startup_id: str,
        showcase_type: ShowcaseType,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add a showcase item (demo, milestone, etc.)
        
        AI agents automatically curate and highlight best content
        """
        showcase_item = {
            "id": f"{startup_id}_{datetime.utcnow().timestamp()}",
            "type": showcase_type.value,
            "title": content.get("title", ""),
            "description": content.get("description", ""),
            "media_url": content.get("media_url"),
            "metrics": content.get("metrics", {}),
            "created_at": datetime.utcnow().isoformat(),
            "featured": False,
            "views": 0,
            "reactions": {}
        }
        
        if startup_id in self._showcases:
            self._showcases[startup_id].showcases.append(showcase_item)
        
        # AI agent auto-curates for featuring
        await self._ai_curate_showcase(showcase_item)
        
        return showcase_item
    
    async def get_leaderboard(
        self,
        category: str = None,
        limit: int = 50,
        time_period: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Get ranked leaderboard of startups
        
        This is the Anti-YC: Pure metrics ranking, no pedigree
        """
        showcases = list(self._showcases.values())
        
        # Filter by category if specified
        if category:
            showcases = [s for s in showcases if s.category == category]
        
        # Sort by traction score
        showcases.sort(key=lambda x: x.traction_score, reverse=True)
        
        # Assign ranks
        for i, showcase in enumerate(showcases):
            showcase.rank_overall = i + 1
        
        # Return top N
        return [
            {
                "rank": s.rank_overall,
                "startup_id": s.startup_id,
                "name": s.name,
                "tagline": s.tagline,
                "traction_score": s.traction_score,
                "tier": s.tier,
                "verified": s.verified,
                "category": s.category,
                "public_metrics": s.public_metrics,
                "integrations_connected": s.integrations_connected,
            }
            for s in showcases[:limit]
        ]
    
    async def get_featured_showcases(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get AI-curated featured showcases
        
        Agent automatically selects best demos, milestones, growth stories
        """
        all_showcases = []
        for startup in self._showcases.values():
            for item in startup.showcases:
                if item.get("featured"):
                    all_showcases.append({
                        "startup_name": startup.name,
                        "startup_id": startup.startup_id,
                        "traction_score": startup.traction_score,
                        **item
                    })
        
        # Sort by views/engagement
        all_showcases.sort(key=lambda x: x.get("views", 0), reverse=True)
        
        return all_showcases[:limit]
    
    async def _ai_curate_showcase(self, showcase_item: Dict) -> bool:
        """
        AI agent automatically curates showcases
        
        Uses Gemini to evaluate quality and relevance
        """
        from app.services.gemini_service import get_gemini_service
        
        gemini = get_gemini_service()
        
        prompt = f"""
        Evaluate this startup showcase item for featuring:
        
        Type: {showcase_item.get('type')}
        Title: {showcase_item.get('title')}
        Description: {showcase_item.get('description')}
        Metrics: {showcase_item.get('metrics')}
        
        Should this be featured on the public showcase? Consider:
        1. Is it impressive/noteworthy?
        2. Does it demonstrate real progress?
        3. Will it inspire other founders?
        
        Respond with just: FEATURE or SKIP
        """
        
        try:
            response = await gemini.generate(prompt)
            if "FEATURE" in response.text.upper():
                showcase_item["featured"] = True
                logger.info("Showcase featured by AI", id=showcase_item.get("id"))
                return True
        except Exception as e:
            logger.warning("AI curation failed", error=str(e))
        
        return False
    
    def _get_tier(self, score: float) -> str:
        """Get tier from score"""
        if score >= 80:
            return "rocket"
        elif score >= 60:
            return "scaling"
        elif score >= 40:
            return "rising"
        elif score >= 20:
            return "building"
        return "ideation"


class AgentManagedCommunity:
    """
    AI-managed community features
    
    Agents handle:
    - Matching founders with complementary skills
    - Curating content and showcases
    - Facilitating introductions
    - Managing async "demo" showcases
    """
    
    def __init__(self):
        self.showcase_service = CommunityShowcaseService()
    
    async def match_cofounders(
        self,
        founder_profile: Dict[str, Any],
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        AI-powered co-founder matching
        
        Matches based on:
        - Complementary skills (e.g., Tech + Sales)
        - Timezone compatibility
        - Stage alignment
        - Industry interest
        """
        from app.services.gemini_service import get_gemini_service
        import json
        
        gemini = get_gemini_service()
        
        # 1. Seed some mock profiles for the AI to pick from (in prod, this comes from DB)
        candidate_pool = [
            {"id": "c1", "name": "Sarah Chen", "role": "CTO", "skills": ["Python", "AI", "Cloud Arch"], "timezone": "UTC-8", "bio": "Ex-Google AI engineer looking for a biz dev partner."},
            {"id": "c2", "name": "Marcus Johnson", "role": "CRO", "skills": ["B2B Sales", "GTM", "Partnerships"], "timezone": "UTC-5", "bio": "Scaled SaaS to $10M ARR. Need a technical genius."},
            {"id": "c3", "name": "Deepak Patel", "role": "Product Lead", "skills": ["UX/UI", "Product Mgmt", "No-Code"], "timezone": "UTC+5.5", "bio": "Product visionary obsessed with PLG growth."},
            {"id": "c4", "name": "Elena Rodriguez", "role": "Marketing Lead", "skills": ["Content", "SEO", "Community"], "timezone": "UTC+1", "bio": "Building communities for Web3/AI startups."},
            {"id": "c5", "name": "Alex Kim", "role": "Full Stack", "skills": ["React", "Node", "Postgres"], "timezone": "UTC+9", "bio": "Hackathon winner. I build fast. Need someone to sell it."}
        ]
        
        prompt = f"""
        Find ideal co-founder matches for this founder from the provided candidate pool:
        
        Founder Profile:
        Skills: {founder_profile.get('skills', [])}
        Looking for: {founder_profile.get('looking_for', [])}
        Timezone: {founder_profile.get('timezone')}
        Bio: {founder_profile.get('bio', '')}
        
        Candidate Pool:
        {json.dumps(candidate_pool)}
        
        Task:
        1. Analyze compatibility (Skills, Timezone, Vision)
        2. Select the top {limit} matches
        3. Assign a 'match_score' (0-100) and 'match_reason' for each
        
        Return pure JSON format:
        {{
            "matches": [
                {{
                    "id": "c1",
                    "name": "Sarah Chen",
                    "role": "CTO",
                    "match_score": 95,
                    "match_reason": "Complementary skills (Tech vs Sales) and compatible timezone.",
                    "skills": ["..."],
                    "bio": "..."
                }}
            ]
        }}
        """
        
        try:
            response = await gemini.generate(prompt)
            # Basic parsing - in prod use structured output mode or more robust parsing
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text)
            return {
                "profile": founder_profile,
                "suggested_matches": data.get("matches", []),
                "match_count": len(data.get("matches", []))
            }
        except Exception as e:
            logger.error("Co-founder matching failed", error=str(e))
            # Fallback to direct return of candidates
            return {
                "profile": founder_profile,
                "suggested_matches": candidate_pool[:limit],
                "match_count": len(candidate_pool[:limit]),
                "error": "AI processing failed, showing all candidates"
            }
    
    async def generate_async_demo(
        self,
        startup_id: str,
        startup_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate async Demo Day content
        
        No weekly manual demo days.
        AI generates pitch deck + talking points.
        Investors browse async.
        """
        from app.services.gemini_service import get_gemini_service
        
        gemini = get_gemini_service()
        
        prompt = f"""
        Generate a compelling 2-minute pitch script for this startup:
        
        Name: {startup_data.get('name')}
        Tagline: {startup_data.get('tagline')}
        Problem: {startup_data.get('problem')}
        Solution: {startup_data.get('solution')}
        Metrics: {startup_data.get('metrics')}
        Ask: {startup_data.get('ask')}
        
        Create:
        1. Hook (10 seconds)
        2. Problem statement (20 seconds)
        3. Solution (30 seconds)
        4. Traction (30 seconds)
        5. Ask (20 seconds)
        6. Closing (10 seconds)
        
        Make it punchy, data-driven, and memorable.
        """
        
        response = await gemini.generate(prompt)
        
        return {
            "startup_id": startup_id,
            "pitch_script": response.text,
            "generated_at": datetime.utcnow().isoformat(),
            "type": "async_demo"
        }


# Global instances
_showcase_service: Optional[CommunityShowcaseService] = None
_community: Optional[AgentManagedCommunity] = None


def get_showcase_service() -> CommunityShowcaseService:
    """Get showcase service"""
    global _showcase_service
    if _showcase_service is None:
        _showcase_service = CommunityShowcaseService()
    return _showcase_service


def get_community_service() -> AgentManagedCommunity:
    """Get community service"""
    global _community
    if _community is None:
        _community = AgentManagedCommunity()
    return _community
