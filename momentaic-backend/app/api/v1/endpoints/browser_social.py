"""
Browser Social Endpoints — Browser-First Integration
Execute real actions on platforms (tweet, post, scrape) via Playwright browser automation.
No API keys needed — users provide their platform credentials.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.credential_encryption import encrypt_credential, decrypt_credential
from app.models.user import User
from app.models.platform_credentials import (
    PlatformCredential, PlatformType, CredentialStatus
)

logger = structlog.get_logger(__name__)
router = APIRouter()


# ==================
# Schemas
# ==================

class CredentialCreate(BaseModel):
    """Save platform credentials"""
    platform: PlatformType
    username: str
    password: str
    startup_id: Optional[UUID] = None


class CredentialResponse(BaseModel):
    """Credential status response (never returns password)"""
    id: UUID
    platform: str
    username: str
    status: str
    last_login_at: Optional[str] = None
    last_action_at: Optional[str] = None
    login_count: int = 0

    class Config:
        from_attributes = True


class BrowserPostRequest(BaseModel):
    """Request to post content via browser"""
    content: str
    image_url: Optional[str] = None
    startup_id: Optional[UUID] = None


class BrowserScrapeRequest(BaseModel):
    """Request to scrape data from a platform"""
    target_url: Optional[str] = None
    data_type: str = "contacts"  # contacts, deals, followers, analytics
    startup_id: Optional[UUID] = None


class BrowserLoginRequest(BaseModel):
    """Trigger a browser login to save session"""
    startup_id: Optional[UUID] = None


# ==================
# Credential Management
# ==================

@router.post("/credentials", response_model=CredentialResponse, status_code=status.HTTP_201_CREATED)
async def save_credentials(
    data: CredentialCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Save encrypted platform credentials for browser automation"""
    # Check if credentials already exist for this platform
    existing = await db.execute(
        select(PlatformCredential).where(
            PlatformCredential.user_id == current_user.id,
            PlatformCredential.platform == data.platform,
        )
    )
    cred = existing.scalar_one_or_none()

    encrypted_pw = encrypt_credential(data.password)

    if cred:
        # Update existing
        cred.username = data.username
        cred.encrypted_password = encrypted_pw
        cred.status = CredentialStatus.PENDING
        cred.session_data = None  # Clear old session
        cred.updated_at = datetime.utcnow()
    else:
        # Create new
        cred = PlatformCredential(
            user_id=current_user.id,
            startup_id=data.startup_id,
            platform=data.platform,
            username=data.username,
            encrypted_password=encrypted_pw,
            status=CredentialStatus.PENDING,
        )
        db.add(cred)

    await db.flush()
    await db.commit()
    await db.refresh(cred)

    logger.info("platform_credentials_saved", platform=data.platform.value, user=current_user.email)

    return CredentialResponse(
        id=cred.id,
        platform=cred.platform.value,
        username=cred.username,
        status=cred.status.value,
        login_count=cred.login_count,
    )


@router.get("/credentials", response_model=list[CredentialResponse])
async def list_credentials(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all saved platform credentials (without passwords)"""
    result = await db.execute(
        select(PlatformCredential).where(
            PlatformCredential.user_id == current_user.id,
        )
    )
    creds = result.scalars().all()
    return [
        CredentialResponse(
            id=c.id,
            platform=c.platform.value,
            username=c.username,
            status=c.status.value,
            last_login_at=c.last_login_at.isoformat() if c.last_login_at else None,
            last_action_at=c.last_action_at.isoformat() if c.last_action_at else None,
            login_count=c.login_count,
        )
        for c in creds
    ]


@router.delete("/credentials/{platform}")
async def delete_credentials(
    platform: PlatformType,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete saved credentials for a platform"""
    result = await db.execute(
        select(PlatformCredential).where(
            PlatformCredential.user_id == current_user.id,
            PlatformCredential.platform == platform,
        )
    )
    cred = result.scalar_one_or_none()
    if not cred:
        raise HTTPException(status_code=404, detail="No credentials found for this platform")
    await db.delete(cred)
    await db.commit()
    return {"success": True, "message": f"Credentials for {platform.value} deleted"}


# ==================
# Browser Login (Session Persistence)
# ==================

@router.post("/login/{platform}")
async def browser_login(
    platform: PlatformType,
    request: BrowserLoginRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a browser login to the platform using stored credentials.
    Saves the browser session (cookies, local storage) for future use.
    """
    result = await db.execute(
        select(PlatformCredential).where(
            PlatformCredential.user_id == current_user.id,
            PlatformCredential.platform == platform,
        )
    )
    cred = result.scalar_one_or_none()
    if not cred:
        raise HTTPException(status_code=404, detail="No credentials found. Save credentials first.")

    password = decrypt_credential(cred.encrypted_password)

    # Platform-specific login URLs and selectors
    LOGIN_CONFIGS = {
        PlatformType.TWITTER: {
            "url": "https://x.com/i/flow/login",
            "username_selector": "input[autocomplete='username']",
            "password_selector": "input[autocomplete='current-password']",
            "submit_selector": "div[data-testid='LoginForm_Login_Button']",
            "success_indicator": "a[data-testid='AppTabBar_Home_Link']",
        },
        PlatformType.LINKEDIN: {
            "url": "https://www.linkedin.com/login",
            "username_selector": "#username",
            "password_selector": "#password",
            "submit_selector": "button[type='submit']",
            "success_indicator": ".feed-shared-update-v2",
        },
        PlatformType.INSTAGRAM: {
            "url": "https://www.instagram.com/accounts/login/",
            "username_selector": "input[name='username']",
            "password_selector": "input[name='password']",
            "submit_selector": "button[type='submit']",
            "success_indicator": "svg[aria-label='Home']",
        },
        PlatformType.HUBSPOT: {
            "url": "https://app.hubspot.com/login",
            "username_selector": "#username",
            "password_selector": "#password",
            "submit_selector": "#loginBtn",
            "success_indicator": ".private-page",
        },
    }

    config = LOGIN_CONFIGS.get(platform)
    if not config:
        raise HTTPException(status_code=400, detail=f"Browser login not supported for {platform.value} yet.")

    try:
        from playwright.async_api import async_playwright
        import json

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()

            # Navigate to login page
            await page.goto(config["url"], wait_until="domcontentloaded", timeout=20000)
            import asyncio
            await asyncio.sleep(2)

            # Fill username
            await page.wait_for_selector(config["username_selector"], timeout=10000)
            await page.fill(config["username_selector"], cred.username)
            await asyncio.sleep(0.5)

            # Some platforms (Twitter/X) have a multi-step login
            if platform == PlatformType.TWITTER:
                # Click "Next" after username
                await page.click("div[role='button']:has-text('Next')")
                await asyncio.sleep(2)
                await page.wait_for_selector(config["password_selector"], timeout=10000)

            # Fill password
            await page.fill(config["password_selector"], password)
            await asyncio.sleep(0.5)

            # Submit
            await page.click(config["submit_selector"])
            await asyncio.sleep(3)

            # Check for success
            try:
                await page.wait_for_selector(config["success_indicator"], timeout=15000)
                login_success = True
            except Exception:
                login_success = False

            if login_success:
                # Save session state
                storage_state = await context.storage_state()
                cred.session_data = storage_state
                cred.status = CredentialStatus.ACTIVE
                cred.last_login_at = datetime.utcnow()
                cred.login_count += 1
                cred.error_message = None
                await db.commit()

                await browser.close()
                logger.info("browser_login_success", platform=platform.value, user=current_user.email)
                return {
                    "success": True,
                    "platform": platform.value,
                    "message": f"Successfully logged into {platform.value}. Session saved."
                }
            else:
                # Check for 2FA prompt
                page_text = await page.inner_text("body")
                is_2fa = any(kw in page_text.lower() for kw in ["verification", "two-factor", "confirm your identity", "security code"])

                cred.status = CredentialStatus.TWO_FA_REQUIRED if is_2fa else CredentialStatus.LOGIN_FAILED
                cred.error_message = "2FA required" if is_2fa else "Login failed — check credentials"
                await db.commit()

                await browser.close()
                return {
                    "success": False,
                    "platform": platform.value,
                    "requires_2fa": is_2fa,
                    "message": cred.error_message,
                }

    except Exception as e:
        logger.error("browser_login_error", platform=platform.value, error=str(e))
        cred.status = CredentialStatus.LOGIN_FAILED
        cred.error_message = str(e)[:500]
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Browser login failed: {str(e)[:200]}")


# ==================
# Browser Posting
# ==================

@router.post("/post/{platform}")
async def browser_post(
    platform: PlatformType,
    request: BrowserPostRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Post content to a platform via browser automation.
    Requires active session (call /login/{platform} first).
    """
    result = await db.execute(
        select(PlatformCredential).where(
            PlatformCredential.user_id == current_user.id,
            PlatformCredential.platform == platform,
        )
    )
    cred = result.scalar_one_or_none()
    if not cred or not cred.session_data:
        raise HTTPException(
            status_code=400,
            detail=f"No active session for {platform.value}. Call POST /browser/login/{platform.value} first."
        )

    POSTING_CONFIGS = {
        PlatformType.TWITTER: {
            "url": "https://x.com/compose/post",
            "text_selector": "div[data-testid='tweetTextarea_0']",
            "submit_selector": "button[data-testid='tweetButton']",
            "success_check": "Post published",
        },
        PlatformType.LINKEDIN: {
            "url": "https://www.linkedin.com/feed/",
            "trigger_selector": "button.share-box-feed-entry__trigger",
            "text_selector": "div.ql-editor",
            "submit_selector": "button.share-actions__primary-action",
            "success_check": "Posted",
        },
    }

    config = POSTING_CONFIGS.get(platform)
    if not config:
        raise HTTPException(status_code=400, detail=f"Browser posting not yet supported for {platform.value}")

    try:
        from playwright.async_api import async_playwright
        import asyncio

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = await browser.new_context(
                storage_state=cred.session_data,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()

            # Navigate to compose/post page
            await page.goto(config["url"], wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)

            # LinkedIn has a trigger button to open the composer
            if platform == PlatformType.LINKEDIN and "trigger_selector" in config:
                try:
                    await page.click(config["trigger_selector"], timeout=5000)
                    await asyncio.sleep(1)
                except Exception:
                    pass  # Composer may already be open

            # Type content
            await page.wait_for_selector(config["text_selector"], timeout=10000)
            await page.click(config["text_selector"])
            await page.keyboard.type(request.content, delay=30)  # Human-like typing speed
            await asyncio.sleep(1)

            # Submit
            await page.click(config["submit_selector"])
            await asyncio.sleep(3)

            # Update session state (cookies may have updated)
            new_state = await context.storage_state()
            cred.session_data = new_state
            cred.last_action_at = datetime.utcnow()
            await db.commit()

            await browser.close()

            logger.info("browser_post_success", platform=platform.value, user=current_user.email,
                        content_length=len(request.content))

            return {
                "success": True,
                "platform": platform.value,
                "content_length": len(request.content),
                "message": f"Content posted to {platform.value} via browser automation.",
            }

    except Exception as e:
        logger.error("browser_post_error", platform=platform.value, error=str(e))
        raise HTTPException(status_code=500, detail=f"Browser posting failed: {str(e)[:200]}")


# ==================
# Browser Scraping (CRM, Analytics)
# ==================

@router.post("/scrape/{platform}")
async def browser_scrape(
    platform: PlatformType,
    request: BrowserScrapeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Scrape data from a platform via browser automation.
    Useful for CRM sync (HubSpot contacts), analytics, etc.
    """
    result = await db.execute(
        select(PlatformCredential).where(
            PlatformCredential.user_id == current_user.id,
            PlatformCredential.platform == platform,
        )
    )
    cred = result.scalar_one_or_none()
    if not cred or not cred.session_data:
        raise HTTPException(
            status_code=400,
            detail=f"No active session for {platform.value}. Call POST /browser/login/{platform.value} first."
        )

    SCRAPE_CONFIGS = {
        PlatformType.HUBSPOT: {
            "contacts": "https://app.hubspot.com/contacts/",
            "deals": "https://app.hubspot.com/deals/",
        },
        PlatformType.TWITTER: {
            "followers": "https://x.com/followers",
            "analytics": "https://analytics.twitter.com/",
        },
        PlatformType.LINKEDIN: {
            "connections": "https://www.linkedin.com/mynetwork/invite-connect/connections/",
            "analytics": "https://www.linkedin.com/analytics/",
        },
    }

    platform_config = SCRAPE_CONFIGS.get(platform, {})
    target_url = request.target_url or platform_config.get(request.data_type)

    if not target_url:
        raise HTTPException(status_code=400, detail=f"No scrape target configured for {platform.value}/{request.data_type}")

    try:
        from playwright.async_api import async_playwright
        import asyncio

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = await browser.new_context(
                storage_state=cred.session_data,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()

            await page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(3)

            # Extract page content for AI processing
            page_text = await page.inner_text("body")
            page_title = await page.title()

            # Use AI to structure the scraped data
            from app.agents.base import get_llm, safe_parse_json

            llm = get_llm("gemini-flash", temperature=0.1)
            if llm:
                extraction_prompt = f"""Extract structured data from this {platform.value} page.
Data type requested: {request.data_type}
Page title: {page_title}
Page content (first 5000 chars):
{page_text[:5000]}

Return a JSON object with:
- "items": array of extracted data items (contacts, deals, followers, etc.)
- "total_count": estimated total items on the page
- "summary": brief summary of what was found

Return ONLY valid JSON."""

                response = await llm.ainvoke(extraction_prompt)
                extracted = safe_parse_json(response.content) or {"items": [], "summary": "AI extraction failed to parse"}
            else:
                extracted = {"items": [], "summary": page_text[:1000], "raw": True}

            # Update session
            new_state = await context.storage_state()
            cred.session_data = new_state
            cred.last_action_at = datetime.utcnow()
            await db.commit()

            await browser.close()

            logger.info("browser_scrape_success", platform=platform.value, data_type=request.data_type)

            return {
                "success": True,
                "platform": platform.value,
                "data_type": request.data_type,
                "data": extracted,
            }

    except Exception as e:
        logger.error("browser_scrape_error", platform=platform.value, error=str(e))
        raise HTTPException(status_code=500, detail=f"Browser scraping failed: {str(e)[:200]}")
