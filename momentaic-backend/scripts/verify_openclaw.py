import asyncio
import sys
import os

# Add project root to path
sys.path.append("/root/momentaic/momentaic-backend")

from app.services.mcp_registry import get_mcp_registry
from app.integrations import OpenClawIntegration

async def verify():
    print("Verifying OpenClaw Integration...")
    
    # 1. Check Integration Class
    claw = OpenClawIntegration()
    print(f"Integration initialized: {claw.display_name}")
    
    # 2. Check MCP Registry
    registry = get_mcp_registry()
    print("MCP Registry loaded.")
    
    tools = registry.list_tools()
    openclaw_tools = [t for t in tools if "OpenClaw" in t.get("name") or "OpenClaw" in t.get("description", "")]
    
    print(f"Found {len(openclaw_tools)} OpenClaw-related tools.")
    for tool in openclaw_tools:
        print(f" - {tool['name']}: {tool['description']}")

    # 3. Check alias routing
    print("\nChecking aliases:")
    aliases = ["browser_navigate", "browser_scrape", "system_command"]
    for alias in aliases:
        tool = registry.get_tool(alias)
        if tool:
            print(f" - Alias '{alias}' found.")
        else:
            print(f" - Alias '{alias}' NOT found!")

    print("\nVerification Complete.")

if __name__ == "__main__":
    asyncio.run(verify())
