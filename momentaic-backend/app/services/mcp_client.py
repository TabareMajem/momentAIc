
import asyncio
import os
import structlog
from contextlib import AsyncExitStack
from typing import Dict, Any, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = structlog.get_logger()

class MCPClientService:
    """
    Manages connections to MCP Servers.
    Acts as the 'Host' for the Model Context Protocol.
    """
    
    def __init__(self):
        self._exit_stack = AsyncExitStack()
        self._sessions: Dict[str, ClientSession] = {}
        
    async def connect_stdio_server(self, name: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        """Connect to a local MCP server running via stdio."""
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        
        try:
            stdio_transport = await self._exit_stack.enter_async_context(stdio_client(server_params))
            session = await self._exit_stack.enter_async_context(ClientSession(stdio_transport[0], stdio_transport[1]))
            await session.initialize()
            
            self._sessions[name] = session
            logger.info("Connected to MCP Server", name=name)
            return session
            
        except Exception as e:
            logger.error("Failed to connect to MCP Server", name=name, error=str(e))
            raise e

    async def list_tools(self, server_name: str):
        """List tools available on a connected server."""
        session = self._sessions.get(server_name)
        if not session:
            raise ValueError(f"Server {server_name} not connected")
            
        result = await session.list_tools()
        return result.tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
        """Call a tool on a connected server."""
        session = self._sessions.get(server_name)
        if not session:
            raise ValueError(f"Server {server_name} not connected")
            
        result = await session.call_tool(tool_name, arguments)
        return result

    async def cleanup(self):
        """Close all connections."""
        await self._exit_stack.aclose()
        self._sessions.clear()

# Global instance
mcp_service = MCPClientService()
