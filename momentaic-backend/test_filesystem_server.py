import sys
sys.stdout.reconfigure(line_buffering=True)
print("STARTING...", flush=True)

import asyncio
import os
from app.services.mcp_client import MCPClientService

PROJECT_ROOT = os.getcwd()

async def main():
    svc = MCPClientService()
    
    print("Connecting to Filesystem MCP server...", flush=True)
    try:
        await svc.connect_stdio_server(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", PROJECT_ROOT],
            env=None
        )
        print("Connected!", flush=True)
    except Exception as e:
        print(f"Connection failed: {e}", flush=True)
        await svc.cleanup()
        return

    # List tools
    print("\nListing tools...", flush=True)
    try:
        tools = await svc.list_tools("filesystem")
        print(f"Tools available: {len(tools)}", flush=True)
        for t in tools:
            print(f"  - {t.name}: {t.description[:80] if t.description else 'N/A'}", flush=True)
    except Exception as e:
        print(f"List tools failed: {e}", flush=True)

    # Test reading a file (read this script itself)
    target_file = os.path.join(PROJECT_ROOT, "test_filesystem_server.py")
    print(f"\nReading file: {target_file}...", flush=True)
    try:
        # Note: filesystem server usually has 'read_file' or similar
        # Let's check tool names first
        if any(t.name == "read_file" for t in tools):
            result = await svc.call_tool("filesystem", "read_file", {
                "path": target_file
            })
            print(f"Read Result Length: {len(str(result))}", flush=True)
            print(f"Snippet: {str(result)[:100]}", flush=True)
        else:
            print("Tool 'read_file' not found.", flush=True)
    except Exception as e:
        print(f"Read failed: {e}", flush=True)

    await svc.cleanup()
    print("\nDone!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
