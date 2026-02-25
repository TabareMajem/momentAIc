
import sys
sys.stdout.reconfigure(line_buffering=True)
print("STARTING SCRIPT...", flush=True)

import asyncio
import os
import structlog
print("Importing app.services.mcp_client...", flush=True)
from app.services.mcp_client import mcp_service
print("Import complete.", flush=True)

# Configure logging
structlog.configure(
    processors=[structlog.processors.JSONRenderer()],
    logger_factory=structlog.PrintLoggerFactory(),
)

async def main():
    print("--- Testing Google MCP Server ---")
    
    cwd = os.getcwd()
    google_script = os.path.join(cwd, "servers/google/server.py")
    
    if not os.path.exists(google_script):
        print(f"Error: Script not found at {google_script}")
        return

    try:
        # Connect
        print("Connecting...")
        await mcp_service.connect_stdio_server(
            name="google",
            command="python3",
            args=[google_script],
            env={**os.environ}
        )
        print("Connected!")
        
        # List Tools
        print("\nListing Tools...")
        tools = await mcp_service.list_tools("google")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
            
        # Call Gmail Tool
        print("\nCalling list_gmail_messages...")
        gmail_result = await mcp_service.call_tool("google", "list_gmail_messages", {"max_results": 3})
        print(f"Gmail Result:\n{gmail_result.content[0].text}")

        # Call Calendar Tool
        print("\nCalling list_calendar_events...")
        calendar_result = await mcp_service.call_tool("google", "list_calendar_events", {"max_results": 3})
        print(f"Calendar Result:\n{calendar_result.content[0].text}")
        
    except Exception as e:
        print(f"\n❌ Failed: {e}")
    finally:
        await mcp_service.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
