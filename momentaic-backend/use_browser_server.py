
import asyncio
import os
import sys

# Ensure app is in path
sys.path.append(os.getcwd())

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    print("Starting client...")
    server_params = StdioServerParameters(
        command="python3",
        args=["/root/momentaic/momentaic-backend/servers/browser/server.py"],
        env=os.environ.copy()
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # List tools
                tools = await session.list_tools()
                print(f"Tools available: {[t.name for t in tools.tools]}")

                # Call tool
                print("Calling browse_page...")
                result = await session.call_tool("browse_page", {"url": "https://example.com"})
                
                content = result.content[0].text
                print(f"Tool Result Preview: {content[:100]}...")
                print("Success!")
                
    except Exception as e:
        print(f"Client failed: {e}")

if __name__ == "__main__":
    asyncio.run(run())
