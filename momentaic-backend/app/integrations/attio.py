"""
Attio CRM Integration
Sync leads, companies, and deals with the most flexible B2B CRM
"""

from typing import Dict, Any, List, Optional
from app.integrations.base import BaseIntegration, SyncResult
from app.core.config import settings
import structlog
import httpx

logger = structlog.get_logger()


class AttioIntegration(BaseIntegration):
    """
    Attio CRM Integration
    
    Capabilities:
    - sync_person: Create or update a person record
    - sync_company: Create or update a company record
    - update_status: Update deal/opportunity status
    - search_records: Search across Attio's flexible schema
    """
    
    provider = "attio"
    display_name = "Attio CRM"
    description = "Flexible, data-driven CRM for modern teams"
    oauth_required = False  # API Key based
    
    def __init__(self, credentials=None, config=None):
        super().__init__(credentials, config)
        self.api_key = settings.attio_api_key
        self.base_url = "https://api.attio.com/v2"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key or 'mock_key'}",
            "Content-Type": "application/json"
        }

    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        return ""

    async def exchange_code(self, code: str, redirect_uri: str):
        return None

    async def refresh_tokens(self):
        return None

    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        # Attio is push-based, not pull
        return SyncResult(success=True, records_synced=0)

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Attio actions
        
        Supported actions:
        - sync_person: { email, name, company_name, title, ... }
        - sync_company: { name, domain, industry, size, ... }
        - update_status: { record_id, status }
        - search_records: { object_type, query }
        """
        if action == "sync_person":
            return await self.sync_person(params)
        elif action == "sync_company":
            return await self.sync_company(params)
        elif action == "update_status":
            return await self.update_status(params)
        elif action == "search_records":
            return await self.search_records(params)
        
        return {"error": f"Unknown action: {action}"}

    async def sync_person(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a person in Attio
        Uses upsert by email
        """
        if not self.api_key or self.api_key == "mock_key":
            logger.info("Attio: Mocking person sync", email=data.get("email"))
            return {
                "success": True,
                "record_id": f"mock_person_{data.get('email', 'unknown').replace('@', '_')}",
                "action": "upserted",
                "data": data
            }
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Attio uses object-based API
                response = await client.post(
                    f"{self.base_url}/objects/people/records",
                    headers=self.headers,
                    json={
                        "data": {
                            "values": {
                                "email_addresses": [{"email_address": data.get("email")}],
                                "name": [{"first_name": data.get("first_name", ""), "last_name": data.get("last_name", "")}],
                                "job_title": [{"value": data.get("title", "")}],
                            }
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                return {
                    "success": True,
                    "record_id": result.get("id", {}).get("record_id"),
                    "action": "created",
                    "data": result
                }
        except Exception as e:
            logger.error("Attio sync_person failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def sync_company(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a company in Attio
        """
        if not self.api_key or self.api_key == "mock_key":
            logger.info("Attio: Mocking company sync", domain=data.get("domain"))
            return {
                "success": True,
                "record_id": f"mock_company_{data.get('domain', 'unknown')}",
                "action": "upserted",
                "data": data
            }
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/objects/companies/records",
                    headers=self.headers,
                    json={
                        "data": {
                            "values": {
                                "name": [{"value": data.get("name")}],
                                "domains": [{"domain": data.get("domain")}],
                            }
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                return {
                    "success": True,
                    "record_id": result.get("id", {}).get("record_id"),
                    "action": "created",
                    "data": result
                }
        except Exception as e:
            logger.error("Attio sync_company failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def update_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the status/stage of a record (e.g., deal stage)
        """
        if not self.api_key or self.api_key == "mock_key":
            return {
                "success": True,
                "record_id": params.get("record_id"),
                "new_status": params.get("status"),
                "mock": True
            }
        
        # Real implementation would use:
        # PATCH /objects/{object_slug}/records/{record_id}
        return {"error": "Real API implementation pending"}

    async def search_records(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search across Attio records
        """
        object_type = params.get("object_type", "companies")
        query = params.get("query", "")
        
        if not self.api_key or self.api_key == "mock_key":
            return {
                "success": True,
                "results": [
                    {"id": "mock_1", "name": f"Mock Result for {query}", "type": object_type}
                ],
                "mock": True
            }
        
        # Real implementation would use:
        # POST /objects/{object_slug}/records/query
        return {"error": "Real API implementation pending"}
