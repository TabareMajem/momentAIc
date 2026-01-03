"""
Launch Executor Agent
Manus AI-style autonomous browser execution for product submissions
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import structlog
import asyncio
import uuid
import os

from app.agents.base import get_llm
from app.data.platform_actions import (
    get_platform_action,
    get_all_platform_ids,
    get_easy_platforms,
    map_product_to_fields,
    PlatformAction,
)

logger = structlog.get_logger()


class SubmissionStatus(str, Enum):
    """Status of a platform submission"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    DRY_RUN = "dry_run"


class ExecutionMode(str, Enum):
    """Execution mode"""
    DRY_RUN = "dry_run"  # Preview without submitting
    EXECUTE = "execute"  # Actually submit


@dataclass
class SubmissionResult:
    """Result of a single platform submission"""
    platform_id: str
    platform_name: str
    status: SubmissionStatus
    screenshot_path: Optional[str] = None
    error: Optional[str] = None
    form_data: Dict[str, str] = field(default_factory=dict)
    submitted_at: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform_id": self.platform_id,
            "platform_name": self.platform_name,
            "status": self.status.value,
            "screenshot": self.screenshot_path,
            "error": self.error,
            "form_data": self.form_data,
            "submitted_at": self.submitted_at,
            "notes": self.notes,
        }


@dataclass
class ExecutionJob:
    """Full execution job state"""
    job_id: str
    status: str  # pending, in_progress, completed, cancelled
    mode: ExecutionMode
    product_info: Dict[str, Any]
    platforms: List[str]
    progress: int = 0
    total: int = 0
    current_platform: Optional[str] = None
    results: List[SubmissionResult] = field(default_factory=list)
    latest_screenshot: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "mode": self.mode.value,
            "product_name": self.product_info.get("name", ""),
            "progress": self.progress,
            "total": self.total,
            "current_platform": self.current_platform,
            "results": [r.to_dict() for r in self.results],
            "latest_screenshot": self.latest_screenshot,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
        }


class LaunchExecutorAgent:
    """
    Launch Executor Agent - Autonomous product submissions
    
    Capabilities:
    - Navigate to submission pages
    - Fill forms with AI-assisted field mapping
    - Submit or preview (dry-run)
    - Capture screenshot proofs
    - Track progress with events
    """
    
    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
        self._active_jobs: Dict[str, ExecutionJob] = {}
    
    async def initialize(self):
        """Initialize headless browser"""
        if self._browser:
            return True
        
        try:
            from playwright.async_api import async_playwright
            
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            self._context = await self._browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )
            self._page = await self._context.new_page()
            
            logger.info("Launch Executor Browser initialized")
            return True
        except ImportError:
            logger.warning("Playwright not installed for executor")
            return False
    
    async def execute_launch(
        self,
        product_info: Dict[str, Any],
        platforms: List[str],
        mode: ExecutionMode = ExecutionMode.DRY_RUN,
        progress_callback: Optional[callable] = None,
    ) -> ExecutionJob:
        """
        Execute product submissions across multiple platforms
        
        Args:
            product_info: Product details (name, tagline, url, description, email)
            platforms: List of platform IDs to submit to
            mode: DRY_RUN or EXECUTE
            progress_callback: Optional callback for progress updates
        """
        # Create job
        job_id = str(uuid.uuid4())[:8]
        job = ExecutionJob(
            job_id=job_id,
            status="in_progress",
            mode=mode,
            product_info=product_info,
            platforms=platforms,
            total=len(platforms),
            started_at=datetime.utcnow().isoformat() + "Z",
        )
        self._active_jobs[job_id] = job
        
        # Initialize browser
        if not await self.initialize():
            job.status = "failed"
            job.error = "Browser initialization failed"
            return job
        
        # Process each platform
        for i, platform_id in enumerate(platforms):
            job.current_platform = platform_id
            job.progress = i
            
            if progress_callback:
                await progress_callback(job.to_dict())
            
            try:
                result = await self._submit_to_platform(
                    platform_id=platform_id,
                    product_info=product_info,
                    mode=mode,
                )
                job.results.append(result)
                
            except Exception as e:
                logger.error(f"Platform submission failed: {platform_id}", error=str(e))
                job.results.append(SubmissionResult(
                    platform_id=platform_id,
                    platform_name=platform_id,
                    status=SubmissionStatus.FAILED,
                    error=str(e),
                ))
            
            # Small delay between platforms
            await asyncio.sleep(1)
        
        # Complete job
        job.status = "completed"
        job.progress = job.total
        job.current_platform = None
        job.completed_at = datetime.utcnow().isoformat() + "Z"
        
        if progress_callback:
            await progress_callback(job.to_dict())
        
        return job
    
    async def _submit_to_platform(
        self,
        platform_id: str,
        product_info: Dict[str, Any],
        mode: ExecutionMode,
    ) -> SubmissionResult:
        """Submit product to a single platform"""
        
        # Get platform action
        action = get_platform_action(platform_id)
        if not action:
            return SubmissionResult(
                platform_id=platform_id,
                platform_name=platform_id,
                status=SubmissionStatus.SKIPPED,
                error=f"No action mapping for platform: {platform_id}",
            )
        
        result = SubmissionResult(
            platform_id=platform_id,
            platform_name=action.name,
            status=SubmissionStatus.IN_PROGRESS,
        )
        
        try:
            # 1. Navigate to submission page
            logger.info(f"Navigating to {action.name}", url=action.submit_url)
            response = await self._page.goto(action.submit_url, wait_until="networkidle", timeout=30000)
            
            if not response or not response.ok:
                result.status = SubmissionStatus.FAILED
                result.error = f"Failed to load page: HTTP {response.status if response else 'No response'}"
                return result
            
            # 2. Wait for page to stabilize
            await asyncio.sleep(1)
            
            # 3. Fill form fields
            field_mapping = map_product_to_fields(product_info, action.fields)
            result.form_data = field_mapping
            
            filled_count = 0
            for selector, value in field_mapping.items():
                if not value:
                    continue
                
                try:
                    # Try multiple selector strategies
                    selectors = selector.split(", ")
                    element = None
                    
                    for sel in selectors:
                        try:
                            element = await self._page.wait_for_selector(sel.strip(), timeout=3000)
                            if element:
                                break
                        except:
                            continue
                    
                    if element:
                        # Clear and fill
                        await element.click()
                        await element.fill("")
                        await element.fill(value)
                        filled_count += 1
                        logger.debug(f"Filled field", selector=selector[:50], value_len=len(value))
                    else:
                        logger.warning(f"Field not found", selector=selector[:50])
                        
                except Exception as e:
                    logger.warning(f"Failed to fill field", selector=selector[:50], error=str(e))
            
            result.notes = f"Filled {filled_count}/{len([v for v in field_mapping.values() if v])} fields"
            
            # 4. Capture screenshot (before submit)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"launch_{platform_id}_{timestamp}.png"
            static_dir = "/root/momentaic/momentaic-backend/app/static/screenshots"
            screenshot_path = f"{static_dir}/{filename}"
            
            # Ensure directory exists
            os.makedirs(static_dir, exist_ok=True)
            
            await self._page.screenshot(path=screenshot_path, full_page=False)
            
            # Public URL for frontend
            public_url = f"/static/screenshots/{filename}"
            result.screenshot_path = public_url
            
            # Update job with latest screenshot
            job_id = [k for k, v in self._active_jobs.items() if v.current_platform == platform_id]
            if job_id:
                self._active_jobs[job_id[0]].latest_screenshot = public_url
            
            # 5. Handle submission based on mode
            if mode == ExecutionMode.DRY_RUN:
                result.status = SubmissionStatus.DRY_RUN
                result.notes += " | DRY RUN - No actual submission"
                logger.info(f"Dry run completed for {action.name}")
                
            else:
                # EXECUTE mode - actually submit
                await asyncio.sleep(action.pre_submit_wait / 1000)
                
                # Find and click submit button
                submit_selectors = action.submit_button.split(", ")
                submitted = False
                
                for sel in submit_selectors:
                    try:
                        submit_btn = await self._page.wait_for_selector(sel.strip(), timeout=3000)
                        if submit_btn:
                            await submit_btn.click()
                            submitted = True
                            break
                    except:
                        continue
                
                if not submitted:
                    result.status = SubmissionStatus.FAILED
                    result.error = "Submit button not found"
                    return result
                
                # Wait for response
                await asyncio.sleep(action.post_submit_wait / 1000)
                
                # Check for success indicators
                page_content = await self._page.content()
                success = any(
                    indicator.lower() in page_content.lower()
                    for indicator in action.success_indicators
                    if not indicator.startswith(".")  # Skip CSS selectors for content check
                )
                
                if not success:
                    # Try CSS selectors
                    for indicator in action.success_indicators:
                        if indicator.startswith(".") or indicator.startswith("["):
                            try:
                                elem = await self._page.query_selector(indicator)
                                if elem:
                                    success = True
                                    break
                            except:
                                pass
                
                # Capture post-submit screenshot
                post_filename = f"launch_{platform_id}_after_{timestamp}.png"
                post_screenshot_path = f"{static_dir}/{post_filename}"
                await self._page.screenshot(path=post_screenshot_path, full_page=False)
                
                # Update with post-submit screenshot
                result.screenshot_path = f"/static/screenshots/{post_filename}"
                
                if success:
                    result.status = SubmissionStatus.SUCCESS
                    result.submitted_at = datetime.utcnow().isoformat() + "Z"
                    result.notes += " | Submission successful!"
                else:
                    # Check for error indicators
                    is_error = any(
                        indicator.lower() in page_content.lower()
                        for indicator in action.error_indicators
                        if not indicator.startswith(".")
                    )
                    
                    if is_error:
                        result.status = SubmissionStatus.FAILED
                        result.error = "Error indicator detected on page"
                    else:
                        # Uncertain - mark as success with note
                        result.status = SubmissionStatus.SUCCESS
                        result.notes += " | Submission sent (unconfirmed)"
                
                logger.info(f"Execution completed for {action.name}", status=result.status.value)
        
        except Exception as e:
            result.status = SubmissionStatus.FAILED
            result.error = str(e)
            logger.error(f"Submission error for {platform_id}", error=str(e))
        
        return result
    
    def get_job(self, job_id: str) -> Optional[ExecutionJob]:
        """Get job by ID"""
        return self._active_jobs.get(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        job = self._active_jobs.get(job_id)
        if job and job.status == "in_progress":
            job.status = "cancelled"
            return True
        return False
    
    def get_supported_platforms(self) -> List[Dict[str, Any]]:
        """Get list of supported platforms"""
        platforms = []
        for platform_id in get_all_platform_ids():
            action = get_platform_action(platform_id)
            if action:
                platforms.append({
                    "id": action.platform_id,
                    "name": action.name,
                    "requires_login": action.requires_login,
                    "submit_url": action.submit_url,
                    "notes": action.notes,
                })
        return platforms
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process an execution request from the agent system"""
        
        return {
            "response": """🚀 I'm the Launch Executor Agent - I can autonomously submit your product to multiple platforms!

**Supported Platforms:** 10+ directories (BetaList, Product Hunt, HN, etc.)

**Modes:**
- 🔍 **Dry Run**: Preview form data without submitting
- ⚡ **Execute**: Actually submit to platforms

Use the API endpoint `/launch/execute` to start an execution job.""",
            "agent": "launch_executor",
        }
    
    async def close(self):
        """Cleanup browser resources"""
        if self._browser:
            await self._browser.close()
            self._browser = None
            logger.info("Launch Executor Browser closed")


# Singleton instance
launch_executor_agent = LaunchExecutorAgent()
