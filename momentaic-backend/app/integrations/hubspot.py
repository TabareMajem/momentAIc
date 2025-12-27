"""
HubSpot CRM Integration
Customer and deal management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.integrations.base import BaseIntegration, IntegrationCredentials, SyncResult
from app.core.config import settings

logger = structlog.get_logger()


class HubSpotIntegration(BaseIntegration):
    """
    HubSpot integration for CRM data
    
    Data types:
    - contacts: Customer contacts
    - companies: Company records
    - deals: Sales deals/pipeline
    
    Actions:
    - create_contact: Create a new contact
    - create_deal: Create a new deal
    - update_deal: Update deal stage
    """
    
    provider = "hubspot"
    display_name = "HubSpot"
    description = "Sync contacts, companies, and deals from HubSpot CRM"
    oauth_required = True
    
    default_scopes = [
        "crm.objects.contacts.read",
        "crm.objects.contacts.write",
        "crm.objects.companies.read",
        "crm.objects.deals.read",
        "crm.objects.deals.write",
    ]
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.base_url = "https://api.hubapi.com"
        self.client_id = getattr(settings, 'hubspot_client_id', None)
        self.client_secret = getattr(settings, 'hubspot_client_secret', None)
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate HubSpot OAuth URL"""
        scopes = " ".join(self.default_scopes)
        return (
            f"https://app.hubspot.com/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
        )
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        """Exchange authorization code for access token"""
        try:
            response = await self.http_client.post(
                "https://api.hubapi.com/oauth/v1/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
            
            data = response.json()
            
            if "error" in data:
                raise Exception(data.get("error_description", "OAuth failed"))
            
            expires_at = datetime.utcnow()
            if "expires_in" in data:
                from datetime import timedelta
                expires_at += timedelta(seconds=data["expires_in"])
            
            return IntegrationCredentials(
                access_token=data.get("access_token"),
                refresh_token=data.get("refresh_token"),
                expires_at=expires_at,
            )
        except Exception as e:
            logger.error("HubSpot token exchange failed", error=str(e))
            raise
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        """Refresh expired tokens"""
        try:
            response = await self.http_client.post(
                "https://api.hubapi.com/oauth/v1/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.credentials.refresh_token,
                },
            )
            
            data = response.json()
            
            if "error" in data:
                raise Exception(data.get("error_description", "Refresh failed"))
            
            expires_at = datetime.utcnow()
            if "expires_in" in data:
                from datetime import timedelta
                expires_at += timedelta(seconds=data["expires_in"])
            
            return IntegrationCredentials(
                access_token=data.get("access_token"),
                refresh_token=data.get("refresh_token"),
                expires_at=expires_at,
            )
        except Exception as e:
            logger.error("HubSpot token refresh failed", error=str(e))
            raise
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        """Sync CRM data from HubSpot"""
        if not self.credentials.access_token:
            return SyncResult(success=False, errors=["No access token"])
        
        await self.ensure_valid_token()
        
        data_types = data_types or ["contacts", "companies", "deals"]
        
        try:
            result_data = {}
            records = 0
            
            if "contacts" in data_types:
                contacts = await self._get_contacts()
                result_data["contacts"] = contacts
                records += len(contacts.get("results", []))
            
            if "companies" in data_types:
                companies = await self._get_companies()
                result_data["companies"] = companies
                records += len(companies.get("results", []))
            
            if "deals" in data_types:
                deals = await self._get_deals()
                result_data["deals"] = deals
                records += len(deals.get("results", []))
            
            return SyncResult(
                success=True,
                records_synced=records,
                data=result_data
            )
        except Exception as e:
            logger.error("HubSpot sync failed", error=str(e))
            return SyncResult(success=False, errors=[str(e)])
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HubSpot actions"""
        actions = {
            "create_contact": self._create_contact,
            "create_deal": self._create_deal,
            "update_deal": self._update_deal,
        }
        
        if action not in actions:
            return {"error": f"Unknown action: {action}"}
        
        return await actions[action](params)
    
    async def _get_contacts(self, limit: int = 100) -> Dict[str, Any]:
        """Get contacts"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/crm/v3/objects/contacts",
                params={
                    "limit": limit,
                    "properties": "email,firstname,lastname,company,phone",
                },
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            if response.status_code != 200:
                return {"results": [], "total": 0}
            
            data = response.json()
            return {
                "results": [
                    {
                        "id": c["id"],
                        "email": c.get("properties", {}).get("email"),
                        "name": f"{c.get('properties', {}).get('firstname', '')} {c.get('properties', {}).get('lastname', '')}".strip(),
                        "company": c.get("properties", {}).get("company"),
                    }
                    for c in data.get("results", [])
                ],
                "total": data.get("total", 0),
            }
        except Exception as e:
            logger.error("Failed to get contacts", error=str(e))
            return {"results": [], "total": 0}
    
    async def _get_companies(self, limit: int = 100) -> Dict[str, Any]:
        """Get companies"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/crm/v3/objects/companies",
                params={
                    "limit": limit,
                    "properties": "name,domain,industry,numberofemployees",
                },
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            if response.status_code != 200:
                return {"results": [], "total": 0}
            
            data = response.json()
            return {
                "results": [
                    {
                        "id": c["id"],
                        "name": c.get("properties", {}).get("name"),
                        "domain": c.get("properties", {}).get("domain"),
                        "industry": c.get("properties", {}).get("industry"),
                    }
                    for c in data.get("results", [])
                ],
                "total": data.get("total", 0),
            }
        except Exception as e:
            logger.error("Failed to get companies", error=str(e))
            return {"results": [], "total": 0}
    
    async def _get_deals(self, limit: int = 100) -> Dict[str, Any]:
        """Get deals"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/crm/v3/objects/deals",
                params={
                    "limit": limit,
                    "properties": "dealname,dealstage,amount,closedate",
                },
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            if response.status_code != 200:
                return {"results": [], "total": 0}
            
            data = response.json()
            return {
                "results": [
                    {
                        "id": d["id"],
                        "name": d.get("properties", {}).get("dealname"),
                        "stage": d.get("properties", {}).get("dealstage"),
                        "amount": d.get("properties", {}).get("amount"),
                    }
                    for d in data.get("results", [])
                ],
                "total": data.get("total", 0),
            }
        except Exception as e:
            logger.error("Failed to get deals", error=str(e))
            return {"results": [], "total": 0}
    
    async def _create_contact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact"""
        try:
            response = await self.http_client.post(
                f"{self.base_url}/crm/v3/objects/contacts",
                json={
                    "properties": {
                        "email": params.get("email"),
                        "firstname": params.get("first_name"),
                        "lastname": params.get("last_name"),
                        "company": params.get("company"),
                    }
                },
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            if response.status_code not in [200, 201]:
                return {"error": "Failed to create contact"}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def _create_deal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal"""
        try:
            response = await self.http_client.post(
                f"{self.base_url}/crm/v3/objects/deals",
                json={
                    "properties": {
                        "dealname": params.get("name"),
                        "dealstage": params.get("stage", "appointmentscheduled"),
                        "amount": params.get("amount"),
                    }
                },
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            if response.status_code not in [200, 201]:
                return {"error": "Failed to create deal"}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def _update_deal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a deal"""
        deal_id = params.get("deal_id")
        if not deal_id:
            return {"error": "deal_id required"}
        
        try:
            response = await self.http_client.patch(
                f"{self.base_url}/crm/v3/objects/deals/{deal_id}",
                json={
                    "properties": {
                        k: v for k, v in params.items()
                        if k not in ["deal_id"]
                    }
                },
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            if response.status_code != 200:
                return {"error": "Failed to update deal"}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_supported_data_types(self) -> List[str]:
        return ["contacts", "companies", "deals"]
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            {"name": "create_contact", "description": "Create a new contact"},
            {"name": "create_deal", "description": "Create a new deal"},
            {"name": "update_deal", "description": "Update deal stage/amount"},
        ]
