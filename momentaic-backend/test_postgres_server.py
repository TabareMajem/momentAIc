import sys
sys.stdout.reconfigure(line_buffering=True)
print("STARTING...", flush=True)

import asyncio
from app.services.mcp_client import MCPClientService

PG_URL = "postgresql://momentaic:17122f617a04c22b1821e4344aab9f8a@127.0.0.1:5432/momentaic"

async def main():
    svc = MCPClientService()
    
    print("Connecting to Postgres MCP server...", flush=True)
    try:
        await svc.connect_stdio_server(
            name="postgres",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-postgres", PG_URL],
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
        tools = await svc.list_tools("postgres")
        print(f"Tools available: {len(tools)}", flush=True)
        for t in tools:
            print(f"  - {t.name}: {t.description[:80] if t.description else 'N/A'}", flush=True)
    except Exception as e:
        print(f"List tools failed: {e}", flush=True)

    # Test a simple query
    print("\nQuerying database...", flush=True)
    try:
        result = await svc.call_tool("postgres", "query", {
            "sql": "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename LIMIT 20;"
        })
        print(f"Query Result:\n{result}", flush=True)
    except Exception as e:
        print(f"Query failed: {e}", flush=True)

    await svc.cleanup()
    print("\nDone!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
