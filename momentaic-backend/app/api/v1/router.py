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
    social,
    growth_analytics,
    growth_monitor,
    llm_optimization,
    social_ugc,
    a2a,
    characters,
    webhooks,
)

api_router = APIRouter()

# A2A Protocol (Heartbeat + Messages + Pulse + Company DNA)
api_router.include_router(
    a2a.router,
    tags=["A2A Protocol"],
)

# AI Character Factory
api_router.include_router(
    characters.router,
    tags=["AI Character Factory"],
)

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

# Growth Monitor (Pipeline Dashboard)
api_router.include_router(
    growth_monitor.router,
    prefix="/growth",
    tags=["Growth Monitor"],
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

# Webhooks (External System Ingestion)
api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["Webhooks"],
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

# Viral Campaign Engine (Soul Cards, AI Agents, etc.)
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

# Native Social Scheduler (Buffer Killer)
api_router.include_router(
    social.router,
    prefix="/social",
    tags=["Social Scheduler"],
)

# Social OAuth (Connect Accounts)
from app.api.v1.endpoints import social_oauth
api_router.include_router(
    social_oauth.router,
    prefix="/social",
    tags=["Social OAuth"],
)

# Guerrilla Growth (Phase 11) - UGC & Campaigns
api_router.include_router(
    social_ugc.router,
    prefix="/social/ugc",
    tags=["Social UGC & Gorilla"],
)

# Growth Analytics (Phase 12)
api_router.include_router(
    growth_analytics.router,
    prefix="/growth-analytics",
    tags=["Growth Analytics"],
)

# AgentForge Integration (Deep Dive)
from app.api.v1.endpoints import agentforge
api_router.include_router(
    agentforge.router,
    prefix="/integrations/agentforge",
    tags=["AgentForge Integration"],
)

# Admin God Mode (Empire Console)
from app.api.v1.endpoints import admin_god_mode
from app.api.v1.endpoints import swarm  # Add swarm import

api_router.include_router(
    admin_god_mode.router,
    prefix="/admin/god-mode",
    tags=["Admin Ecosystem"],
)

api_router.include_router(
    swarm.router,
    prefix="/admin/swarm",
    tags=["Admin Swarm"],
)

# General User Strategy (Empire Features)
from app.api.v1.endpoints import strategy
api_router.include_router(
    strategy.router,
    prefix="/strategy",
    tags=["Strategy & Empire"],
)

# Nexus Synergy
from app.api.v1.endpoints import nexus
api_router.include_router(
    nexus.router,
    prefix="/admin/synergy",
    tags=["Admin Synergy"],
)

# Magic URL (Project PHOENIX)
from app.api.v1.endpoints import magic_url
api_router.include_router(
    magic_url.router,
    prefix="/onboarding",
    tags=["Magic Onboarding"],
)

# Deployment Webhooks (Vercel/Netlify)
from app.api.v1.endpoints import deployment_webhooks
api_router.include_router(
    deployment_webhooks.router,
    prefix="/webhooks",
    tags=["Deployment Webhooks"],
)

# Voice Agents (Qwen3)
from app.api.v1.endpoints import voice
api_router.include_router(
    voice.router,
    prefix="/voice",
    tags=["Voice Agents"],
)

# LLM Optimization (Agent SEO)
api_router.include_router(
    llm_optimization.router,
    prefix="/llm-context",
    tags=["LLM Optimization"],
)

# Autonomy Settings (Proactive Agent Control)
from app.api.v1.endpoints import autonomy
api_router.include_router(
    autonomy.router,
    prefix="/startups",
    tags=["Autonomy Settings"],
)

# Google Analytics OAuth (Proactive Analytics)
from app.api.v1.endpoints import google_analytics
api_router.include_router(
    google_analytics.router,
    prefix="/integrations",
    tags=["Google Analytics"],
)

# Operations Center (Finance & Legal)
from app.api.v1.endpoints import operations
api_router.include_router(
    operations.router,
    prefix="/operations",
    tags=["Operations Center"],
)

# Product Factory (PM, Design, Tech)
from app.api.v1.endpoints import product
api_router.include_router(
    product.router,
    prefix="/product",
    tags=["Product Factory"],
)

# OpenClaw Headless Browser Proxy
from app.api.v1 import openclaw
api_router.include_router(
    openclaw.router,
    prefix="/openclaw",
    tags=["OpenClaw"],
)

# AstroTurf Community GTM Agent
from app.api.v1 import astroturf
api_router.include_router(
    astroturf.router,
    prefix="/astroturf",
    tags=["AstroTurf GTM"],
)

# Synthetic Call Center Voice Webhooks
from app.api.v1.endpoints import voice_webhooks
api_router.include_router(
    voice_webhooks.router,
    prefix="/voice/webhooks",
    tags=["Voice Webhooks"],
)

# AgentForge / Yokaizen Core Integrations
from app.api.v1.integrations import yokaizen
api_router.include_router(
    yokaizen.router,
    prefix="/integrations/yokaizen",
    tags=["Yokaizen"],
)

# Global Multilingual Campaign
from app.api.v1.endpoints import global_campaign
api_router.include_router(
    global_campaign.router,
    prefix="/campaigns/global",
    tags=["Global Campaign"],
)
