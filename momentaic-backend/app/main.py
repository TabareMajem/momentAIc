"""
MomentAIc API Application
The Entrepreneur Operating System
"""

from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog
import time
import math

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1.router import api_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer() if settings.is_production else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting MomentAIc API", env=settings.app_env)
    await init_db()
    logger.info("Database initialized")

    # === MCP SYSTEM: Connect to Protocol Servers ===
    from app.services.mcp_client import mcp_service
    import os
    
    cwd = os.getcwd()
    mcp_status = {}
    
    # 1. Browser Server
    try:
        browser_script = os.path.join(cwd, "servers/browser/server.py")
        if os.path.exists(browser_script):
            await mcp_service.connect_stdio_server(
                name="browser",
                command="python3",
                args=[browser_script],
                env={**os.environ}
            )
            mcp_status["browser"] = "connected"
        else:
            mcp_status["browser"] = "skipped (script not found)"
    except Exception as e:
        mcp_status["browser"] = f"failed: {str(e)[:100]}"
        logger.error("MCP Browser Server failed", error=str(e))
    
    # 2. Google Workspace Server
    try:
        google_script = os.path.join(cwd, "servers/google/server.py")
        if os.path.exists(google_script):
            await mcp_service.connect_stdio_server(
                name="google",
                command="python3",
                args=[google_script],
                env={**os.environ}
            )
            mcp_status["google"] = "connected"
        else:
            mcp_status["google"] = "skipped (script not found)"
    except Exception as e:
        mcp_status["google"] = f"failed: {str(e)[:100]}"
        logger.error("MCP Google Server failed", error=str(e))

    # 3. Postgres Server
    try:
        pg_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        await mcp_service.connect_stdio_server(
            name="postgres",
            command="npx",
            args=["-y", "@zeddotdev/postgres-context-server", pg_url],
            env={**os.environ}
        )
        mcp_status["postgres"] = "connected"
    except Exception as e:
        mcp_status["postgres"] = f"failed: {str(e)[:100]}"
        logger.error("MCP Postgres Server failed", error=str(e))

    # 4. Filesystem Server
    try:
        project_root = cwd 
        await mcp_service.connect_stdio_server(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", project_root],
            env={**os.environ}
        )
        mcp_status["filesystem"] = "connected"
    except Exception as e:
        mcp_status["filesystem"] = f"failed: {str(e)[:100]}"
        logger.error("MCP Filesystem Server failed", error=str(e))
    
    logger.info("MCP Server Status", **mcp_status)
    
    # === SUPEROS: Proactive Heartbeat (The 10 Elon Musks) ===
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from app.services.activity_stream import activity_stream
    
    scheduler = AsyncIOScheduler()
    
    async def run_proactive_agent(agent_name: str, task_description: str, agent_func):
        """
        Wrapper to run a proactive agent task and report to Command Center.
        Now with autonomy-level awareness.
        """
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.startup import Startup
        from app.models.autonomy import StartupAutonomySettings, AutonomyLevel
        
        # Report start
        activity_id = await activity_stream.report_start(agent_name, task_description)
        
        async with AsyncSessionLocal() as db:
            try:
                # Get startups with their autonomy settings (only non-paused)
                result = await db.execute(
                    select(Startup)
                    .options(selectinload(Startup.autonomy_settings))
                    .limit(100)
                )
                startups = result.scalars().all()
                
                await activity_stream.report_progress(activity_id, f"Targeting {len(startups)} startups...", 10)
                
                processed = 0
                for i, startup in enumerate(startups):
                    # Check autonomy settings - skip if paused or missing
                    settings = startup.autonomy_settings
                    if settings and settings.is_paused:
                        logger.debug("Skipping paused startup", startup_id=str(startup.id))
                        continue
                    
                    # Update progress
                    progress = 10 + int((i / len(startups)) * 80)
                    await activity_stream.report_progress(
                        activity_id, 
                        f"Processing {startup.name}...", 
                        progress
                    )
                    
                    # Execute Agent Logic
                    try:
                        # Context construction with autonomy level
                        autonomy_level = settings.global_level if settings else 1  # Default to Advisor
                        context = {
                            "startup_id": str(startup.id),
                            "name": startup.name,
                            "description": startup.description,
                            "industry": startup.industry,
                            "autonomy_level": autonomy_level,  # NEW: Pass autonomy level
                        }
                        
                        # Call the agent calculation
                        # Note: We await the function passed in
                        await agent_func(startup, context)
                        
                    except Exception as e:
                        logger.error(f"Error for {startup.name}", agent=agent_name, error=str(e))
                    
                    processed += 1
                
                await activity_stream.report_complete(activity_id, {"processed": processed})
                
            except Exception as e:
                logger.error("Proactive run failed", agent=agent_name, error=str(e))
                await activity_stream.report_error(activity_id, str(e))

    # --- AGENT TASKS ---

    async def run_content_agent(startup, context):
        """Generate daily content ideas (GrowthSuperAgent)"""
        from app.agents.growth import growth_agent
        
        # Mission: Viral Campaign / Content
        await growth_agent.run(
            mission="viral_campaign", 
            target={"topic": "industry_trends"}, 
            user_id=str(startup.owner_id)
        )

    async def run_sdr_agent(startup, context):
        """Draft outreach for new leads (GrowthSuperAgent)"""
        from app.agents.growth import growth_agent
        
        # Mission: Sales Hunt
        await growth_agent.run(
            mission="sales_hunt",
            target={"criteria": "new_leads"},
            user_id=str(startup.owner_id)
        )

    async def run_competitor_intel(startup, context):
        """Scan competitors (GrowthSuperAgent)"""
        from app.agents.growth import growth_agent
        
        # Mission: Competitor Intel (routed via viral/market mission)
        await growth_agent.run(
            mission="market_scan",
            target={"competitors": "top_3"},
            user_id=str(startup.owner_id)
        )

    async def run_growth_hacker(startup, context):
        """Weekly growth report (GrowthSuperAgent)"""
        from app.agents.growth import growth_agent
        
        # Mission: Growth Audit
        await growth_agent.run(
            mission="growth_audit",
            target={"scope": "weekly_metrics"},
            user_id=str(startup.owner_id)
        )

    # --- SCHEDULE ---
    
    # 0. Morning Brief: Daily at 6 AM (Ghost Board)
    async def run_morning_brief(startup, context):
        from app.agents.morning_brief_agent import morning_brief_agent
        await morning_brief_agent.generate_brief(str(startup.id), context)

    @scheduler.scheduled_job(CronTrigger(hour=6, minute=0), id='daily_morning_brief')
    async def schedule_morning_brief():
        await run_proactive_agent("MorningBriefAgent", "Compiling daily Morning Brief & Mentor Note", run_morning_brief)

    # 1. ContentAgent: Daily at 6 AM
    @scheduler.scheduled_job(CronTrigger(hour=6, minute=0), id='daily_content')
    async def schedule_content():
        await run_proactive_agent("ContentAgent", "Generating daily content ideas", run_content_agent)

    # 2. SDRAgent: Daily at 9 AM
    @scheduler.scheduled_job(CronTrigger(hour=9, minute=0), id='daily_sdr')
    async def schedule_sdr():
        await run_proactive_agent("SDRAgent", "Drafting outreach for new leads", run_sdr_agent)

    # 3. CompetitorIntel: Daily at 2 PM
    @scheduler.scheduled_job(CronTrigger(hour=14, minute=0), id='daily_competitor')
    async def schedule_competitor():
        await run_proactive_agent("CompetitorIntelAgent", "Scanning competitor landscape", run_competitor_intel)

    # 4. GrowthHacker: Mondays at 8 AM
    @scheduler.scheduled_job(CronTrigger(day_of_week='mon', hour=8, minute=0), id='weekly_growth')
    async def schedule_growth():
        await run_proactive_agent("GrowthHackerAgent", "Generating weekly growth report", run_growth_hacker)

    # 5. Heartbeat (Trigger Engine): Every hour (Backup)
    @scheduler.scheduled_job(CronTrigger(minute=0), id='hourly_heartbeat')
    async def schedule_heartbeat():
         # Keep the original trigger engine running too
        from app.core.database import AsyncSessionLocal
        from app.triggers.engine import evaluate_triggers
        from sqlalchemy import select
        from app.models.startup import Startup
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Startup).limit(100))
            for startup in result.scalars().all():
                await evaluate_triggers(db, str(startup.id))

    # 6. Morning Brief (using scheduler.py's autonomy-aware implementation)
    from app.scheduler import run_morning_briefing, run_trend_scan
    
    @scheduler.scheduled_job(CronTrigger(hour=6, minute=0), id='morning_brief')
    async def schedule_morning_brief():
        await run_morning_briefing()

    # 6b. Executive Assistant (The "Proactive Agent"): Daily at 8:00 AM UTC
    # Checks MCP tools (Calendar, Email, DB, Files) and emails a briefing
    @scheduler.scheduled_job(CronTrigger(hour=8, minute=0), id='executive_briefing')
    async def schedule_executive_briefing():
        from app.services.executive_assistant import executive_assistant
        await executive_assistant.run_daily_briefing()

    # 6c. "Hair on Fire" Daemon (Crisis Monitor): Every 1 minute
    @scheduler.scheduled_job(IntervalTrigger(minutes=1), id='hair_on_fire_daemon')
    async def schedule_hair_on_fire():
        from app.services.executive_assistant import executive_assistant
        await executive_assistant.check_urgent_comms()

    # 6d. Trend Scan (from scheduler.py — autonomy-aware): Every hour
    @scheduler.scheduled_job(IntervalTrigger(hours=1), id='trend_scan')
    async def schedule_trend_scan():
        await run_trend_scan()

    # 7. OpenClaw Heartbeat Engine: Every 30 minutes
    @scheduler.scheduled_job(IntervalTrigger(minutes=30), id='openclaw_heartbeat')
    async def schedule_openclaw_heartbeat():
        """Run all configured agent heartbeats (OpenClaw-inspired autonomy)"""
        from app.services.heartbeat_engine import run_all_heartbeats
        await run_all_heartbeats()

    # 8. AI Character Factory Heartbeat: ENABLED
    # Runs to evaluate the status of deployed characters
    @scheduler.scheduled_job(IntervalTrigger(minutes=60), id='character_heartbeat')
    async def schedule_character_heartbeat():
        """Run the Character Factory heartbeat"""
        from app.services.heartbeat_engine import run_heartbeat_for_agent, load_heartbeat_configs
        
        configs = load_heartbeat_configs()
        char_config = next((c for c in configs if c.get("agent_id") == "character_agent"), None)
        
        if char_config:
            await run_heartbeat_for_agent(char_config)

    scheduler.start()
    logger.info("🚀 SuperOS Heartbeat Scheduler: ACTIVE", jobs=len(scheduler.get_jobs()))
    logger.info("🧬 OpenClaw Heartbeat Engine: ACTIVE (runs every 30 min)")
    # === END SUPEROS ===
    
    yield
    
    # Shutdown
    logger.info("Shutting down MomentAIc API")
    scheduler.shutdown(wait=False)
    await close_db()
    await mcp_service.cleanup()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="The Entrepreneur Operating System - AI-Native Startup Management",
    version="1.0.0",
    docs_url="/api/v1/docs" if not settings.is_production else None,
    redoc_url="/api/v1/redoc" if not settings.is_production else None,
    openapi_url="/api/v1/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Redis-backed rate limiting middleware.
    Limits standard API requests based on settings.rate_limit_requests per settings.rate_limit_window.
    """
    # Skip rate limiting for static files, docs, health, and webhooks
    path = request.url.path
    if path.startswith(("/static", "/assets", "/api/v1/health", "/api/v1/docs", "/api/v1/redoc", "/api/stripe/webhook", "/api/v1/billing/webhook")):
        return await call_next(request)
        
    # Get client IP (fallback to 127.0.0.1 if not behind proxy)
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    # Optional: authenticated user rate limiting is better, but IP is a generic fallback
    # In a full production app, you'd extract the JWT user ID here if present.
    limit_key = f"rate_limit:{client_ip}"
    
    try:
        import redis.asyncio as aioredis
        redis_client = aioredis.from_url(settings.redis_url or "redis://localhost:6379/0", decode_responses=True)
        
        # Determine current window bucket (e.g., current minute)
        current_time = int(time.time())
        window_start = current_time - (current_time % settings.rate_limit_window)
        bucket_key = f"{limit_key}:{window_start}"
        
        async with redis_client.pipeline(transaction=True) as pipe:
            # Increment and set expiry concurrently
            pipe.incr(bucket_key)
            pipe.expire(bucket_key, settings.rate_limit_window * 2)
            results = await pipe.execute()
            
            request_count = results[0]
            
            if request_count > settings.rate_limit_requests:
                logger.warning("Rate limit exceeded", ip=client_ip, path=path, count=request_count, limit=settings.rate_limit_requests)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "error": "Too many requests",
                        "detail": f"Rate limit exceeded. Maximum {settings.rate_limit_requests} requests per {settings.rate_limit_window} seconds."
                    },
                    headers={"Retry-After": str(settings.rate_limit_window)}
                )
        
        await redis_client.aclose()
    except ImportError:
        # Ignore if aioredis isn't installed (tests/dev)
        pass
    except Exception as e:
        # Fail open if Redis is down
        logger.warning("Rate limiter bypass (Redis error)", error=str(e))

    return await call_next(request)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    # Skip logging for health checks
    if request.url.path == "/api/v1/health":
        return await call_next(request)
    
    logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2),
    )
    
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    # Convert errors to JSON-serializable format
    errors = []
    for error in exc.errors():
        serializable_error = {}
        for key, value in error.items():
            if key == "ctx":
                # Context often contains non-serializable objects (like Exceptions)
                continue
            
            if key == "loc":
                # Preserve location path, but stringify elements just in case
                serializable_error[key] = [str(x) for x in value]
                continue
                
            if isinstance(value, (str, int, float, bool, type(None))):
                serializable_error[key] = value
            else:
                # Stringify anything else to be safe
                serializable_error[key] = str(value)
        errors.append(serializable_error)
    
    logger.warning("Validation error", errors=errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "detail": errors,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error("Unhandled exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else None,
        },
    )


# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Stripe Webhook Alias (Fix for Misconfigured URL)
# Redirect /api/stripe/webhook to /api/v1/billing/webhook
# Using 307 Temporary Redirect to preserve POST method and body
from fastapi.responses import RedirectResponse

@app.post("/api/stripe/webhook", include_in_schema=False)
async def legacy_stripe_webhook_redirect(request: Request):
    return RedirectResponse(url="/api/v1/billing/webhook", status_code=307)


# Mount static files (for agent screenshots)
from fastapi.staticfiles import StaticFiles
import os

static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint — checks real dependencies"""
    checks = {}
    overall = "healthy"
    
    # Check Database
    try:
        from app.core.database import async_session_maker
        from sqlalchemy import text
        async with async_session_maker() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"error: {str(e)[:100]}"
        overall = "degraded"
    
    # Check Redis
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.redis_url or "redis://localhost:6379")
        await r.ping()
        await r.aclose()
        checks["redis"] = "connected"
    except Exception as e:
        checks["redis"] = f"error: {str(e)[:100]}"
        overall = "degraded"
    
    # Check LLM availability (lightweight — just verify key exists)
    checks["llm"] = "configured" if settings.google_api_key else "no_api_key"
    if not settings.google_api_key:
        overall = "degraded"
    
    # Check MCP servers
    from app.services.mcp_client import mcp_service
    mcp_servers = list(mcp_service._sessions.keys())
    checks["mcp_servers"] = mcp_servers if mcp_servers else "none_connected"
    
    return {
        "status": overall,
        "app": settings.app_name,
        "version": "5.0.0",
        "environment": settings.app_env,
        "checks": checks,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "docs": f"{settings.api_v1_prefix}/docs",
        "health": f"{settings.api_v1_prefix}/health",
        "llms": "/llms.txt",
    }

@app.get("/llms.txt", include_in_schema=False)
async def root_llms_txt():
    """Serve llms.txt at root"""
    from fastapi import Response
    from app.services.llm_context import llm_context_service
    content = llm_context_service.generate_llms_txt()
    return Response(content=content, media_type="text/plain")

@app.get("/llms-full.txt", include_in_schema=False)
async def root_llms_full_txt():
    """Serve llms-full.txt at root"""
    from fastapi import Response
    from app.services.llm_context import llm_context_service
    content = llm_context_service.generate_llms_full_txt()
    return Response(content=content, media_type="text/plain")



# ==========================================
# FRONTEND SERVING (SPA)
# ==========================================
# Must be AFTER API routes to avoid conflict

# 1. Mount assets (JS, CSS)
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "momentaic-frontend", "dist")
assets_dir = os.path.join(frontend_dist, "assets")

if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# 2. Mount other static files in root of dist (favicon, robots, etc)
# We can't mount root "/" directly or it blocks API. 
# So we serve specific files or let the catch-all handle index.html

# 3. SPA Catch-all
from fastapi.responses import FileResponse

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """
    Serve the frontend Svelte/React app.
    If file exists in dist, serve it.
    Otherwise serve index.html for client-side routing.
    """
    # Skip API routes just in case (though they should be matched first if defined above)
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"message": "Not Found"})

    # Check if file exists in dist (e.g. favicon.png, logo.png)
    file_path = os.path.join(frontend_dist, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
        
    # Fallback to index.html for SPA routing
    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return JSONResponse(status_code=404, content={"message": "Frontend not built"})
