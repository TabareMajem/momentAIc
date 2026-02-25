"""
Agent Registry
Central factory for creating and managing agent lifecycles.
Provides dependency injection and avoids global singletons.
"""

from typing import Dict, Any
import importlib

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, str] = {}
        
    def register(self, name: str, module_path: str, class_name: str):
        """Register an agent's class path by canonical name."""
        self._agents[name] = f"{module_path}:{class_name}"
        
    def get(self, name: str, **kwargs) -> Any:
        """
        Instantiate and return a fresh agent instance.
        This resolves the singleton shared state issue across requests
        and allows for easy dependency injection in tests.
        """
        if name not in self._agents:
            raise ValueError(f"Agent '{name}' not found in registry")
            
        path = self._agents[name]
        module_path, class_name = path.split(":")
        
        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)
        
        # Instantiate fresh
        return agent_class(**kwargs)

# Global registry instance
agent_registry = AgentRegistry()

# ===========================
# Register All Agents
# ===========================

# Core
agent_registry.register("supervisor", "app.agents.supervisor", "SupervisorAgent")
agent_registry.register("sales", "app.agents.sales_agent", "SalesAgent")
agent_registry.register("content", "app.agents.content_agent", "ContentAgent")

# Phase 1
agent_registry.register("tech_lead", "app.agents.tech_lead_agent", "TechLeadAgent")
agent_registry.register("finance_cfo", "app.agents.finance_cfo_agent", "FinanceCFOAgent")
agent_registry.register("legal_counsel", "app.agents.legal_counsel_agent", "LegalCounselAgent")
agent_registry.register("growth_hacker", "app.agents.growth_hacker_agent", "GrowthHackerAgent")
agent_registry.register("product_pm", "app.agents.product_pm_agent", "ProductPMAgent")

# Phase 2
agent_registry.register("customer_success", "app.agents.customer_success_agent", "CustomerSuccessAgent")
agent_registry.register("data_analyst", "app.agents.data_analyst_agent", "DataAnalystAgent")
agent_registry.register("hr_operations", "app.agents.hr_operations_agent", "HROperationsAgent")
agent_registry.register("marketing", "app.agents.marketing_agent", "MarketingAgent")
agent_registry.register("community", "app.agents.community_agent", "CommunityAgent")
agent_registry.register("devops", "app.agents.devops_agent", "DevOpsAgent")
agent_registry.register("strategy", "app.agents.strategy_agent", "StrategyAgent")
agent_registry.register("browser", "app.agents.browser_agent", "BrowserAgent")
agent_registry.register("design", "app.agents.design_agent", "DesignAgent")
agent_registry.register("planning", "app.agents.planning_agent", "PlanningAgent")

# Swarm / Hunter
agent_registry.register("lead_scraper", "app.agents.lead_scraper_agent", "LeadScraperAgent")
agent_registry.register("lead_researcher", "app.agents.lead_researcher_agent", "LeadResearcherAgent")
agent_registry.register("sdr", "app.agents.sdr_agent", "SDRAgent")
agent_registry.register("judgement", "app.agents.judgement_agent", "JudgementAgent")
agent_registry.register("qa_tester", "app.agents.qa_tester_agent", "QATesterAgent")
agent_registry.register("launch_strategist", "app.agents.launch_strategist_agent", "LaunchStrategistAgent")

# Specialty / Guerrilla
agent_registry.register("competitor_intel", "app.agents.competitor_intel_agent", "CompetitorIntelAgent")
agent_registry.register("onboarding_coach", "app.agents.onboarding_coach_agent", "OnboardingCoachAgent")
agent_registry.register("fundraising_coach", "app.agents.fundraising_coach_agent", "FundraisingCoachAgent")
agent_registry.register("ambassador", "app.agents.ambassador_agent", "AmbassadorAgent")
agent_registry.register("acquisition", "app.agents.acquisition_agent", "AcquisitionAgent")
agent_registry.register("dealmaker", "app.agents.dealmaker_agent", "DealmakerAgent")
agent_registry.register("deep_research", "app.agents.deep_research_agent", "DeepResearchAgent")
agent_registry.register("empire_strategist", "app.agents.empire_strategist", "EmpireStrategist")
agent_registry.register("kol_headhunter", "app.agents.kol_headhunter_agent", "KOLHeadhunterAgent")
agent_registry.register("launch_executor", "app.agents.launch_executor_agent", "LaunchExecutorAgent")
agent_registry.register("localization_architect", "app.agents.localization_architect_agent", "LocalizationArchitectAgent")
agent_registry.register("war_gaming", "app.agents.war_gaming_agent", "WarGamingAgent")
agent_registry.register("integration_builder", "app.agents.integration_builder_agent", "IntegrationBuilderAgent")

# Guerrilla specifics
agent_registry.register("guerrilla_campaign", "app.agents.guerrilla.guerrilla_campaign_agent", "GuerrillaCampaignAgent")
agent_registry.register("discord", "app.agents.guerrilla.discord_agent", "DiscordAgent")
agent_registry.register("reddit_sniper", "app.agents.guerrilla.reddit_sniper_agent", "RedditSniperAgent")

# Some legacy systems expect exact match keys
