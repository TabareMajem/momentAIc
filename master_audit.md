# MomentAIc Ecosystem: Master Audit Document

## 1. Backend Infrastructure Audit

### 1.1 AI Agents Registry (`app/agents/`)
The system contains a massive Swarm of 50+ specialized agents designed for different aspects of business scaling and automation.
- **Core Operating Agents**: `startup_brain.py`, `empire_strategist.py`, `success_protocol.py`
- **Growth & Marketing**: `growth_hacker_agent.py`, `marketing_agent.py`, `viral_campaign_agent.py`, `viral_content_agent.py`, `sdr_agent.py`, `acquisition_agent.py`
- **Product & Tech**: `tech_lead_agent.py`, `product_pm_agent.py`, `devops_agent.py`, `qa_tester_agent.py`, `design_agent.py`, `integration_builder_agent.py`
- **Operations & Finance**: `finance_cfo_agent.py`, `hr_operations_agent.py`, `legal_counsel_agent.py`, `dealmaker_agent.py`
- **Specialized / Specialized Avatars**: `elon_musk` (`musk_enforcer_agent.py`), `nolan_agent.py`
- **Outreach & Network**: `ambassador_agent.py`, `vc_headhunter_agent.py`, `kol_headhunter_agent.py`
- **Analysis & Research**: `deep_research_agent.py`, `data_analyst_agent.py`, `competitor_intel_agent.py`
- **Execution & Orchestration**: `chain_executor.py`, `launch_executor_agent.py`, `launch_strategist_agent.py`
- **Onboarding & Coaching**: `onboarding_coach_agent.py`, `onboarding_genius.py`
- **Content Factories**: `character_factory_agent.py`, `manga_agent.py`, `localization_architect_agent.py`

### 1.2 Core Services (`app/services/`)
The platform is powered by a robust modular service architecture:
- **Execution Engines**: `execution_maestro.py`, `heartbeat_engine.py`, `scheduler.py`
- **Growth Loops & Viral Mechanics**: `viral_growth_engine.py`, `growth_loop.py`, `astroturf_service.py`, `ugc_pipeline.py`, `community_showcase.py`
- **Data & Intelligence**: `agent_memory_service.py`, `gemini_service.py`, `google_research.py`, `live_data_service.py`, `kol_research.py`, `instant_analysis.py`
- **External Interfaces**: `mcp_client.py` (Model Context Protocol), `browser_worker.py`, `openclaw_service.py`, `github_service.py`, `twilio_service.py`
- **Communication & Delivery**: `email_service.py`, `outreach_service.py`, `notification_service.py`, `message_bus.py`, `deliverable_service.py`

### 1.3 Integrations (`app/integrations/`)
The system integrates with a comprehensive suite of external APIs across 30+ service categories:
- **CRM & Sales**: `hubspot.py`, `attio.py`, `clay.py`, `instantly.py`, `crm.py`
- **Marketing & Social**: `twitter.py`, `linkedin.py`, `typefully.py`, `marketing.py`
- **Billing & Affiliate**: `stripe.py`, `payments.py`, `affiliate.py`, `ecommerce.py`, `accounting.py`
- **Communication & Community**: `slack.py`, `gmail.py`, `communication.py`, `community.py`, `support.py`
- **Productivity & Design**: `notion.py`, `productivity.py`, `scheduling.py`, `design.py`, `video.py`
### 1.4 Triggers & Scheduled Tasks
The application employs two independent scheduling systems: **APScheduler** (for in-memory fast loops) and **Celery Beat** (for distributed async tasks).

**APScheduler (`scheduler.py`) Core Loops**:
- `isp_daily_driver` (Daily 8AM UTC): Inevitable Success Protocol execution.
- `isp_weekly_reports` (Weekly Mon 9AM UTC).
- `evaluate_triggers` (Every 5 mins): Metric/time-based evaluation.
- `hourly_hunter` (Every 1 hour): Automated SDR lead generation based on `StartupAutonomySettings`.
- `content_daily_post` (Daily 10AM UTC): Trend discovery & social post scheduling.
- `competitor_weekly_scan` (Weekly Wed 7AM UTC): Competitive intelligence gathering.
- `growth_social_scan` (Every 4 hours): Scans Reddit and other platforms for intent.
- `reddit_sniper_scan` (Every 4 hours): Narrative marketing high-intent replies.
- `morning_brief` (Daily 6AM UTC): Email to founders.
- `qa_weekly_audit` (Weekly Sun 2AM UTC): Automated QA validation.

**Celery Beat (`celery_app.py`)**:
- `calculate-daily-signals`: Analyzes PMF and velocity metrics.
- `publish-scheduled-content` (Every 5 mins).
### 1.5 Domain Data Models (`app/models/`)
The database schema maps out a complex SaaS / Agency structure:
- **Core Entities**: `user.py`, `startup.py` (projects/companies), `autonomy.py` (startup autonomy settings)
- **Agent Interactivity**: `agent_message.py`, `agent_memory.py`, `conversation.py`, `action_item.py`, `character.py`
- **Growth Engine**: `growth.py`, `viral.py`, `referral.py`, `ambassador.py`, `astroturf.py`, `social.py`
- **Infrastructure**: `integration.py`, `trigger.py`, `workflow.py`, `heartbeat_ledger.py`, `push_subscription.py`, `telecom.py`

---

## 2. Frontend Flows & Admin Features

### 2.1 Onboarding Modalities
The SaaS employs multiple onboarding vectors to match user intent and technical proficiency:
- **`StartupNew.tsx`**: Standard manual project creation.
- **`OnboardingWizard.tsx`**: Guided step-by-step setup.
- **`AutoPilotOnboarding.tsx`**: High-autonomy setup where AI configures the initial architecture.
- **`GeniusOnboarding.tsx`**: Conversational/strategic onboarding for founders requiring architectural guidance.
- **Imports**: `FromBolt.tsx`, `FromLovable.tsx` (Migrating existing projects from other AI-builders).

### 2.2 Super Admin & Control Centers
Powerful interfaces designed for ecosystem governance, mostly gated behind super admin privileges (e.g., `tabaremajem@gmail.com`).
- **`AdminPanel.tsx`**: Global user, subscription, and platform metrics.
- **`TelemetryCore.tsx`**: Real-time system diagnostics and performance tracking.
- **`GlobalCampaign.tsx` & `CampaignCenter.tsx`**: Hubs for managing cross-project marketing pushes.
- **[NEW] `CampaignControlModal.tsx`**: Built-in "Matrix Console" in the Ambassador Dashboard for managing interconnected domains, auto-generating content, and syncing social nodes (TikTok/IG/Twitter).
- **`WarRoomDashboard.tsx`**: Executive-level overview of critical alerts and AI debates.

### 2.3 Core Application Workspaces
- **`Dashboard.tsx`**: The central user hub for a given project/startup.
- **`GrowthEngine.tsx`**: Interface for managing the viral loops and SDR agents.
- **`AgentForge.tsx`**: Visual node-based workflow editor for chaining AI agent behaviors.
- **`TriggersPage.tsx`**: UI to configure automated reactions to platform events.
- **`BusinessPulse.tsx`**: Real-time analytics and metric tracking.
- **`CharacterFactory.tsx`**: Interface for designing specialized AI influencer personas/avatars.
---

## 3. Development Gaps & Work-In-Progress (WIP)

### 3.1 Hardcoded Values & Mock Interfaces
- **Frontend `CharacterFactory.tsx` (L76)**: Currently uses a hardcoded `startup_id` instead of pulling from the active auth context.
- **Backend Integrations (`app/integrations/`)**: Multiple services (Clay, Typefully, Instantly, Attio) fallback to a `'mock_key'` and return synthetic JSON dictionaries if a real API key is not configured for the startup.
- **Super Admin Panel Restrictions**: The new `CampaignControlModal` is currently hardcoded specifically to `tabaremajem@gmail.com` rather than using a generalized RBAC `is_superuser` column.

### 3.2 Unlinked Executions
- **Autonomy Engine Execution (`app/api/v1/endpoints/autonomy.py` / `actions.py`)**: The approval endpoint correctly shifts the `ActionItem` state to `approved`, but the actual execution pipeline contains a `TODO: Execute the approved action` / `(mocked for now)`, meaning the physical action (like sending an email) is not always chained automatically upon approval.
---

## 4. Marketing Materials & Hooks

### Core Value Hooks (Based on Audit)
1. **The Autonomous Business OS**: "Not just another SaaS. A complete neuro-network for your entire business. Replace an entire agency with a multi-agent swarm that debates, decides, and executes."
2. **Infinite Growth Engine**: "Why hire SDRs? Our Hourly Hunter and Sniper Agents scan Reddit, Twitter, and email—pitching your product with narrative-driven context while you sleep."
3. **The Matrix Campaign Control**: "Govern 8 discrete domains from one central command. Push a button, generate a viral hook, and dispatch Sentinels across all social channels instantly."

### Generated Artifacts

#### Output 1: The Autonomous Business OS
![Autonomous Business OS](/root/.gemini/antigravity/brain/eaaa4a7a-8d33-4a12-b01d-322663287d37/momentai_business_os_1771770121942.png)
_Use Case: Main Landing Page Hero Background or OpenGraph meta image._

#### Output 2: The Agent Swarm Network
![Swarm Network](/root/.gemini/antigravity/brain/eaaa4a7a-8d33-4a12-b01d-322663287d37/momentai_swarm_network_1771770065058.png)
_Use Case: "Meet the Team" or Agent Forge promotional graphics._

#### Output 3: Campaign Matrix Control
![Campaign Matrix](/root/.gemini/antigravity/brain/eaaa4a7a-8d33-4a12-b01d-322663287d37/momentai_campaign_matrix_1771770087436.png)
_Use Case: Super Admin / God-Mode feature tier advertising on pricing pages._
