"""
API v1 Router
Aggregates all endpoint modules
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    startups,
    signals,
    growth,
    agents,
    workflows,
    billing,
)

api_router = APIRouter()

# Auth endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# Startup management
api_router.include_router(
    startups.router,
    prefix="/startups",
    tags=["Startups"],
)

# Neural Signal Engine
api_router.include_router(
    signals.router,
    prefix="/signals",
    tags=["Neural Signals"],
)

# Growth Engine (CRM + Content)
api_router.include_router(
    growth.router,
    prefix="/growth",
    tags=["Growth Engine"],
)

# Agent Swarm (Chat)
api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["Agent Swarm"],
)

# Agent Forge (Workflows)
api_router.include_router(
    workflows.router,
    prefix="/forge",
    tags=["Agent Forge"],
)

# Billing & Credits
api_router.include_router(
    billing.router,
    prefix="/billing",
    tags=["Billing"],
)
