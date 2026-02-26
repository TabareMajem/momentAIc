"""
MomentAIc AI Agents
LangGraph-powered agent swarm for startup operations
"""

from app.agents.base import (
    get_llm,
    get_agent_config,
    AGENT_CONFIGS,
    AgentState,
    web_search,
    linkedin_search,
    company_research,
    draft_email,
)
# Helper for lazy loading agents
def _get_agent(agent_class_path: str):
    import importlib
    module_path, class_name = agent_class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    # Most agents are exported as a singleton instance in their module
    # or we might need to instantiate them. 
    # Looking at the original code, it was 'from ... import X_agent'
    # which implies the module already has an instance.
    return getattr(module, class_name)

class LazyAgents:
    @property
    def supervisor(self):
        from app.agents.supervisor import supervisor_agent
        return supervisor_agent

    @property
    def sales(self):
        from app.agents.sales_agent import sales_agent
        return sales_agent

    @property
    def community_manager(self):
        from app.agents.community_manager_agent import community_manager_agent
        return community_manager_agent

    @property
    def cx_guardian(self):
        from app.agents.cx_guardian_agent import cx_guardian_agent
        return cx_guardian_agent

    @property
    def content(self):
        from app.agents.content_agent import content_agent
        return content_agent

    @property
    def tech_lead(self):
        from app.agents.tech_lead_agent import tech_lead_agent
        return tech_lead_agent

    @property
    def finance_cfo(self):
        from app.agents.finance_cfo_agent import finance_cfo_agent
        return finance_cfo_agent

    @property
    def legal_counsel(self):
        from app.agents.legal_counsel_agent import legal_counsel_agent
        return legal_counsel_agent

    @property
    def growth_hacker(self):
        from app.agents.growth_hacker_agent import growth_hacker_agent
        return growth_hacker_agent

    @property
    def product_pm(self):
        from app.agents.product_pm_agent import product_pm_agent
        return product_pm_agent

    @property
    def customer_success(self):
        from app.agents.customer_success_agent import customer_success_agent
        return customer_success_agent

    @property
    def data_analyst(self):
        from app.agents.data_analyst_agent import data_analyst_agent
        return data_analyst_agent

    @property
    def hr_operations(self):
        from app.agents.hr_operations_agent import hr_operations_agent
        return hr_operations_agent

    @property
    def marketing(self):
        from app.agents.marketing_agent import marketing_agent
        return marketing_agent

    @property
    def community(self):
        from app.agents.community_agent import community_agent
        return community_agent

    @property
    def devops(self):
        from app.agents.devops_agent import devops_agent
        return devops_agent

    @property
    def strategy(self):
        from app.agents.strategy_agent import strategy_agent
        return strategy_agent

    @property
    def browser(self):
        from app.agents.browser_agent import browser_agent
        return browser_agent

    @property
    def design(self):
        from app.agents.design_agent import design_agent
        return design_agent

    @property
    def planning(self):
        from app.agents.planning_agent import planning_agent
        return planning_agent

    @property
    def lead_scraper(self):
        from app.agents.lead_scraper_agent import lead_scraper_agent
        return lead_scraper_agent

    @property
    def lead_researcher(self):
        from app.agents.lead_researcher_agent import lead_researcher_agent
        return lead_researcher_agent

    @property
    def sdr(self):
        from app.agents.sdr_agent import sdr_agent
        return sdr_agent

    @property
    def notification(self):
        from app.agents.notification_agent import notification_agent
        return notification_agent

from app.agents.registry import agent_registry

# Create a proxy object for backward compatibility
class AgentProxy:
    def __getattr__(self, name):
        # Name comes in like "sales_agent", registry needs "sales"
        core_name = name.replace("_agent", "")
        try:
            return agent_registry.get(core_name)
        except ValueError:
            raise AttributeError(f"Agent {name} not found")

# Re-defining common names for direct access if needed
# but keeping them as functions to ensure they don't load immediately
def get_supervisor_agent():
    return agent_registry.get("supervisor")

def get_sales_agent():
    return agent_registry.get("sales")

# For now, let's just use the properties for the ones that were singletons
# Note: I'll use a hack to keep the names exactly as they were used in the app
import sys

class _AgentsModule(sys.modules[__name__].__class__):
    def __getattr__(self, name):
        """
        Catch-all for any agent imported statically like:
        `from app.agents import sales_agent`
        """
        if name.endswith("_agent") or name in [
            "empire_strategist", "deep_research_agent", "get_llm", "get_agent_config",
            "AGENT_CONFIGS", "AgentState", "web_search", "linkedin_search",
            "company_research", "draft_email"
        ]:
            # If it's a known function/constant from base.py, let normal resolution handle it
            if name in globals():
                return globals()[name]
                
            core_name = name.replace("_agent", "")
            try:
                # Return a fresh instance from the registry
                return agent_registry.get(core_name)
            except ValueError:
                raise AttributeError(f"Agent {name} not found in registry")
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Replace current module with the proxy one
sys.modules[__name__].__class__ = _AgentsModule

__all__ = [
    # Core
    "get_llm",
    "get_agent_config",
    "AGENT_CONFIGS",
    "AgentState",
    # Original Agents
    "supervisor_agent",
    "sales_agent",
    "content_agent",
    # Phase 1 Agents
    "tech_lead_agent",
    "finance_cfo_agent",
    "legal_counsel_agent",
    "growth_hacker_agent",
    "product_pm_agent",
    # Phase 2 Agents
    "customer_success_agent",
    "data_analyst_agent",
    "hr_operations_agent",
    "marketing_agent",
    "community_agent",
    "devops_agent",
    "strategy_agent",
    "browser_agent",
    "design_agent",
    "planning_agent",
    # Tools
    "web_search",
    "linkedin_search",
    "company_research",
    "draft_email",
    # Hunter Swarm Agents
    "lead_scraper_agent",
    "lead_researcher_agent",
    "sdr_agent",
    "judgement_agent",
    "qa_tester_agent",
    "launch_strategist_agent",
    # USAF (Ultimate Startup Automation Flow) Components
    "startup_brain",
    "chain_executor",
    "success_protocol",
    "swarm_router",
    # ==== NEW: Previously Unregistered Specialty Agents ====
    "competitor_intel_agent",
    "onboarding_coach_agent",
    "fundraising_coach_agent",
    "ambassador_agent",
    "acquisition_agent",
    "dealmaker_agent",
    "deep_research_agent",
    "empire_strategist",
    "kol_headhunter_agent",
    "launch_executor_agent",
    "localization_architect_agent",
    "war_gaming_agent",
    "integration_builder_agent",
]

