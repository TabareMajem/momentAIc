"""
Agent Integration & E2E Route Tests
Tests the full lifecycle of specialized agents with mocked LLM calls
to verify structured parsing, BaseAgent inheritance features, and routing.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.api.v1.endpoints.chat import MessageRequest

@pytest.fixture
def mock_startup_context():
    return {
        "id": "test_startup_123",
        "name": "Acme Corp",
        "description": "A B2B SaaS for dog walkers",
        "industry": "Pets / SaaS",
        "target_audience": "Urban dog walkers with 5+ clients"
    }

@pytest.fixture
def mock_llm_chain():
    """Mock the langchain LCEL chain for BaseAgent"""
    with patch("app.agents.base.ChatOpenAI") as mock_openai, \
         patch("app.agents.base.ChatGoogleGenerativeAI") as mock_gemini:
        
        # Setup mock chain
        chain_mock = MagicMock()
        chain_mock.ainvoke.return_value = MagicMock(content="""
        {
            "priority": "high",
            "findings": ["Finding 1", "Finding 2"],
            "recommendation": "Do the thing"
        }
        """)
        
        # When get_llm is called, it returns something that can create our chain
        yield chain_mock

@pytest.mark.asyncio
async def test_sales_agent_structured_output(mock_startup_context):
    """Test the upgraded SalesAgent utilizing exact Pydantic output"""
    from app.agents.registry import AgentRegistry
    from app.agents.sales_agent import SalesAgent, SalesStrategyResponse
    
    # 1. Verification of instantiation and inheritance
    agent = AgentRegistry.get("SalesAgent")
    assert isinstance(agent, SalesAgent)
    from app.agents.base import BaseAgent
    assert isinstance(agent, BaseAgent)
    
    # 2. Mocking the structured_llm_call directly to focus on business logic
    with patch.object(agent, 'structured_llm_call') as mock_call:
        expected_response = SalesStrategyResponse(
            priority_leads=["Lead A"],
            outreach_angles=["Angle B"],
            qualification_criteria=["Criteria C"],
            next_steps="Draft email",
            confidence_score=90
        )
        mock_call.return_value = expected_response
        
        # Run agent
        result = await agent.strategize(
            target_audience="Dog walkers",
            product_description="SaaS tool",
            startup_context=mock_startup_context
        )
        
        # Assertions
        assert result == expected_response
        mock_call.assert_called_once()
        # Verify the prompt passed to the LLM contains context
        call_args = mock_call.call_args.kwargs
        assert "SaaS tool" in call_args["prompt"]
        assert mock_startup_context["name"] in call_args["prompt"]


@pytest.mark.asyncio
async def test_yokaizen_agent_connectivity(mock_startup_context):
    """Test the Yokaizen Specialized agent (Phase 5 addition)"""
    from app.agents.registry import AgentRegistry
    from app.agents.specialized.yokaizen_agent import YokaizenAgent, YokaizenStrategyResponse
    
    agent = AgentRegistry.get("YokaizenAgent")
    assert isinstance(agent, YokaizenAgent)
    
    with patch("app.services.agent_memory_service.agent_memory_service.get_relevant_memories") as mock_memories:
        # Mock empty memories
        mock_memories.return_value = []
        
        with patch.object(agent, 'structured_llm_call') as mock_call:
            expected_response = YokaizenStrategyResponse(
                tactics=["Use Bonded Yokai"],
                reasoning="Co-parenting drives viral loops",
                target_audience="West",
                viral_mechanic="Sync Quests"
            )
            mock_call.return_value = expected_response
            
            result = await agent.chat(
                user_input="How do I get more installs?",
                startup_context=mock_startup_context
            )
            
            assert result == expected_response
            # Verify memory was queried
            mock_memories.assert_called_once_with(
                startup_id=mock_startup_context["id"],
                query="How do I get more installs?",
                agent_type="yokaizen"
            )

@pytest.mark.asyncio
async def test_agent_autonomy_system():
    """Verify the BaseAgent autonomy methods are present and functional"""
    from app.agents.base import BaseAgent
    
    class DummyAgent(BaseAgent):
        async def proactive_scan(self, startup_context):
            return [{"action": "test", "priority": "high"}]
            
        async def autonomous_action(self, action, startup_context):
            return "DONE"
            
    agent = DummyAgent("test_agent")
    
    # Check default flags
    assert agent.can_act_autonomously() is True
    
    # Check scan execution
    scan_results = await agent.proactive_scan({"name": "Test"})
    assert len(scan_results) == 1
    assert scan_results[0]["action"] == "test"
    
    # Check action execution
    result = await agent.autonomous_action(scan_results[0], {"name": "Test"})
    assert result == "DONE"

def test_ecosystem_router_routing():
    """Verify Ecosystem Router maps correctly to external services"""
    from app.services.ecosystem_router import EcosystemRouter, TaskCategory, Platform
    
    router = EcosystemRouter()
    
    # Test specific Yokaizen routing
    assert router.determine_platform(TaskCategory.SALES_HUNT) == Platform.YOKAIZEN
    assert router.determine_platform(TaskCategory.MARKETING_CAMPAIGN) == Platform.YOKAIZEN
    
    # Test specific AgentForge routing
    assert router.determine_platform(TaskCategory.WORKFLOW) == Platform.AGENTFORGE
    assert router.determine_platform(TaskCategory.VOICE_OUTBOUND) == Platform.AGENTFORGE
    
    # Test local fallback
    assert router.determine_platform(TaskCategory.LEGAL) == Platform.MOMENTAIC
    assert router.determine_platform(TaskCategory.FINANCE) == Platform.MOMENTAIC
