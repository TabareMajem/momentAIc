"""
Growth Engine Tests (CRM + Content Studio)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.models.user import User
from app.models.startup import Startup
from app.models.growth import Lead, LeadStatus, ContentItem


class TestLeadEndpoints:
    """Test CRM/Lead management endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_lead(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test lead creation"""
        response = await client.post(
            f"/api/v1/growth/leads?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "company_name": "Acme Corp",
                "company_website": "https://acme.com",
                "company_size": "50-100",
                "company_industry": "SaaS",
                "contact_name": "John Doe",
                "contact_title": "CTO",
                "contact_email": "john@acme.com",
                "source": "linkedin",
                "deal_value": 50000,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["company_name"] == "Acme Corp"
        assert data["status"] == "new"
        assert data["contact_email"] == "john@acme.com"
    
    @pytest.mark.asyncio
    async def test_list_leads(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test listing leads"""
        # Create a lead first
        await client.post(
            f"/api/v1/growth/leads?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "company_name": "Test Company",
                "contact_name": "Jane Smith",
                "contact_email": "jane@test.com",
                "source": "manual",
            },
        )
        
        response = await client.get(
            f"/api/v1/growth/leads?startup_id={test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_leads_kanban(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test Kanban view"""
        response = await client.get(
            f"/api/v1/growth/leads/kanban?startup_id={test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "new" in data
        assert "outreach" in data
        assert "won" in data
    
    @pytest.mark.asyncio
    async def test_update_lead_status(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test moving lead through pipeline"""
        # Create lead
        create_response = await client.post(
            f"/api/v1/growth/leads?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "company_name": "Pipeline Test",
                "contact_name": "Test Contact",
                "contact_email": "test@pipeline.com",
                "source": "manual",
            },
        )
        lead_id = create_response.json()["id"]
        
        # Move to outreach
        response = await client.patch(
            f"/api/v1/growth/leads/{lead_id}?startup_id={test_startup.id}",
            headers=auth_headers,
            json={"status": "outreach"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "outreach"
    
    @pytest.mark.asyncio
    async def test_toggle_autopilot(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test autopilot toggle"""
        # Create lead
        create_response = await client.post(
            f"/api/v1/growth/leads?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "company_name": "Autopilot Test",
                "contact_name": "Auto Pilot",
                "contact_email": "auto@pilot.com",
                "source": "manual",
            },
        )
        lead_id = create_response.json()["id"]
        
        # Enable autopilot
        response = await client.post(
            f"/api/v1/growth/leads/{lead_id}/autopilot?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "enabled": True,
                "max_followups": 5,
                "followup_interval_days": 3,
            },
        )
        assert response.status_code == 200
        assert response.json()["autopilot_enabled"] == True
    
    @pytest.mark.asyncio
    async def test_generate_outreach(self, client: AsyncClient, test_startup: Startup, auth_headers: dict, mock_llm):
        """Test AI outreach generation"""
        # Create lead
        create_response = await client.post(
            f"/api/v1/growth/leads?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "company_name": "Outreach Test Co",
                "contact_name": "Outreach Target",
                "contact_email": "outreach@test.com",
                "source": "linkedin",
            },
        )
        lead_id = create_response.json()["id"]
        
        # Generate outreach
        response = await client.post(
            f"/api/v1/growth/leads/{lead_id}/generate-outreach?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "channel": "email",
                "tone": "professional",
                "objective": "intro",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "body" in data


class TestContentEndpoints:
    """Test Content Studio endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_content(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test content creation"""
        response = await client.post(
            f"/api/v1/growth/content?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "title": "My First Post",
                "platform": "linkedin",
                "content_type": "post",
                "body": "This is the content of my post...",
                "hook": "Stop scrolling - you need to read this!",
                "cta": "Follow for more insights!",
                "hashtags": ["#startup", "#tech"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My First Post"
        assert data["platform"] == "linkedin"
    
    @pytest.mark.asyncio
    async def test_list_content(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test listing content"""
        # Create content first
        await client.post(
            f"/api/v1/growth/content?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "title": "Test Content",
                "platform": "twitter",
                "content_type": "post",
                "body": "Test tweet content",
            },
        )
        
        response = await client.get(
            f"/api/v1/growth/content?startup_id={test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_content_calendar(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test content calendar view"""
        response = await client.get(
            f"/api/v1/growth/content/calendar?startup_id={test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "scheduled" in data
        assert "drafts" in data
        assert "published_this_week" in data
    
    @pytest.mark.asyncio
    async def test_generate_content(self, client: AsyncClient, test_startup: Startup, auth_headers: dict, mock_llm):
        """Test AI content generation"""
        response = await client.post(
            f"/api/v1/growth/content/generate?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "platform": "linkedin",
                "content_type": "post",
                "topic": "The future of AI in startups",
                "tone": "professional",
                "trend_based": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "body" in data
    
    @pytest.mark.asyncio
    async def test_schedule_content(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test scheduling content"""
        # Create content
        create_response = await client.post(
            f"/api/v1/growth/content?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "title": "Scheduled Post",
                "platform": "linkedin",
                "content_type": "post",
                "body": "This will be posted later",
                "scheduled_for": "2025-12-31T10:00:00Z",
            },
        )
        assert create_response.status_code == 201
        data = create_response.json()
        assert data["status"] == "scheduled"
        assert data["scheduled_for"] is not None
    
    @pytest.mark.asyncio
    async def test_publish_content(self, client: AsyncClient, test_startup: Startup, auth_headers: dict):
        """Test publishing content"""
        # Create draft content
        create_response = await client.post(
            f"/api/v1/growth/content?startup_id={test_startup.id}",
            headers=auth_headers,
            json={
                "title": "Draft to Publish",
                "platform": "twitter",
                "content_type": "post",
                "body": "Publishing this now!",
            },
        )
        content_id = create_response.json()["id"]
        
        # Publish
        response = await client.post(
            f"/api/v1/growth/content/{content_id}/publish?startup_id={test_startup.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "published"
