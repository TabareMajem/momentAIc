"""
Success Protocol - The Inevitable Success Playbook
Defines what MUST happen at each startup phase for guaranteed progress
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger()


class StartupPhase(str, Enum):
    """Startup growth phases"""
    IDEA = "idea"
    BUILD = "build"
    LAUNCH = "launch"
    GROW = "grow"
    SCALE = "scale"


@dataclass
class PhaseMetrics:
    """Metrics that define phase completion"""
    name: str
    target: int
    unit: str
    current: int = 0
    
    @property
    def progress(self) -> float:
        return min(100, (self.current / max(self.target, 1)) * 100)
    
    @property
    def is_complete(self) -> bool:
        return self.current >= self.target


@dataclass
class PhaseAction:
    """A required action in a phase"""
    id: str
    name: str
    description: str
    agent_chain: List[str]  # Ordered list of agents to execute
    priority: int  # 1-5, 1 is highest
    estimated_hours: float
    automated: bool = True  # Can this run without human approval?
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_chain": self.agent_chain,
            "priority": self.priority,
            "estimated_hours": self.estimated_hours,
            "automated": self.automated
        }


@dataclass
class PhaseDefinition:
    """Complete definition of a startup phase"""
    phase: StartupPhase
    name: str
    description: str
    entry_metrics: List[PhaseMetrics]  # Metrics to enter this phase
    exit_metrics: List[PhaseMetrics]   # Metrics to graduate to next phase
    required_actions: List[PhaseAction]
    recommended_agents: List[str]
    next_phase: Optional[StartupPhase] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value,
            "name": self.name,
            "description": self.description,
            "entry_metrics": [{"name": m.name, "target": m.target, "unit": m.unit} for m in self.entry_metrics],
            "exit_metrics": [{"name": m.name, "target": m.target, "unit": m.unit} for m in self.exit_metrics],
            "required_actions": [a.to_dict() for a in self.required_actions],
            "recommended_agents": self.recommended_agents,
            "next_phase": self.next_phase.value if self.next_phase else None
        }


# ==================
# THE PLAYBOOK
# ==================

PHASE_DEFINITIONS: Dict[StartupPhase, PhaseDefinition] = {
    StartupPhase.IDEA: PhaseDefinition(
        phase=StartupPhase.IDEA,
        name="Idea Stage",
        description="Validate your concept and find product-market fit signals",
        entry_metrics=[],  # Entry point
        exit_metrics=[
            PhaseMetrics("user_interviews", 10, "interviews"),
            PhaseMetrics("problem_validated", 1, "boolean"),
            PhaseMetrics("target_customer_defined", 1, "boolean")
        ],
        required_actions=[
            PhaseAction(
                id="validate_problem",
                name="Validate the Problem",
                description="Research if this is a real problem worth solving",
                agent_chain=["strategy", "competitor_intel", "data_analyst"],
                priority=1,
                estimated_hours=4,
                automated=True
            ),
            PhaseAction(
                id="define_icp",
                name="Define Ideal Customer Profile",
                description="Create detailed ICP with demographics and pain points",
                agent_chain=["strategy", "sales", "content"],
                priority=1,
                estimated_hours=2,
                automated=True
            ),
            PhaseAction(
                id="find_beta_users",
                name="Find 10 Beta Users",
                description="Identify and reach out to potential beta testers",
                agent_chain=["lead_scraper", "lead_researcher", "sdr"],
                priority=2,
                estimated_hours=8,
                automated=True
            ),
            PhaseAction(
                id="competitor_analysis",
                name="Deep Competitor Analysis",
                description="Map all competitors, their strengths, weaknesses, pricing",
                agent_chain=["competitor_intel", "browser", "data_analyst"],
                priority=2,
                estimated_hours=4,
                automated=True
            ),
        ],
        recommended_agents=["strategy", "onboarding_coach", "competitor_intel"],
        next_phase=StartupPhase.BUILD
    ),
    
    StartupPhase.BUILD: PhaseDefinition(
        phase=StartupPhase.BUILD,
        name="Build Stage",
        description="Create MVP, landing page, and gather initial users",
        entry_metrics=[
            PhaseMetrics("problem_validated", 1, "boolean"),
        ],
        exit_metrics=[
            PhaseMetrics("mvp_complete", 1, "boolean"),
            PhaseMetrics("landing_page_live", 1, "boolean"),
            PhaseMetrics("waitlist_signups", 100, "users"),
            PhaseMetrics("beta_users_active", 10, "users")
        ],
        required_actions=[
            PhaseAction(
                id="create_landing_page",
                name="Create Landing Page",
                description="Design and build a compelling landing page",
                agent_chain=["design", "content", "tech_lead"],
                priority=1,
                estimated_hours=8,
                automated=False  # Needs human review
            ),
            PhaseAction(
                id="setup_waitlist",
                name="Setup Waitlist",
                description="Configure email capture and waitlist system",
                agent_chain=["tech_lead", "growth_hacker"],
                priority=1,
                estimated_hours=2,
                automated=True
            ),
            PhaseAction(
                id="build_mvp",
                name="Build MVP",
                description="Develop minimum viable product",
                agent_chain=["product_pm", "tech_lead", "qa_tester"],
                priority=1,
                estimated_hours=80,
                automated=False
            ),
            PhaseAction(
                id="content_engine",
                name="Start Content Engine",
                description="Begin creating content to build audience",
                agent_chain=["content", "judgement", "growth_hacker"],
                priority=2,
                estimated_hours=4,
                automated=True
            ),
        ],
        recommended_agents=["tech_lead", "product_pm", "design", "content"],
        next_phase=StartupPhase.LAUNCH
    ),
    
    StartupPhase.LAUNCH: PhaseDefinition(
        phase=StartupPhase.LAUNCH,
        name="Launch Stage",
        description="Go to market and acquire first paying customers",
        entry_metrics=[
            PhaseMetrics("mvp_complete", 1, "boolean"),
            PhaseMetrics("landing_page_live", 1, "boolean"),
        ],
        exit_metrics=[
            PhaseMetrics("platforms_submitted", 50, "platforms"),
            PhaseMetrics("total_users", 1000, "users"),
            PhaseMetrics("paying_customers", 10, "customers"),
            PhaseMetrics("mrr", 1000, "USD")
        ],
        required_actions=[
            PhaseAction(
                id="generate_launch_strategy",
                name="Generate Launch Strategy",
                description="AI-powered launch planning with platform recommendations",
                agent_chain=["launch_strategist"],
                priority=1,
                estimated_hours=2,
                automated=True
            ),
            PhaseAction(
                id="submit_to_platforms",
                name="Submit to 50+ Platforms",
                description="Auto-submit to Product Hunt, directories, etc.",
                agent_chain=["launch_strategist", "launch_executor"],
                priority=1,
                estimated_hours=4,
                automated=True
            ),
            PhaseAction(
                id="outreach_campaign",
                name="Launch Outreach Campaign",
                description="Generate and send personalized outreach to leads",
                agent_chain=["lead_scraper", "lead_researcher", "sdr", "sales"],
                priority=1,
                estimated_hours=8,
                automated=True
            ),
            PhaseAction(
                id="viral_content",
                name="Create Viral Launch Content",
                description="Generate viral posts for social media",
                agent_chain=["content", "judgement", "community"],
                priority=2,
                estimated_hours=4,
                automated=True
            ),
            PhaseAction(
                id="pr_outreach",
                name="PR Outreach",
                description="Reach out to journalists and bloggers",
                agent_chain=["lead_researcher", "sdr", "content"],
                priority=2,
                estimated_hours=6,
                automated=True
            ),
        ],
        recommended_agents=["launch_strategist", "launch_executor", "sdr", "content"],
        next_phase=StartupPhase.GROW
    ),
    
    StartupPhase.GROW: PhaseDefinition(
        phase=StartupPhase.GROW,
        name="Growth Stage",
        description="Scale acquisition and optimize funnel",
        entry_metrics=[
            PhaseMetrics("paying_customers", 10, "customers"),
        ],
        exit_metrics=[
            PhaseMetrics("paying_customers", 100, "customers"),
            PhaseMetrics("mrr", 10000, "USD"),
            PhaseMetrics("churn_rate_below", 5, "percent")
        ],
        required_actions=[
            PhaseAction(
                id="funnel_optimization",
                name="Optimize Conversion Funnel",
                description="Analyze and improve each funnel stage",
                agent_chain=["data_analyst", "growth_hacker", "product_pm"],
                priority=1,
                estimated_hours=8,
                automated=True
            ),
            PhaseAction(
                id="scale_content",
                name="Scale Content Production",
                description="10x content output with AI",
                agent_chain=["content", "judgement", "community", "ambassador_outreach"],
                priority=1,
                estimated_hours=10,
                automated=True
            ),
            PhaseAction(
                id="sales_pipeline",
                name="Build Sales Pipeline",
                description="Systematic outbound sales process",
                agent_chain=["lead_scraper", "lead_researcher", "sdr", "sales", "customer_success"],
                priority=1,
                estimated_hours=16,
                automated=True
            ),
            PhaseAction(
                id="customer_success_system",
                name="Customer Success System",
                description="Reduce churn with proactive success",
                agent_chain=["customer_success", "data_analyst"],
                priority=2,
                estimated_hours=4,
                automated=True
            ),
        ],
        recommended_agents=["growth_hacker", "data_analyst", "sales", "customer_success"],
        next_phase=StartupPhase.SCALE
    ),
    
    StartupPhase.SCALE: PhaseDefinition(
        phase=StartupPhase.SCALE,
        name="Scale Stage",
        description="Raise funding, build team, achieve escape velocity",
        entry_metrics=[
            PhaseMetrics("mrr", 10000, "USD"),
        ],
        exit_metrics=[
            PhaseMetrics("mrr", 100000, "USD"),
            PhaseMetrics("funding_raised", 500000, "USD"),
            PhaseMetrics("team_size", 10, "people")
        ],
        required_actions=[
            PhaseAction(
                id="fundraising_prep",
                name="Fundraising Preparation",
                description="Prepare pitch deck, data room, investor list",
                agent_chain=["fundraising_coach", "finance_cfo", "data_analyst"],
                priority=1,
                estimated_hours=20,
                automated=False
            ),
            PhaseAction(
                id="investor_outreach",
                name="Investor Outreach",
                description="Research and reach out to matching investors",
                agent_chain=["fundraising_coach", "lead_researcher", "sdr"],
                priority=1,
                estimated_hours=16,
                automated=True
            ),
            PhaseAction(
                id="hiring_pipeline",
                name="Build Hiring Pipeline",
                description="Create job postings, source candidates",
                agent_chain=["hr_operations", "content"],
                priority=2,
                estimated_hours=8,
                automated=True
            ),
            PhaseAction(
                id="legal_compliance",
                name="Legal & Compliance",
                description="Ensure legal structure is investor-ready",
                agent_chain=["legal_counsel", "finance_cfo"],
                priority=2,
                estimated_hours=8,
                automated=False
            ),
        ],
        recommended_agents=["fundraising_coach", "finance_cfo", "hr_operations", "legal_counsel"],
        next_phase=None
    ),
}


class SuccessProtocol:
    """
    The Inevitable Success Protocol (ISP)
    
    Guides startups through phases with automated agent orchestration.
    Knows exactly what to do next and which agents to deploy.
    """
    
    def __init__(self):
        self.phases = PHASE_DEFINITIONS
        logger.info("Success Protocol initialized", phases=len(self.phases))
    
    def get_phase(self, phase: StartupPhase) -> PhaseDefinition:
        """Get phase definition"""
        return self.phases.get(phase)
    
    def detect_phase(self, metrics: Dict[str, Any]) -> StartupPhase:
        """
        Detect current phase based on metrics
        """
        # Check from Scale backwards
        for phase in reversed(list(StartupPhase)):
            phase_def = self.phases[phase]
            if self._meets_entry_metrics(metrics, phase_def.entry_metrics):
                return phase
        return StartupPhase.IDEA
    
    def _meets_entry_metrics(self, current: Dict[str, Any], required: List[PhaseMetrics]) -> bool:
        """Check if current metrics meet entry requirements"""
        if not required:
            return True
        
        for metric in required:
            current_value = current.get(metric.name, 0)
            if current_value < metric.target:
                return False
        return True
    
    def get_required_actions(
        self, 
        phase: StartupPhase, 
        completed_actions: List[str] = None
    ) -> List[PhaseAction]:
        """
        Get required actions for phase, filtered by what's already done
        """
        completed = set(completed_actions or [])
        phase_def = self.phases.get(phase)
        if not phase_def:
            return []
        
        actions = [a for a in phase_def.required_actions if a.id not in completed]
        # Sort by priority
        return sorted(actions, key=lambda a: a.priority)
    
    def get_next_action(
        self, 
        phase: StartupPhase, 
        completed_actions: List[str] = None
    ) -> Optional[PhaseAction]:
        """Get the single highest-priority next action"""
        actions = self.get_required_actions(phase, completed_actions)
        return actions[0] if actions else None
    
    def get_automated_actions(
        self, 
        phase: StartupPhase, 
        completed_actions: List[str] = None
    ) -> List[PhaseAction]:
        """Get actions that can run without human approval"""
        return [
            a for a in self.get_required_actions(phase, completed_actions)
            if a.automated
        ]
    
    def get_phase_progress(
        self, 
        phase: StartupPhase, 
        current_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate progress towards phase completion"""
        phase_def = self.phases.get(phase)
        if not phase_def:
            return {"progress": 0, "status": "unknown"}
        
        total_progress = 0
        metric_progress = []
        
        for metric in phase_def.exit_metrics:
            current = current_metrics.get(metric.name, 0)
            progress = min(100, (current / max(metric.target, 1)) * 100)
            total_progress += progress
            metric_progress.append({
                "name": metric.name,
                "current": current,
                "target": metric.target,
                "progress": progress,
                "complete": current >= metric.target
            })
        
        avg_progress = total_progress / max(len(phase_def.exit_metrics), 1)
        
        return {
            "phase": phase.value,
            "overall_progress": avg_progress,
            "ready_to_advance": avg_progress >= 100,
            "metrics": metric_progress,
            "next_phase": phase_def.next_phase.value if phase_def.next_phase else None
        }
    
    def get_agent_chain(self, action_id: str, phase: StartupPhase) -> List[str]:
        """Get the agent chain for a specific action"""
        phase_def = self.phases.get(phase)
        if not phase_def:
            return []
        
        for action in phase_def.required_actions:
            if action.id == action_id:
                return action.agent_chain
        return []
    
    def get_all_phases_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all phases for display"""
        return [
            {
                "phase": p.value,
                "name": self.phases[p].name,
                "description": self.phases[p].description,
                "action_count": len(self.phases[p].required_actions),
                "exit_metrics": [m.name for m in self.phases[p].exit_metrics]
            }
            for p in StartupPhase
        ]


# Singleton instance
success_protocol = SuccessProtocol()
