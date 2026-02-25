"""
Tests for the "Show Me The Money" Revenue Dashboard and Stripe Integration
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.api.v1.endpoints.agents import _get_agent_response
from app.models.conversation import AgentType

@pytest.mark.asyncio
async def test_agent_revenue_context_injection():
    """
    Verify that _get_agent_response correctly queries the LiveDataService
    and injects Stripe MRR into the agent's startup_context.
    """
    mock_db = AsyncMock()
    startup_id = str(uuid4())
    startup_context = {
        "startup_id": startup_id,
        "name": "TestCorp",
        "description": "A test company",
        "metrics": {"mrr": 0}
    }
    
    mock_revenue_data = {
        "monthly_recurring_revenue": 15000.0,
        "annual_recurring_revenue": 180000.0,
        "active_subscriptions": 150,
        "churn_rate_percent": 2.5,
        "source": "Stripe Live Data"
    }

    with patch("app.services.live_data_service.live_data_service.get_live_revenue", new_callable=AsyncMock) as mock_get_revenue:
        mock_get_revenue.return_value = mock_revenue_data
        
        # We also need to mock the agent's process method so it doesn't actually call the LLM
        with patch("app.agents.finance_cfo_agent.FinanceCFOAgent.process", new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {"response": "Dummy response"}
            
            await _get_agent_response(
                agent_type=AgentType.FINANCE_CFO,
                message="What is our MRR?",
                startup_context=startup_context,
                user_id=str(uuid4()),
                db=mock_db
            )
            
            # 1. Verify live data service was called
            mock_get_revenue.assert_called_once_with(startup_id, mock_db)
            
            # 2. Verify the context was enriched with the mocked Stripe data
            assert startup_context["metrics"]["mrr"] == 15000.0
            assert startup_context["metrics"]["churn"] == 2.5
            assert "live_revenue_data" in startup_context["metrics"]

@pytest.mark.asyncio
async def test_stripe_integration_sync_logic():
    """
    Verify the StripeIntegration wrapper parses subscription data correctly
    """
    from app.integrations.stripe import StripeIntegration
    from app.integrations.base import IntegrationCredentials
    
    # Mock the httpx client inside StripeIntegration
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # We need mock responses for MRR, Customers, and Subscriptions
        
        # 1. MRR Call (subscriptions api)
        mock_get.side_effect = [
            # MRR call
            MagicMock(status_code=200, json=lambda: {
                "data": [{
                    "items": {"data": [{"price": {"unit_amount": 5000, "recurring": {"interval": "month"}}, "quantity": 2}]}
                }],
                "has_more": False
            }),
            # Customers call
            MagicMock(status_code=200, json=lambda: {"data": [1, 2, 3], "has_more": False}),
            # Active Subs call
            MagicMock(status_code=200, json=lambda: {"total_count": 50}),
            # Trialing Subs call
            MagicMock(status_code=200, json=lambda: {"total_count": 5}),
            # Canceled Subs call
            MagicMock(status_code=200, json=lambda: {"data": [1, 2]})
        ]
        
        client = StripeIntegration(credentials=IntegrationCredentials(api_key="sk_test_123"))
        result = await client.sync_data(data_types=["mrr", "customers", "subscriptions"])
        
        assert result.success is True
        # (5000 cents * 2) / 100 = 100.0 MRR
        assert result.data["mrr"] == 100.0
        assert result.data["arr"] == 1200.0
        assert result.data["customers"]["total"] == 3
        
        subs = result.data["subscriptions"]
        assert subs["active"] == 50
        assert subs["trialing"] == 5
        assert subs["canceled_this_month"] == 2
        
        # churn = 2 / (50 + 2) = 3.8%
        assert subs["churn_rate"] == 3.8
