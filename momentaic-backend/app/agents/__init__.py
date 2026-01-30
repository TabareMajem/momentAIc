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

# Create a proxy object for backward compatibility
class AgentProxy:
    def __getattr__(self, name):
        agents = LazyAgents()
        if hasattr(agents, name.replace("_agent", "")):
            return getattr(agents, name.replace("_agent", ""))
        raise AttributeError(f"Agent {name} not found")

# Re-defining common names for direct access if needed
# but keeping them as functions to ensure they don't load immediately
def get_supervisor_agent():
    from app.agents.supervisor import supervisor_agent
    return supervisor_agent

def get_sales_agent():
    from app.agents.sales_agent import sales_agent
    return sales_agent

# For now, let's just use the properties for the ones that were singletons
# Note: I'll use a hack to keep the names exactly as they were used in the app
import sys

class _AgentsModule(sys.modules[__name__].__class__):
    @property
    def supervisor_agent(self):
        from app.agents.supervisor import supervisor_agent
        return supervisor_agent
    
    @property
    def sales_agent(self):
        from app.agents.sales_agent import sales_agent
        return sales_agent

    @property
    def content_agent(self):
        from app.agents.content_agent import content_agent
        return content_agent

    @property
    def tech_lead_agent(self):
        from app.agents.tech_lead_agent import tech_lead_agent
        return tech_lead_agent

    @property
    def finance_cfo_agent(self):
        from app.agents.finance_cfo_agent import finance_cfo_agent
        return finance_cfo_agent

    @property
    def legal_counsel_agent(self):
        from app.agents.legal_counsel_agent import legal_counsel_agent
        return legal_counsel_agent

    @property
    def growth_hacker_agent(self):
        from app.agents.growth_hacker_agent import growth_hacker_agent
        return growth_hacker_agent

    @property
    def product_pm_agent(self):
        from app.agents.product_pm_agent import product_pm_agent
        return product_pm_agent

    @property
    def customer_success_agent(self):
        from app.agents.customer_success_agent import customer_success_agent
        return customer_success_agent

    @property
    def data_analyst_agent(self):
        from app.agents.data_analyst_agent import data_analyst_agent
        return data_analyst_agent

    @property
    def hr_operations_agent(self):
        from app.agents.hr_operations_agent import hr_operations_agent
        return hr_operations_agent

    @property
    def marketing_agent(self):
        from app.agents.marketing_agent import marketing_agent
        return marketing_agent

    @property
    def community_agent(self):
        from app.agents.community_agent import community_agent
        return community_agent

    @property
    def devops_agent(self):
        from app.agents.devops_agent import devops_agent
        return devops_agent

    @property
    def strategy_agent(self):
        from app.agents.strategy_agent import strategy_agent
        return strategy_agent

    @property
    def browser_agent(self):
        from app.agents.browser_agent import browser_agent
        return browser_agent

    @property
    def design_agent(self):
        from app.agents.design_agent import design_agent
        return design_agent

    @property
    def lead_scraper_agent(self):
        from app.agents.lead_scraper_agent import lead_scraper_agent
        return lead_scraper_agent

    @property
    def lead_researcher_agent(self):
        from app.agents.lead_researcher_agent import lead_researcher_agent
        return lead_researcher_agent

    @property
    def sdr_agent(self):
        from app.agents.sdr_agent import sdr_agent
        return sdr_agent

    @property
    def judgement_agent(self):
        from app.agents.judgement_agent import judgement_agent
        return judgement_agent

    @property
    def qa_tester_agent(self):
        from app.agents.qa_tester_agent import qa_tester_agent
        return qa_tester_agent

    @property
    def launch_strategist_agent(self):
        from app.agents.launch_strategist_agent import launch_strategist_agent
        return launch_strategist_agent

    # === NEW: Previously Unregistered Agents ===
    @property
    def competitor_intel_agent(self):
        from app.agents.competitor_intel_agent import competitor_intel_agent
        return competitor_intel_agent

    @property
    def onboarding_coach_agent(self):
        from app.agents.onboarding_coach_agent import onboarding_coach_agent
        return onboarding_coach_agent

    @property
    def fundraising_coach_agent(self):
        from app.agents.fundraising_coach_agent import fundraising_coach_agent
        return fundraising_coach_agent

    @property
    def ambassador_agent(self):
        from app.agents.ambassador_agent import ambassador_agent
        return ambassador_agent

    @property
    def acquisition_agent(self):
        from app.agents.acquisition_agent import acquisition_agent
        return acquisition_agent

    @property
    def dealmaker_agent(self):
        from app.agents.dealmaker_agent import dealmaker_agent
        return dealmaker_agent

    @property
    def deep_research_agent(self):
        from app.agents.deep_research_agent import deep_research_agent
        return deep_research_agent

    @property
    def empire_strategist(self):
        from app.agents.empire_strategist import empire_strategist
        return empire_strategist

    @property
    def kol_headhunter_agent(self):
        from app.agents.kol_headhunter_agent import kol_headhunter_agent
        return kol_headhunter_agent

    @property
    def launch_executor_agent(self):
        from app.agents.launch_executor_agent import launch_executor_agent
        return launch_executor_agent

    @property
    def localization_architect_agent(self):
        from app.agents.localization_architect_agent import localization_architect_agent
        return localization_architect_agent

    @property
    def war_gaming_agent(self):
        from app.agents.war_gaming_agent import war_gaming_agent
        return war_gaming_agent

    @property
    def integration_builder_agent(self):
        from app.agents.integration_builder_agent import integration_builder_agent
        return integration_builder_agent

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

