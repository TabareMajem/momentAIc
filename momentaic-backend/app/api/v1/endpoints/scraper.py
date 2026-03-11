"""
Influencer Scraper API Endpoints
REST + SSE endpoints for launching, monitoring, and exporting scrape jobs.
"""

import json
import structlog
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import List, Dict, Any

from app.core.security import get_current_user
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session

logger = structlog.get_logger(__name__)
router = APIRouter()


# ============ SCHEMAS ============

class LaunchJobRequest(BaseModel):
    """Request body for launching a scrape job."""
    accounts: Dict[str, List[Dict[str, str]]] = {}  # platform -> [{username, password, cookies_path}]
    proxies: List[str] = []  # List of proxy URLs
    batch_size: Optional[int] = 50
    max_workers: Optional[int] = 10
    is_shared: bool = False
    startup_id: Optional[str] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    total_targets: int
    processed: int
    errors: int
    progress_pct: float
    elapsed_seconds: float
    rate_per_second: float


class AccountLoadRequest(BaseModel):
    """Load accounts into the rotation pool."""
    platform: str
    accounts: List[Dict[str, str]]


class ProxyLoadRequest(BaseModel):
    """Load proxies into the pool."""
    proxies: List[str]


class SaveAccountRequest(BaseModel):
    """Save a social media account for scraping."""
    platform: str  # instagram, twitter, tiktok
    username: str
    password: Optional[str] = None
    cookie_string: Optional[str] = None
    proxy_url: Optional[str] = None


# ============ ENDPOINTS ============

@router.post("/launch")
async def launch_scrape_job(
    file: UploadFile = File(...),
    is_shared: bool = Query(False, description="Share results to Global Community DB"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a CSV of target profiles and launch a scraping job.

    CSV format:
    ```
    handle,platform
    @username1,instagram
    @username2,twitter
    @username3,tiktok
    ```

    Returns a job_id for monitoring progress via SSE.
    """
    from app.services.scraper.scraper_orchestrator import scraper_orchestrator

    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    content = await file.read()
    csv_text = content.decode("utf-8")

    startup_id = getattr(current_user, 'active_startup_id', None)
    
    targets, job_id = scraper_orchestrator.ingest_csv(
        csv_text, 
        startup_id=startup_id,
        is_shared=is_shared,
    )

    if not targets:
        raise HTTPException(status_code=400, detail="No valid targets found in CSV")

    logger.info(
        "Scrape job created",
        job_id=job_id,
        targets=len(targets),
        user=current_user.email,
    )

    return {
        "job_id": job_id,
        "total_targets": len(targets),
        "status": "pending",
        "message": f"Job created. Start monitoring at /api/v1/scraper/status/{job_id}",
    }


@router.post("/accounts")
async def load_accounts(
    request: AccountLoadRequest,
    current_user: User = Depends(get_current_user),
):
    """Load social media accounts into the rotation pool."""
    from app.services.scraper.account_pool import account_pool

    count = account_pool.load_accounts(request.platform, request.accounts)
    return {
        "loaded": count,
        "platform": request.platform,
        "pool_status": account_pool.get_pool_status(request.platform),
    }


@router.post("/proxies")
async def load_proxies(
    request: ProxyLoadRequest,
    current_user: User = Depends(get_current_user),
):
    """Load proxy URLs into the rotation pool."""
    from app.services.scraper.proxy_manager import proxy_manager

    count = proxy_manager.load_proxies(request.proxies)
    return {"loaded": count, "stats": proxy_manager.get_stats()}


@router.get("/status/{job_id}")
async def stream_job_status(
    job_id: str,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    SSE stream of real-time scraping progress.
    Connect and receive live updates as profiles are scraped.
    """
    from app.services.scraper.scraper_orchestrator import scraper_orchestrator
    from app.core.security import decode_access_token

    if not token:
        raise HTTPException(status_code=401, detail="Missing token query parameter")
        
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid token")

    job_status = scraper_orchestrator.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_stream():
        async for event_json in scraper_orchestrator.run_job(job_id):
            yield f"data: {event_json}\n\n"
        yield f"data: {json.dumps({'event': 'stream_end'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/status/{job_id}/poll")
async def poll_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Poll-based (non-streaming) job status check."""
    from app.services.scraper.scraper_orchestrator import scraper_orchestrator

    status = scraper_orchestrator.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status


@router.get("/results/{job_id}")
async def get_results(
    job_id: str,
    format: str = Query("json", regex="^(json|csv)$"),
    current_user: User = Depends(get_current_user),
):
    """
    Download completed scraping results as JSON or CSV.
    """
    from app.services.scraper.scraper_orchestrator import scraper_orchestrator

    results = scraper_orchestrator.get_results(job_id, format=format)
    if results is None:
        raise HTTPException(status_code=404, detail="Job not found or still running")

    if format == "csv":
        return Response(
            content=results,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="influencers_{job_id}.csv"',
            },
        )

    return Response(
        content=results,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="influencers_{job_id}.json"',
        },
    )


@router.post("/stop/{job_id}")
async def stop_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Gracefully stop a running scrape job."""
    from app.services.scraper.scraper_orchestrator import scraper_orchestrator

    success = scraper_orchestrator.stop_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"job_id": job_id, "status": "stopped"}


@router.get("/pool/status")
async def get_pool_status(
    current_user: User = Depends(get_current_user),
):
    """Get the current status of all account pools and proxies."""
    from app.services.scraper.account_pool import account_pool
    from app.services.scraper.proxy_manager import proxy_manager

    return {
        "accounts": account_pool.get_all_status(),
        "proxies": proxy_manager.get_stats(),
    }

@router.get("/community")
async def get_community_database(
    platform: Optional[str] = Query(None, description="Filter by platform (e.g., instagram, twitter)"),
    keyword: Optional[str] = Query(None, description="Search bio/keywords for specific term"),
    language: Optional[str] = Query(None, description="Filter by language code (e.g., en, es)"),
    min_followers: Optional[int] = Query(0, description="Minimum follower count"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch profiles from the Global Community Database (is_shared=True).
    """
    from app.models.scraped_profile import ScrapedProfile
    from sqlalchemy import or_
    
    query = db.query(ScrapedProfile).filter(ScrapedProfile.is_shared == True)
    
    if platform:
        query = query.filter(ScrapedProfile.platform == platform.lower())
        
    if min_followers and min_followers > 0:
        query = query.filter(ScrapedProfile.follower_count >= min_followers)
        
    if language:
        query = query.filter(ScrapedProfile.language == language.lower())
        
    if keyword:
        search_term = f"%{keyword.lower()}%"
        query = query.filter(
            or_(
                ScrapedProfile.bio.ilike(search_term),
                # PostgreSQL specific JSONB contains/text search can be added here
                # if needed, but bio search is usually sufficient for simple keyword filters.
            )
        )
        
    total = query.count()
    profiles = query.order_by(ScrapedProfile.created_at.desc()).offset(offset).limit(limit).all()
    
    results = []
    for p in profiles:
        results.append({
            "id": str(p.id),
            "platform": p.platform,
            "handle": p.handle,
            "url": p.url,
            "follower_count": p.follower_count,
            "bio": p.bio,
            "engagement_rate": p.engagement_rate,
            "keywords": p.keywords,
            "language": p.language,
            "created_at": p.created_at.isoformat() if p.created_at else None
        })
        
    return {
        "items": results,
        "total": total,
        "limit": limit,
        "offset": offset
    }


# ============ ACCOUNT MANAGEMENT ENDPOINTS ============

@router.post("/accounts/save")
async def save_account(
    request: SaveAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save a social media account for use in the scraping pool.
    Credentials are encrypted at rest using Fernet.
    """
    from app.models.platform_account import PlatformAccount
    from app.core.credential_encryption import encrypt_credential

    if request.platform not in ("instagram", "twitter", "tiktok"):
        raise HTTPException(status_code=400, detail="Platform must be instagram, twitter, or tiktok")

    if not request.password and not request.cookie_string:
        raise HTTPException(status_code=400, detail="Provide either a password or cookie string")

    startup_id = getattr(current_user, 'active_startup_id', None)
    if not startup_id:
        raise HTTPException(status_code=400, detail="No active startup selected")

    # Encrypt credentials
    enc_password = encrypt_credential(request.password) if request.password else None
    enc_cookies = encrypt_credential(request.cookie_string) if request.cookie_string else None

    account = PlatformAccount(
        startup_id=startup_id,
        platform=request.platform,
        username=request.username,
        encrypted_password=enc_password,
        encrypted_cookies=enc_cookies,
        proxy_url=request.proxy_url,
    )

    db.add(account)
    await db.commit()
    await db.refresh(account)

    logger.info("Account saved", platform=request.platform, username=request.username)

    return {
        "id": str(account.id),
        "platform": account.platform,
        "username": account.username,
        "status": account.status,
        "has_password": bool(enc_password),
        "has_cookies": bool(enc_cookies),
    }


@router.get("/accounts/mine")
async def list_my_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all saved accounts for the current startup (credentials redacted)."""
    from app.models.platform_account import PlatformAccount
    from sqlalchemy import select

    startup_id = getattr(current_user, 'active_startup_id', None)
    if not startup_id:
        return {"accounts": []}

    result = await db.execute(
        select(PlatformAccount)
        .where(PlatformAccount.startup_id == startup_id)
        .where(PlatformAccount.is_active == True)
        .order_by(PlatformAccount.created_at.desc())
    )
    accounts = result.scalars().all()

    return {
        "accounts": [
            {
                "id": str(a.id),
                "platform": a.platform,
                "username": a.username,
                "status": a.status,
                "has_password": bool(a.encrypted_password),
                "has_cookies": bool(a.encrypted_cookies),
                "proxy_url": a.proxy_url,
                "last_error": a.last_error,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in accounts
        ],
        "total": len(accounts),
        "by_platform": {
            "instagram": sum(1 for a in accounts if a.platform == "instagram"),
            "twitter": sum(1 for a in accounts if a.platform == "twitter"),
            "tiktok": sum(1 for a in accounts if a.platform == "tiktok"),
        }
    }


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-delete an account (mark as inactive)."""
    from app.models.platform_account import PlatformAccount
    from sqlalchemy import select

    startup_id = getattr(current_user, 'active_startup_id', None)

    result = await db.execute(
        select(PlatformAccount)
        .where(PlatformAccount.id == account_id)
        .where(PlatformAccount.startup_id == startup_id)
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.is_active = False
    await db.commit()

    return {"deleted": True, "id": account_id}

