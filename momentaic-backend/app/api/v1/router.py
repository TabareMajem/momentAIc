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
    integrations,
    triggers,
    mcp_tools,
    import_flows,
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

# Integrations Hub
api_router.include_router(
    integrations.router,
    prefix="/integrations",
    tags=["Integrations"],
)

# Proactive Triggers
api_router.include_router(
    triggers.router,
    prefix="/triggers",
    tags=["Proactive Triggers"],
)

# MCP Tools (AI orchestration)
api_router.include_router(
    mcp_tools.router,
    tags=["MCP Tools"],
)

# Traction Score (Performance ranking)
api_router.include_router(
    mcp_tools.traction_router,
    tags=["Traction Score"],
)

# Leaderboard (Public rankings)
api_router.include_router(
    mcp_tools.leaderboard_router,
    tags=["Leaderboard"],
)

# Community (Showcase, matching)
api_router.include_router(
    mcp_tools.community_router,
    tags=["Community"],
)

# Deep Research
api_router.include_router(
    mcp_tools.research_router,
    tags=["Deep Research"],
)

# Cross-Platform SSO (AgentForgeai.com <-> MomentAIc)
from app.api.v1.endpoints import sso
api_router.include_router(
    sso.router,
    tags=["Cross-Platform SSO"],
)

# Admin Panel (Superuser only)
from app.api.v1.endpoints import admin
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin Panel"],
)

# Investment Dashboard
from app.api.v1.endpoints import investment
api_router.include_router(
    investment.router,
    tags=["Investment"],
)

# Viral Referral System
from app.api.v1.endpoints import referrals
api_router.include_router(
    referrals.router,
    prefix="/referrals",
    tags=["Referrals"],
)

# Ambassador Program
from app.api.v1.endpoints import ambassadors
api_router.include_router(
    ambassadors.router,
    prefix="/ambassadors",
    tags=["Ambassadors"],
)

# Viral Campaign Engine (Soul Cards, etc.)
from app.api.v1.endpoints import viral
api_router.include_router(
    viral.router,
    prefix="/viral",
    tags=["Viral Campaigns"],
)

# Activity Stream (Live Matrix)
from app.api.v1.endpoints import events
api_router.include_router(
    events.router,
    prefix="/events",
    tags=["Activity Stream"],
)

# Onboarding Wizard (60-Second Result)
from app.api.v1.endpoints import onboarding
api_router.include_router(
    onboarding.router,
    prefix="/onboarding",
    tags=["Onboarding"],
)

# GitHub Import
api_router.include_router(
    import_flows.router,
    prefix="/startups/import",
    tags=["Import Flows"],
)

# Marketplace
from app.api.v1.endpoints import marketplace
api_router.include_router(
    marketplace.router,
    tags=["Marketplace"],
)

# QA & Testing
from app.api.v1.endpoints import qa
api_router.include_router(
    qa.router,
    tags=["QA & Testing"],
)

# Launch Strategy
from app.api.v1.endpoints import launch
api_router.include_router(
    launch.router,
    tags=["Launch Strategy"],
)

# War Room (Admin Only - Global Launch Agents)
from app.api.v1.endpoints import war_room
api_router.include_router(
    war_room.router,
    tags=["War Room"],
)

# Free Roast (Public Viral Hook)
from app.api.v1.endpoints import free_roast
api_router.include_router(
    free_roast.router,
    tags=["Free Roast"],
)

# Growth Hacking Tools (Admin Only)
from app.api.v1.endpoints import growth_hack
api_router.include_router(
    growth_hack.router,
    tags=["Growth Hacking"],
)

# The Vault (Day 1 Deliverables)
from app.api.v1.endpoints import vault
api_router.include_router(
    vault.router,
    prefix="/vault",
    tags=["The Vault"],
)

# Proactive Actions (Morning Brief)
from app.api.v1.endpoints import actions
api_router.include_router(
    actions.router,
    prefix="/actions",
    tags=["Proactive Actions"],
)

# Innovator Lab (Deep Research, War Gaming, Growth)
from app.api.v1.endpoints import innovator
api_router.include_router(
    innovator.router,
    prefix="/innovator",
    tags=["Innovator Lab"],
)

# Notifications (Web Push)
from app.api.v1.endpoints import notifications
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
)

# Infinite Content Loop (Admin)
from app.api.v1.endpoints import content_loop
api_router.include_router(
    content_loop.router,
    prefix="/admin/loops",
    tags=["Infinite Content Loop"],
)
