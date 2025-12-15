"""
Startup Tests
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.models.user import User
from app.models.startup import Startup


class TestStartupEndpoints:
    """Test startup CRUD endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_startup(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test startup creation"""
        response = await client.post(
            "/api/v1/startups",
            headers=auth_headers,
            json={
                "name": "My New Startup",
                "tagline": "Changing the world",
                "description": "A revolutionary product",
                "industry": "FinTech",
                "stage": "mvp",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My New Startup"
        assert data["industry"] == "FinTech"
        assert data["stage"] == "mvp"
    
    @pytest.mark.asyncio
    async def test_list_startups(self, client: AsyncClient, test_user: User, test_startup: Startup, auth_headers: dict):
        """Test listing user's startups"""
        response = await client.get("/api/v1/startups", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(s["id"] == str(test_startup.id) for s in data)
    
    @pytest.mark.asyncio
    async def test_get_startup(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test getting a specific startup"""
        response = await client.get(
            f"/api/v1/startups/{test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_startup.id)
        assert data["name"] == test_startup.name
    
    @pytest.mark.asyncio
    async def test_get_startup_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent startup"""
        response = await client.get(
            f"/api/v1/startups/{uuid4()}",
            headers=auth_headers,
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_startup(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test updating a startup"""
        response = await client.patch(
            f"/api/v1/startups/{test_startup.id}",
            headers=auth_headers,
            json={
                "name": "Updated Startup Name",
                "stage": "pmf",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Startup Name"
        assert data["stage"] == "pmf"
    
    @pytest.mark.asyncio
    async def test_delete_startup(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test deleting a startup"""
        response = await client.delete(
            f"/api/v1/startups/{test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 204
        
        # Verify deletion
        response = await client.get(
            f"/api/v1/startups/{test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_dashboard(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test getting startup dashboard"""
        response = await client.get(
            f"/api/v1/startups/{test_startup.id}/dashboard",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "startup" in data
        assert "lead_summary" in data
        assert "content_scheduled" in data
    
    @pytest.mark.asyncio
    async def test_update_metrics(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test updating startup metrics"""
        response = await client.post(
            f"/api/v1/startups/{test_startup.id}/metrics",
            headers=auth_headers,
            json={
                "mrr": 25000,
                "dau": 1000,
                "burn_rate": 40000,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metrics"]["mrr"] == 25000
        assert data["metrics"]["dau"] == 1000


class TestSprintEndpoints:
    """Test sprint management endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_sprint(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test sprint creation"""
        response = await client.post(
            f"/api/v1/startups/{test_startup.id}/sprints",
            headers=auth_headers,
            json={
                "goal": "Launch MVP",
                "key_results": [
                    "Complete core features",
                    "Deploy to production",
                    "Onboard 10 beta users",
                ],
                "start_date": "2025-01-01",
                "end_date": "2025-01-07",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["goal"] == "Launch MVP"
        assert len(data["key_results"]) == 3
        assert data["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_list_sprints(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test listing sprints"""
        # Create a sprint first
        await client.post(
            f"/api/v1/startups/{test_startup.id}/sprints",
            headers=auth_headers,
            json={
                "goal": "Test Sprint",
                "key_results": ["Result 1"],
                "start_date": "2025-01-01",
                "end_date": "2025-01-07",
            },
        )
        
        response = await client.get(
            f"/api/v1/startups/{test_startup.id}/sprints",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_create_standup(self, client: AsyncClient, test_startup: Startup, auth_headers: dict, mock_llm):
        """Test standup creation with AI feedback"""
        # Create sprint
        sprint_response = await client.post(
            f"/api/v1/startups/{test_startup.id}/sprints",
            headers=auth_headers,
            json={
                "goal": "Sprint for standup test",
                "key_results": ["Key result"],
                "start_date": "2025-01-01",
                "end_date": "2025-01-07",
            },
        )
        sprint_id = sprint_response.json()["id"]
        
        # Create standup
        response = await client.post(
            f"/api/v1/startups/{test_startup.id}/sprints/{sprint_id}/standups",
            headers=auth_headers,
            json={
                "yesterday": "Worked on feature X",
                "today": "Will finish feature X and start Y",
                "blockers": "None",
                "mood": "good",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["yesterday"] == "Worked on feature X"
        assert data["mood"] == "good"
