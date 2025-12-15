"""
Agent Forge (Workflow) Tests
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.startup import Startup


class TestWorkflowEndpoints:
    """Test workflow builder endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_workflow(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test workflow creation"""
        response = await client.post(
            f"/api/v1/forge/workflows?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "name": "Lead Nurture Workflow",
                "description": "Automated lead nurturing sequence",
                "nodes": [
                    {"id": "trigger_1", "type": "trigger", "label": "New Lead", "config": {}},
                    {"id": "ai_1", "type": "ai", "label": "Research Lead", "config": {"model": "gemini-pro"}},
                    {"id": "notify_1", "type": "notification", "label": "Notify Team", "config": {}},
                ],
                "edges": [
                    {"id": "e1", "source": "trigger_1", "target": "ai_1"},
                    {"id": "e2", "source": "ai_1", "target": "notify_1"},
                ],
                "trigger_type": "webhook",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Lead Nurture Workflow"
        assert len(data["nodes"]) == 3
        assert data["webhook_url"] is not None
    
    @pytest.mark.asyncio
    async def test_list_workflows(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test listing workflows"""
        # Create workflow first
        await client.post(
            f"/api/v1/forge/workflows?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "name": "Test Workflow",
                "nodes": [{"id": "t1", "type": "trigger", "label": "Start"}],
                "edges": [],
                "trigger_type": "manual",
            },
        )
        
        response = await client.get(
            f"/api/v1/forge/workflows?startup_id={test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_workflow(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test getting a workflow"""
        # Create workflow
        create_response = await client.post(
            f"/api/v1/forge/workflows?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "name": "Get Test Workflow",
                "nodes": [{"id": "t1", "type": "trigger", "label": "Start"}],
                "edges": [],
                "trigger_type": "manual",
            },
        )
        workflow_id = create_response.json()["id"]
        
        # Get workflow
        response = await client.get(
            f"/api/v1/forge/workflows/{workflow_id}?startup_id={test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["id"] == workflow_id
    
    @pytest.mark.asyncio
    async def test_update_workflow(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test updating a workflow"""
        # Create workflow
        create_response = await client.post(
            f"/api/v1/forge/workflows?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "name": "Original Name",
                "nodes": [{"id": "t1", "type": "trigger", "label": "Start"}],
                "edges": [],
                "trigger_type": "manual",
            },
        )
        workflow_id = create_response.json()["id"]
        
        # Update workflow
        response = await client.patch(
            f"/api/v1/forge/workflows/{workflow_id}?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "name": "Updated Name",
                "status": "active",
            },
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
        assert response.json()["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_analyze_workflow(self, client: AsyncClient, test_startup: Startup, auth_headers: dict, mock_llm):
        """Test workflow analysis from natural language"""
        response = await client.post(
            f"/api/v1/forge/analyze?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "prompt": "When a new lead comes in, research their company, draft an email, and notify me for approval before sending",
                "context": "B2B SaaS sales process",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "understanding" in data
        assert "suggested_nodes" in data
        assert "suggested_edges" in data
        assert len(data["suggested_nodes"]) > 0
    
    @pytest.mark.asyncio
    async def test_run_workflow(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test running a workflow"""
        # Create and activate workflow
        create_response = await client.post(
            f"/api/v1/forge/workflows?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "name": "Run Test Workflow",
                "nodes": [
                    {"id": "t1", "type": "trigger", "label": "Start"},
                    {"id": "transform_1", "type": "transform", "label": "Process"},
                ],
                "edges": [{"id": "e1", "source": "t1", "target": "transform_1"}],
                "trigger_type": "manual",
            },
        )
        workflow_id = create_response.json()["id"]
        
        # Activate workflow
        await client.patch(
            f"/api/v1/forge/workflows/{workflow_id}?startup_id={test_startup.id}",
            headers=auth_headers,
            json={"status": "active"},
        )
        
        # Run workflow
        response = await client.post(
            f"/api/v1/forge/workflows/{workflow_id}/run?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "inputs": {"data": "test input"},
                "async_execution": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] in ["running", "completed", "pending"]
    
    @pytest.mark.asyncio
    async def test_list_workflow_runs(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test listing workflow runs"""
        # Create, activate, and run workflow
        create_response = await client.post(
            f"/api/v1/forge/workflows?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "name": "Runs Test Workflow",
                "nodes": [{"id": "t1", "type": "trigger", "label": "Start"}],
                "edges": [],
                "trigger_type": "manual",
            },
        )
        workflow_id = create_response.json()["id"]
        
        await client.patch(
            f"/api/v1/forge/workflows/{workflow_id}?startup_id={test_startup.id}",
            headers=auth_headers,
            json={"status": "active"},
        )
        
        await client.post(
            f"/api/v1/forge/workflows/{workflow_id}/run?startup_id={test_startup.id}",
            headers=auth_headers,
            json={"inputs": {}},
        )
        
        # List runs
        response = await client.get(
            f"/api/v1/forge/workflows/{workflow_id}/runs?startup_id={test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


class TestApprovalEndpoints:
    """Test human-in-the-loop approval endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_pending_approvals(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test getting pending approvals"""
        response = await client.get(
            f"/api/v1/forge/approvals/pending?startup_id={test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "approvals" in data


class TestWebhookEndpoints:
    """Test webhook trigger endpoints"""
    
    @pytest.mark.asyncio
    async def test_trigger_webhook(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test triggering workflow via webhook"""
        # Create workflow with webhook trigger
        create_response = await client.post(
            f"/api/v1/forge/workflows?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "name": "Webhook Workflow",
                "nodes": [{"id": "t1", "type": "trigger", "label": "Webhook"}],
                "edges": [],
                "trigger_type": "webhook",
            },
        )
        webhook_url = create_response.json()["webhook_url"]
        workflow_id = create_response.json()["id"]
        
        # Activate workflow
        await client.patch(
            f"/api/v1/forge/workflows/{workflow_id}?startup_id={test_startup.id}",
            headers=auth_headers,
            json={"status": "active"},
        )
        
        # Trigger webhook (no auth required)
        response = await client.post(
            f"/api/v1/forge/webhook/{webhook_url}",
            json={"event": "new_lead", "data": {"email": "test@example.com"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "started"
