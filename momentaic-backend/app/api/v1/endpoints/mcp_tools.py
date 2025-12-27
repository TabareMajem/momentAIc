"""
MCP & AI Tools API Endpoints
Expose MCP tools, traction scores, and leaderboard
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/mcp", tags=["MCP Tools"])


# --- Request/Response Models ---

class ToolExecuteRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}


class TractionScoreRequest(BaseModel):
    metrics: Dict[str, Any]
    startup_id: Optional[str] = None


class ShowcaseCreateRequest(BaseModel):
    startup_id: str
    startup_data: Dict[str, Any]


class ShowcaseItemRequest(BaseModel):
    startup_id: str
    showcase_type: str
    content: Dict[str, Any]


class DeepResearchRequest(BaseModel):
    topic: str
    depth: str = "comprehensive"


class CofounderMatchRequest(BaseModel):
    skills: List[str]
    looking_for: List[str]
    timezone: Optional[str] = None
    stage: Optional[str] = None
    industry: Optional[str] = None


# --- MCP Tool Endpoints ---

@router.get("/manifest")
async def get_mcp_manifest():
    """
    Get MCP manifest with all available tools
    
    Returns tool definitions for AI model integration
    """
    from app.services.mcp_registry import get_mcp_registry
    
    registry = get_mcp_registry()
    return registry.get_mcp_manifest()


@router.get("/tools")
async def list_tools(category: Optional[str] = None):
    """List all available MCP tools"""
    from app.services.mcp_registry import get_mcp_registry
    
    registry = get_mcp_registry()
    tools = registry.list_tools(category)
    return {
        "tools": tools,
        "total": len(tools),
        "categories": ["integrations", "agents", "actions"]
    }


@router.post("/execute")
async def execute_tool(request: ToolExecuteRequest):
    """
    Execute an MCP tool
    
    Allows AI models to dynamically invoke any registered tool
    """
    from app.services.mcp_registry import get_mcp_registry
    
    registry = get_mcp_registry()
    result = await registry.execute_tool(request.tool_name, request.parameters)
    
    if "error" in result and result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


# --- Traction Score Endpoints ---

traction_router = APIRouter(prefix="/traction", tags=["Traction Score"])


@traction_router.post("/score")
async def calculate_traction_score(request: TractionScoreRequest):
    """
    Calculate founder traction score
    
    Performance-based ranking - the anti-pedigree approach
    """
    from app.services.traction_score import get_traction_engine
    
    engine = get_traction_engine()
    score = engine.calculate_score(request.metrics, request.startup_id)
    
    return {
        "overall_score": score.overall_score,
        "tier": score.tier,
        "percentile": score.percentile,
        "breakdown": {
            "revenue": score.revenue_score,
            "growth": score.velocity_score,
            "engagement": score.product_score,
            "momentum": score.momentum_score
        },
        "verified": score.verified,
        "last_updated": score.last_updated.isoformat()
    }


@traction_router.post("/hood-memo")
async def generate_hood_investment_memo(request: TractionScoreRequest):
    """
    Generate Hood Investment Memo
    
    AI-powered VC-quality memos for the 100,000 founders building billion-dollar companies.
    The Hood = where real builders come from.
    """
    from app.services.traction_score import get_traction_engine
    
    engine = get_traction_engine()
    score = engine.calculate_score(request.metrics, request.startup_id)
    
    startup_data = {
        **request.metrics,
        "name": request.startup_id or "Your Startup"
    }
    
    memo = await engine.generate_investor_memo(score, startup_data)
    
    return {
        "memo": memo,
        "score": score.overall_score,
        "tier": score.tier
    }


# --- Leaderboard & Showcase Endpoints ---

leaderboard_router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@leaderboard_router.get("/")
async def get_leaderboard(
    category: Optional[str] = None,
    limit: int = 50,
    time_period: str = "all"
):
    """
    Get ranked leaderboard
    
    Public ranking of startups by traction - pure metrics
    """
    from app.services.community_showcase import get_showcase_service
    
    service = get_showcase_service()
    leaderboard = await service.get_leaderboard(category, limit, time_period)
    
    return {
        "leaderboard": leaderboard,
        "total": len(leaderboard),
        "category": category or "all",
        "time_period": time_period
    }


@leaderboard_router.get("/featured")
async def get_featured_showcases(limit: int = 10):
    """
    Get AI-curated featured showcases
    
    Agent automatically selects best demos and milestones
    """
    from app.services.community_showcase import get_showcase_service
    
    service = get_showcase_service()
    featured = await service.get_featured_showcases(limit)
    
    return {
        "featured": featured,
        "total": len(featured)
    }


# --- Community Endpoints ---

community_router = APIRouter(prefix="/community", tags=["Community"])


@community_router.post("/showcase/create")
async def create_showcase(request: ShowcaseCreateRequest):
    """Create or update startup showcase profile"""
    from app.services.community_showcase import get_showcase_service
    
    service = get_showcase_service()
    showcase = await service.create_showcase(
        request.startup_id,
        request.startup_data
    )
    
    return {
        "startup_id": showcase.startup_id,
        "name": showcase.name,
        "traction_score": showcase.traction_score,
        "tier": showcase.tier,
        "verified": showcase.verified
    }


@community_router.post("/showcase/add-item")
async def add_showcase_item(request: ShowcaseItemRequest):
    """Add showcase item (demo, milestone, etc.)"""
    from app.services.community_showcase import get_showcase_service, ShowcaseType
    
    service = get_showcase_service()
    
    try:
        showcase_type = ShowcaseType(request.showcase_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid showcase type: {request.showcase_type}")
    
    item = await service.add_showcase_item(
        request.startup_id,
        showcase_type,
        request.content
    )
    
    return item


@community_router.post("/cofounder-match")
async def match_cofounders(request: CofounderMatchRequest):
    """
    AI-powered co-founder matching
    
    Find complementary co-founders globally
    """
    from app.services.community_showcase import get_community_service
    
    service = get_community_service()
    
    profile = {
        "skills": request.skills,
        "looking_for": request.looking_for,
        "timezone": request.timezone,
        "stage": request.stage,
        "industry": request.industry
    }
    
    matches = await service.match_cofounders(profile)
    return matches


@community_router.post("/async-demo")
async def generate_async_demo(startup_id: str, startup_data: Dict[str, Any]):
    """
    Generate async demo pitch
    
    AI creates pitch script - no manual demo days needed
    """
    from app.services.community_showcase import get_community_service
    
    service = get_community_service()
    demo = await service.generate_async_demo(startup_id, startup_data)
    return demo


# --- Deep Research Endpoints ---

research_router = APIRouter(prefix="/research", tags=["Deep Research"])


@research_router.post("/deep")
async def deep_research(request: DeepResearchRequest):
    """
    Deep Research mode
    
    Comprehensive web research using Gemini
    """
    from app.services.gemini_service import get_gemini_service
    
    gemini = get_gemini_service()
    result = await gemini.deep_research(request.topic, request.depth)
    return result


# Export all routers
__all__ = ["router", "traction_router", "leaderboard_router", "community_router", "research_router"]
