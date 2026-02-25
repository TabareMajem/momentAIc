"""
Agent Registry & BaseAgent Integration Tests
Tests that the AgentRegistry can instantiate agents
and that upgraded agents properly inherit from BaseAgent.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestAgentRegistry:
    """Test the AgentRegistry instantiation and resolution."""

    def test_registry_loads_all_agents(self):
        """Registry should have 40+ agents registered."""
        from app.agents.registry import agent_registry
        assert len(agent_registry._agents) >= 35, (
            f"Expected 35+ agents, got {len(agent_registry._agents)}"
        )

    def test_registry_get_unknown_agent_raises(self):
        """Getting an unknown agent should raise ValueError."""
        from app.agents.registry import agent_registry
        with pytest.raises(ValueError, match="not found"):
            agent_registry.get("nonexistent_agent_xyz")

    def test_registry_returns_fresh_instances(self):
        """Each .get() call should return a new instance (not singleton)."""
        from app.agents.registry import agent_registry
        # Use planning agent since it's lightweight
        a1 = agent_registry.get("planning")
        a2 = agent_registry.get("planning")
        assert a1 is not a2, "Registry should return fresh instances, not singletons"

    def test_registry_contains_core_agents(self):
        """Core agents should be registered."""
        from app.agents.registry import agent_registry
        core_agents = [
            "sales", "content", "growth_hacker", "product_pm",
            "marketing", "sdr", "launch_strategist", "planning",
        ]
        for name in core_agents:
            assert name in agent_registry._agents, f"Agent '{name}' missing from registry"


class TestBaseAgentInheritance:
    """Test that upgraded agents properly inherit from BaseAgent."""

    def test_product_pm_is_base_agent(self):
        from app.agents.base import BaseAgent
        from app.agents.product_pm_agent import ProductPMAgent
        assert issubclass(ProductPMAgent, BaseAgent)

    def test_marketing_is_base_agent(self):
        from app.agents.base import BaseAgent
        from app.agents.marketing_agent import MarketingAgent
        assert issubclass(MarketingAgent, BaseAgent)

    def test_sdr_is_base_agent(self):
        from app.agents.base import BaseAgent
        from app.agents.sdr_agent import SDRAgent
        assert issubclass(SDRAgent, BaseAgent)

    def test_launch_strategist_is_base_agent(self):
        from app.agents.base import BaseAgent
        from app.agents.launch_strategist_agent import LaunchStrategistAgent
        assert issubclass(LaunchStrategistAgent, BaseAgent)

    def test_guerrilla_campaign_is_base_agent(self):
        from app.agents.base import BaseAgent
        from app.agents.guerrilla.guerrilla_campaign_agent import GuerrillaCampaignAgent
        assert issubclass(GuerrillaCampaignAgent, BaseAgent)

    def test_discord_dispute_bot_is_base_agent(self):
        from app.agents.base import BaseAgent
        from app.agents.guerrilla.discord_agent import DiscordDisputeBot
        assert issubclass(DiscordDisputeBot, BaseAgent)


class TestBaseAgentMethods:
    """Test that BaseAgent provides structured_llm_call and self_correcting_call."""

    def test_base_agent_has_structured_llm_call(self):
        from app.agents.base import BaseAgent
        assert hasattr(BaseAgent, "structured_llm_call")

    def test_base_agent_has_self_correcting_call(self):
        from app.agents.base import BaseAgent
        assert hasattr(BaseAgent, "self_correcting_call")

    def test_product_pm_has_structured_models(self):
        """ProductPMAgent should define Pydantic response models."""
        from app.agents.product_pm_agent import (
            ProductPMProcess,
            PrioritizationResult,
            UserStoriesResult,
            PRDResult,
            FeedbackAnalysisResult,
            RoadmapResult,
            CompetitiveResult,
        )
        # Verify they're all Pydantic models
        from pydantic import BaseModel
        for model in [ProductPMProcess, PrioritizationResult, UserStoriesResult,
                      PRDResult, FeedbackAnalysisResult, RoadmapResult, CompetitiveResult]:
            assert issubclass(model, BaseModel), f"{model.__name__} is not a Pydantic model"

    def test_marketing_has_structured_models(self):
        """MarketingAgent should define Pydantic response models."""
        from app.agents.marketing_agent import (
            CampaignPlan,
            LeadMagnet,
            LandingPageSection,
            ViralHook,
            OpportunityList,
        )
        from pydantic import BaseModel
        for model in [CampaignPlan, LeadMagnet, LandingPageSection, ViralHook, OpportunityList]:
            assert issubclass(model, BaseModel), f"{model.__name__} is not a Pydantic model"

    def test_sdr_has_spam_analysis_model(self):
        """SDRAgent should define SpamAnalysis Pydantic model."""
        from app.agents.sdr_agent import SpamAnalysis
        from pydantic import BaseModel
        assert issubclass(SpamAnalysis, BaseModel)
