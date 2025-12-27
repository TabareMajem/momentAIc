"""
Notion Integration
Workspace documentation and databases
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.integrations.base import BaseIntegration, IntegrationCredentials, SyncResult
from app.core.config import settings

logger = structlog.get_logger()


class NotionIntegration(BaseIntegration):
    """
    Notion integration for workspace data
    
    Data types:
    - databases: Notion databases
    - pages: Notion pages
    
    Actions:
    - create_page: Create a new page
    - query_database: Query database entries
    """
    
    provider = "notion"
    display_name = "Notion"
    description = "Sync databases and pages from Notion"
    oauth_required = True
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.base_url = "https://api.notion.com/v1"
        self.client_id = getattr(settings, 'notion_client_id', None)
        self.client_secret = getattr(settings, 'notion_client_secret', None)
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate Notion OAuth URL"""
        return (
            f"https://api.notion.com/v1/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&owner=user"
            f"&state={state}"
        )
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        """Exchange authorization code for access token"""
        import base64
        
        try:
            # Notion uses Basic auth for token exchange
            auth = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            response = await self.http_client.post(
                "https://api.notion.com/v1/oauth/token",
                json={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "application/json",
                },
            )
            
            data = response.json()
            
            if "error" in data:
                raise Exception(data.get("error", "OAuth failed"))
            
            return IntegrationCredentials(
                access_token=data.get("access_token"),
            )
        except Exception as e:
            logger.error("Notion token exchange failed", error=str(e))
            raise
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        """Notion tokens don't expire"""
        return self.credentials
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        """Sync data from Notion"""
        if not self.credentials.access_token:
            return SyncResult(success=False, errors=["No access token"])
        
        data_types = data_types or ["databases", "pages"]
        
        try:
            result_data = {}
            records = 0
            
            if "databases" in data_types:
                databases = await self._search_databases()
                result_data["databases"] = databases
                records += len(databases)
            
            if "pages" in data_types:
                pages = await self._search_pages()
                result_data["pages"] = pages
                records += len(pages)
            
            return SyncResult(
                success=True,
                records_synced=records,
                data=result_data
            )
        except Exception as e:
            logger.error("Notion sync failed", error=str(e))
            return SyncResult(success=False, errors=[str(e)])
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Notion actions"""
        actions = {
            "create_page": self._create_page,
            "query_database": self._query_database,
        }
        
        if action not in actions:
            return {"error": f"Unknown action: {action}"}
        
        return await actions[action](params)
    
    async def _search_databases(self) -> List[Dict[str, Any]]:
        """Search for databases"""
        try:
            response = await self.http_client.post(
                f"{self.base_url}/search",
                json={
                    "filter": {"property": "object", "value": "database"},
                    "page_size": 100,
                },
                headers={
                    "Authorization": f"Bearer {self.credentials.access_token}",
                    "Notion-Version": "2022-06-28",
                },
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            return [
                {
                    "id": db["id"],
                    "title": db.get("title", [{}])[0].get("plain_text", "Untitled"),
                    "url": db.get("url"),
                }
                for db in data.get("results", [])
            ]
        except Exception as e:
            logger.error("Failed to search databases", error=str(e))
            return []
    
    async def _search_pages(self) -> List[Dict[str, Any]]:
        """Search for pages"""
        try:
            response = await self.http_client.post(
                f"{self.base_url}/search",
                json={
                    "filter": {"property": "object", "value": "page"},
                    "page_size": 100,
                },
                headers={
                    "Authorization": f"Bearer {self.credentials.access_token}",
                    "Notion-Version": "2022-06-28",
                },
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            return [
                {
                    "id": page["id"],
                    "title": self._get_page_title(page),
                    "url": page.get("url"),
                    "last_edited": page.get("last_edited_time"),
                }
                for page in data.get("results", [])
            ]
        except Exception as e:
            logger.error("Failed to search pages", error=str(e))
            return []
    
    def _get_page_title(self, page: Dict) -> str:
        """Extract page title"""
        props = page.get("properties", {})
        for prop in props.values():
            if prop.get("type") == "title":
                title_array = prop.get("title", [])
                if title_array:
                    return title_array[0].get("plain_text", "Untitled")
        return "Untitled"
    
    async def _create_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new page"""
        parent_id = params.get("parent_id")
        title = params.get("title", "New Page")
        content = params.get("content", "")
        
        if not parent_id:
            return {"error": "parent_id required (database or page ID)"}
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/pages",
                json={
                    "parent": {"database_id": parent_id},
                    "properties": {
                        "Name": {"title": [{"text": {"content": title}}]},
                    },
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"text": {"content": content}}]
                            }
                        }
                    ] if content else [],
                },
                headers={
                    "Authorization": f"Bearer {self.credentials.access_token}",
                    "Notion-Version": "2022-06-28",
                },
            )
            
            if response.status_code not in [200, 201]:
                return {"error": "Failed to create page"}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def _query_database(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query a database"""
        database_id = params.get("database_id")
        
        if not database_id:
            return {"error": "database_id required"}
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/databases/{database_id}/query",
                json={"page_size": params.get("limit", 100)},
                headers={
                    "Authorization": f"Bearer {self.credentials.access_token}",
                    "Notion-Version": "2022-06-28",
                },
            )
            
            if response.status_code != 200:
                return {"error": "Failed to query database"}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_supported_data_types(self) -> List[str]:
        return ["databases", "pages"]
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            {"name": "create_page", "description": "Create a new page"},
            {"name": "query_database", "description": "Query database entries"},
        ]
