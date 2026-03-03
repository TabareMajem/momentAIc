"""
Instantly.ai Integration
High-volume cold email with warm-up
"""

from typing import Dict, Any, List, Optional
from app.integrations.base import BaseIntegration, SyncResult
from app.core.config import settings
import structlog
import httpx

logger = structlog.get_logger()


class InstantlyIntegration(BaseIntegration):
    """
    Instantly.ai Cold Email Integration
    
    Capabilities:
    - add_lead_to_campaign: Add a lead to an email sequence
    - get_campaign_analytics: Get open/reply rates for a campaign
    - list_campaigns: List all active campaigns
    - check_replies: Get recent replies for follow-up
    """
    
    provider = "instantly"
    display_name = "Instantly.ai"
    description = "High-volume cold email with warm-up"
    oauth_required = False
    
    def __init__(self, credentials=None, config=None):
        super().__init__(credentials, config)
        self.api_key = settings.instantly_api_key
        self.base_url = "https://api.instantly.ai/api/v1"
        
        self.headers = {
            "Content-Type": "application/json"
        }

    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        return ""

    async def exchange_code(self, code: str, redirect_uri: str):
        return None

    async def refresh_tokens(self):
        return None

    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        return SyncResult(success=True, records_synced=0)

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Instantly actions
        
        Supported actions:
        - add_lead_to_campaign: { campaign_id, email, first_name, last_name, company_name, variables }
        - get_campaign_analytics: { campaign_id }
        - list_campaigns: {}
        - check_replies: { campaign_id }
        """
        if action == "add_lead_to_campaign":
            return await self.add_lead_to_campaign(params)
        elif action == "get_campaign_analytics":
            return await self.get_campaign_analytics(params)
        elif action == "list_campaigns":
            return await self.list_campaigns()
        elif action == "check_replies":
            return await self.check_replies(params)
        
        return {"error": f"Unknown action: {action}"}

    async def add_lead_to_campaign(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a lead to an Instantly campaign
        """
        campaign_id = data.get("campaign_id")
        email = data.get("email")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/lead/add",
                    params={"api_key": self.api_key},
                    headers=self.headers,
                    json={
                        "campaign_id": campaign_id,
                        "email": email,
                        "first_name": data.get("first_name", ""),
                        "last_name": data.get("last_name", ""),
                        "company_name": data.get("company_name", ""),
                        "personalization": data.get("variables", {}),
                        "skip_if_in_workspace": True
                    }
                )
                response.raise_for_status()
                result = response.json()
                return {
                    "success": True,
                    "lead_id": result.get("id"),
                    "status": "added"
                }
        except Exception as e:
            logger.error("Instantly add_lead failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def get_campaign_analytics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get analytics for a campaign
        """
        campaign_id = params.get("campaign_id")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/campaign/summary",
                    params={"api_key": self.api_key, "campaign_id": campaign_id},
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()
                return {
                    "success": True,
                    "campaign_id": campaign_id,
                    "analytics": result
                }
        except Exception as e:
            logger.error("Instantly get_campaign_analytics failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def list_campaigns(self) -> Dict[str, Any]:
        """
        List all campaigns
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/campaign/list",
                    params={"api_key": self.api_key},
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()
                return {
                    "success": True,
                    "campaigns": result
                }
        except Exception as e:
            logger.error("Instantly list_campaigns failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def check_replies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for replies to follow up on
        """
        campaign_id = params.get("campaign_id")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/lead/replies",
                    params={"api_key": self.api_key, "campaign_id": campaign_id},
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()
                return {
                    "success": True,
                    "replies": result
                }
        except Exception as e:
            logger.error("Instantly check_replies failed", error=str(e))
            return {"success": False, "error": str(e)}
