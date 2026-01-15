"""
MomentAIc API Application
The Entrepreneur Operating System
"""

from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog
import time

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
    
    # === SUPEROS: Proactive Heartbeat (The 10 Elon Musks) ===
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from app.services.activity_stream import activity_stream
    
    scheduler = AsyncIOScheduler()
    
    async def run_proactive_agent(agent_name: str, task_description: str, agent_func):
        """
        Wrapper to run a proactive agent task and report to Command Center.
        """
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select
        from app.models.startup import Startup
        
        # Report start
        activity_id = await activity_stream.report_start(agent_name, task_description)
        
        async with AsyncSessionLocal() as db:
            try:
                # 1. Get relevant startups (Active & Growth/God Mode for heavy agents)
                # For MVP, we run for all, but in prod we'd filter by tier
                result = await db.execute(select(Startup).limit(100))
                startups = result.scalars().all()
                
                await activity_stream.report_progress(activity_id, f"Targeting {len(startups)} startups...", 10)
                
                processed = 0
                for i, startup in enumerate(startups):
                    # Update progress
                    progress = 10 + int((i / len(startups)) * 80)
                    await activity_stream.report_progress(
                        activity_id, 
                        f"Processing {startup.name}...", 
                        progress
                    )
                    
                    # Execute Agent Logic
                    try:
                        # Context construction
                        context = {
                            "startup_id": str(startup.id),
                            "name": startup.name,
                            "description": startup.description,
                            "industry": startup.industry
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
        """Generate daily content ideas"""
        from app.agents.content_agent import content_agent
        from app.models.growth import ContentPlatform
        
        # Generate 3 ideas for LinkedIn
        await content_agent.generate_ideas(startup_context=context, count=3)

    async def run_sdr_agent(startup, context):
        """Draft outreach for new leads"""
        # In a real impl, this would query triggers or new leads
        pass 

    async def run_competitor_intel(startup, context):
        """Scan competitors"""
        from app.agents.competitor_intel_agent import competitor_intel_agent
        # Trigger scan
        pass

    async def run_growth_hacker(startup, context):
        """Weekly growth report"""
        from app.agents.growth_hacker_agent import growth_hacker_agent
        # Generate report
        pass

    # --- SCHEDULE ---
    
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

    # 6. Morning Brief (The 'AI CEO' Report): Daily at 6:00 AM UTC
    @scheduler.scheduled_job(CronTrigger(hour=6, minute=0), id='morning_brief')
    async def schedule_morning_brief():
        from app.services.morning_brief import morning_brief_service
        await morning_brief_service.generate_daily_brief()

    scheduler.start()
    logger.info("🚀 SuperOS Heartbeat Scheduler: ACTIVE (runs every 60 min)")
    # === END SUPEROS ===
    
    yield
    
    # Shutdown
    logger.info("Shutting down MomentAIc API")
    scheduler.shutdown(wait=False)
    await close_db()


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
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "docs": f"{settings.api_v1_prefix}/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        workers=settings.workers if settings.is_production else 1,
    )
