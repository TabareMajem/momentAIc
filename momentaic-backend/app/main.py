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
    
    yield
    
    # Shutdown
    logger.info("Shutting down MomentAIc API")
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
