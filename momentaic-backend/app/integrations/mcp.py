from typing import List, Dict, Any, Optional
import httpx
from app.integrations.base import BaseIntegration, SyncResult, IntegrationCredentials
import structlog

logger = structlog.get_logger()

class MCPIntegration(BaseIntegration):
    """
    Model Context Protocol (MCP) Integration Client
    Allows MomentAIc to communicate with any MCP-compliant server.
    """
    display_name = "MCP Connector"
    description = "Community-built Model Context Protocol integration"
    
    def __init__(self, credentials: IntegrationCredentials, config: Dict[str, Any]):
        super().__init__(credentials)
        self.server_url = config.get("server_url")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Discover tools available on the MCP server"""
        if not self.server_url:
            return []
        
        try:
            # MCP JSON-RPC: listTools
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            response = await self.client.post(self.server_url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("result", {}).get("tools", [])
        except Exception as e:
            logger.error("MCP tool discovery failed", url=self.server_url, error=str(e))
            return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on the MCP server"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            response = await self.client.post(self.server_url, json=payload)
            response.raise_for_status()
            return response.json().get("result", {})
        except Exception as e:
            logger.error("MCP tool execution failed", tool=tool_name, error=str(e))
            return {"error": str(e), "success": False}

    async def sync_data(self, data_types: Optional[List[str]] = None) -> SyncResult:
        """
        MCP servers can expose resources. We can sync resources if defined.
        For now, we'll implement a basic health check as sync.
        """
        tools = await self.list_tools()
        if tools:
            return SyncResult(
                success=True,
                records_synced=len(tools),
                data={"available_tools": [t["name"] for t in tools]}
            )
        return SyncResult(success=False, errors=["Could not list tools from MCP server"])

    async def close(self):
        await self.client.aclose()
