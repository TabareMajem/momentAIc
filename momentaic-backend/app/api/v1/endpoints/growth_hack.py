"""
Growth Hacking API Endpoints
Exposes KOL research and growth strategies to the War Room
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import structlog

from app.core.admin_guard import AdminGuard
from app.models.user import User
from app.services.kol_research import kol_research
from app.services.growth_strategies import growth_strategies

logger = structlog.get_logger()

router = APIRouter(prefix="/growth-hack", tags=["Growth Hacking"])


# ============ SCHEMAS ============

class KOLSearchRequest(BaseModel):
    """Request for KOL search."""
    keywords: Optional[List[str]] = None
    min_followers: int = Field(default=5000, ge=1000)
    max_followers: int = Field(default=100000, le=500000)
    regions: List[str] = Field(default=["US", "LatAm", "Europe", "Asia"])


class ContentSyndicationRequest(BaseModel):
    """Request for content syndication plan."""
    title: str
    body: str
    platforms: Optional[List[str]] = None


class LaunchBlitzRequest(BaseModel):
    """Request for full launch blitz."""
    target_users: int = Field(default=100000, ge=1000)


# ============ KOL RESEARCH ENDPOINTS ============

@router.post("/kol/search/twitter")
async def search_twitter_kols(
    request: KOLSearchRequest,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Search for KOLs on Twitter/X.
    Admin only.
    """
    profiles = await kol_research.find_twitter_kols(
        keywords=request.keywords,
        min_followers=request.min_followers,
        max_followers=request.max_followers
    )
    
    return {
        "source": "twitter",
        "total_found": len(profiles),
        "profiles": [p.dict() for p in profiles[:50]]
    }


@router.post("/kol/search/producthunt")
async def search_producthunt_makers(
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Find Product Hunt makers.
    Admin only.
    """
    profiles = await kol_research.find_product_hunt_makers()
    
    return {
        "source": "producthunt",
        "total_found": len(profiles),
        "profiles": [p.dict() for p in profiles]
    }


@router.post("/kol/search/github")
async def search_github_influencers(
    topics: Optional[List[str]] = None,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Find GitHub influencers.
    Admin only.
    """
    profiles = await kol_research.find_github_influencers(topics=topics)
    
    return {
        "source": "github",
        "total_found": len(profiles),
        "profiles": [p.dict() for p in profiles]
    }


@router.post("/kol/generate-hitlist")
async def generate_full_hitlist(
    request: KOLSearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Generate a complete KOL hit list from all sources.
    Admin only.
    """
    logger.info("Generating full KOL hit list", admin=current_user.email)
    
    hit_list = await kol_research.generate_hit_list(
        target_count=100,
        regions=request.regions
    )
    
    return hit_list


# ============ CONTENT SYNDICATION ENDPOINTS ============

@router.post("/syndicate")
async def create_syndication_plan(
    request: ContentSyndicationRequest,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Create a content syndication plan across platforms.
    Admin only.
    """
    plan = await growth_strategies.syndicate_content(
        content={"title": request.title, "body": request.body},
        platforms=request.platforms
    )
    
    return plan


@router.get("/communities")
async def get_communities(
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Get list of relevant communities to participate in.
    Admin only.
    """
    communities = await growth_strategies.find_communities()
    
    return {
        "total": len(communities),
        "communities": communities
    }


@router.get("/reverse-outreach")
async def get_reverse_outreach_tactics(
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Get reverse outreach tactics (directories, podcasts, etc).
    Admin only.
    """
    tactics = await growth_strategies.setup_reverse_outreach()
    
    return tactics


# ============ LAUNCH BLITZ ============

@router.post("/blitz")
async def execute_launch_blitz(
    request: LaunchBlitzRequest,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Execute full launch blitz across all growth channels.
    Admin only.
    
    This is the "God Mode" activation for 100k user acquisition.
    """
    logger.info(
        "LAUNCH BLITZ INITIATED",
        admin=current_user.email,
        target=request.target_users
    )
    
    results = await growth_strategies.execute_launch_blitz(
        target_users=request.target_users
    )
    
    return results
