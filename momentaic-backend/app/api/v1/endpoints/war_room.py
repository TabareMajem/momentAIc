"""
War Room API Endpoints - Admin Only
Provides access to the War Room agent swarm for authorized admins.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import structlog

from app.core.admin_guard import AdminGuard
from app.models.user import User
from app.agents.kol_headhunter_agent import kol_headhunter, HitList
from app.agents.dealmaker_agent import dealmaker
from app.agents.localization_architect_agent import localization_architect

logger = structlog.get_logger()

router = APIRouter(prefix="/admin/war-room", tags=["War Room"])


# Request/Response Models
class KOLScanRequest(BaseModel):
    """Request to scan for KOLs."""
    regions: List[str] = Field(
        default=["US", "LatAm", "Europe", "Asia"],
        description="Regions to scan"
    )
    max_targets_per_region: int = Field(default=50, ge=10, le=200)
    keywords: Optional[List[str]] = None


class OutreachCampaignRequest(BaseModel):
    """Request to launch an outreach campaign."""
    hit_list_ids: List[str] = Field(description="IDs of hit lists to use")
    sequence: str = Field(default="initial", description="Email sequence to use")
    auto_create_pages: bool = Field(default=True, description="Auto-create partner pages for premium targets")


class LocalizationRequest(BaseModel):
    """Request to localize content."""
    source_content: Dict[str, str] = Field(description="Original content to localize")
    target_regions: List[str] = Field(description="Target regions for localization")


class PipelineStatusResponse(BaseModel):
    """Ambassador pipeline status."""
    total_deals: int
    by_stage: Dict[str, int]
    by_region: Dict[str, int]
    conversion_rate: float
    recent_activity: List[Dict[str, Any]]


# Endpoints

@router.get("/status")
async def get_war_room_status(
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Get War Room status and agent availability.
    Admin only.
    """
    return {
        "status": "operational",
        "admin": current_user.email,
        "agents": {
            "kol_headhunter": "ready",
            "dealmaker": "ready",
            "localization_architect": "ready"
        },
        "pipeline": {
            "total_targets": 0,
            "active_campaigns": 0,
            "pending_responses": 0
        }
    }


@router.post("/scan-kols")
async def scan_kols(
    request: KOLScanRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Trigger KOL discovery scan across specified regions.
    Admin only.
    
    This initiates a background scan using the KOL Headhunter agent.
    Results are stored and can be retrieved via /hit-lists endpoint.
    """
    logger.info(
        "War Room: KOL scan initiated",
        admin=current_user.email,
        regions=request.regions
    )
    
    # Queue background scan
    async def run_scan():
        try:
            results = {}
            for region in request.regions:
                hit_list = await kol_headhunter.scan_region(
                    region=region,
                    max_targets=request.max_targets_per_region
                )
                results[region] = hit_list
            logger.info(f"KOL scan complete: {len(results)} regions scanned")
        except Exception as e:
            logger.error(f"KOL scan failed: {e}")
    
    background_tasks.add_task(run_scan)
    
    return {
        "status": "scan_initiated",
        "regions": request.regions,
        "estimated_time_minutes": len(request.regions) * 5,
        "message": f"Scanning {len(request.regions)} regions for KOL targets..."
    }


@router.get("/hit-lists")
async def get_hit_lists(
    region: Optional[str] = None,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Retrieve generated hit lists from KOL scans.
    Admin only.
    """
    # In production, fetch from database
    return {
        "hit_lists": [],
        "total_targets": 0,
        "filters": {"region": region} if region else {}
    }


@router.post("/launch-outreach")
async def launch_outreach(
    request: OutreachCampaignRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Launch an outreach campaign to KOL targets.
    Admin only.
    
    Uses the Dealmaker agent to send personalized outreach.
    """
    logger.info(
        "War Room: Outreach campaign launched",
        admin=current_user.email,
        hit_lists=request.hit_list_ids
    )
    
    async def run_outreach():
        try:
            # Fetch hit lists and launch campaign
            results = await dealmaker.launch_outreach_campaign(
                hit_list=[],  # Populated from DB
                sequence=request.sequence
            )
            logger.info(f"Outreach complete: {results}")
        except Exception as e:
            logger.error(f"Outreach failed: {e}")
    
    background_tasks.add_task(run_outreach)
    
    return {
        "status": "campaign_launched",
        "sequence": request.sequence,
        "auto_pages": request.auto_create_pages,
        "message": "Dealmaker agent is processing outreach..."
    }


@router.post("/localize")
async def localize_content(
    request: LocalizationRequest,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Localize marketing content for target regions.
    Admin only.
    """
    logger.info(
        "War Room: Localization requested",
        admin=current_user.email,
        regions=request.target_regions
    )
    
    results = await localization_architect.localize_campaign(
        source_content=request.source_content,
        target_regions=request.target_regions
    )
    
    return {
        "status": "localization_complete",
        "regions": request.target_regions,
        "results": {region: r.dict() for region, r in results.items()}
    }


@router.get("/pipeline")
async def get_pipeline(
    current_user: User = Depends(AdminGuard.require_admin)
) -> PipelineStatusResponse:
    """
    Get the current ambassador pipeline status.
    Admin only.
    """
    # In production, fetch from database
    return PipelineStatusResponse(
        total_deals=0,
        by_stage={
            "identified": 0,
            "contacted": 0,
            "responded": 0,
            "negotiating": 0,
            "closed_won": 0,
            "closed_lost": 0
        },
        by_region={
            "US": 0,
            "LatAm": 0,
            "Europe": 0,
            "Asia": 0
        },
        conversion_rate=0.0,
        recent_activity=[]
    )


@router.post("/handle-response")
async def handle_kol_response(
    kol_email: str,
    response_content: str,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Process a KOL's response and get recommended next action.
    Admin only.
    """
    result = await dealmaker.handle_response(
        kol_email=kol_email,
        response_content=response_content
    )
    
    return {
        "status": "analyzed",
        "recommendation": result
    }


@router.post("/create-partner-page")
async def create_partner_page(
    influencer_name: str,
    handle: str,
    custom_headline: Optional[str] = None,
    current_user: User = Depends(AdminGuard.require_admin)
) -> Dict[str, Any]:
    """
    Create a co-branded partner landing page.
    Admin only.
    """
    page_url = f"https://momentaic.com/partners/{handle.lower()}"
    
    return {
        "status": "page_created",
        "url": page_url,
        "influencer": influencer_name,
        "headline": custom_headline or f"{influencer_name} x MomentAIc"
    }
