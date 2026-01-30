import asyncio
import sys
import uvicorn
from fastapi import FastAPI, Body, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Mock OpenClaw Server
app = FastAPI()

class NavigateRequest(BaseModel):
    url: str

class ActRequest(BaseModel):
    kind: str
    targetId: Optional[str] = None
    ref: Optional[int] = None

@app.post("/tabs/open")
async def open_tab(req: NavigateRequest):
    print(f"[Server] Opening tab for {req.url}")
    return {"targetId": "tab-123", "success": True}

@app.get("/snapshot")
async def get_snapshot(targetId: str, format: str = "ai"):
    print(f"[Server] Getting snapshot for {targetId} (format={format})")
    # Return a mock AI snapshot
    return {
        "title": "Mock Page",
        "url": "http://mock.com",
        "role": "WebArea",
        "children": [
            {"role": "heading", "name": "Welcome to Mock Page"},
            {"role": "button", "name": "Click Me", "ref": 42}
        ]
    }

@app.post("/act")
async def act(req: Request):
    body = await req.json()
    print(f"[Server] Performing action: {body}")
    return {"success": True, "targetId": body.get("targetId")}

# --- Client Test Logic ---

async def run_client_test():
    """Run the client test against the mock server"""
    await asyncio.sleep(2) # Give server time to start
    
    print("\n\n--- Starting Client Test ---")
    
    # 1. Configure
    from app.core.config import settings
    # We must patch the URL to point to our local mock port
    # We must patch the URL to point to our local mock port
    settings.openclaw_api_url = "http://127.0.0.1:18790" 
    
    # 2. Initialize Integration
    from app.integrations.openclaw import OpenClawIntegration
    claw = OpenClawIntegration()
    claw.base_url = "http://127.0.0.1:18790" # Force override
    
    print(f"Testing against: {claw.base_url}")
    
    # 3. Test Navigation
    print("\n[Client] Testing Browser Navigate...")
    result = await claw.execute_action("browser_navigate", {
        "url": "http://example.com"
    })
    print(f"Result: {result}")
    assert result["success"] == True
    assert result["targetId"] == "tab-123"
    assert "snapshot" in result
    
    # 4. Test Interaction (Click)
    print("\n[Client] Testing Browser Interact (Click)...")
    result = await claw.execute_action("browser_act", {
        "kind": "click",
        "ref": 42,
        "targetId": "tab-123" # Explicit target
    })
    print(f"Result: {result}")
    assert result["success"] == True
    
    print("\n--- Test Completed Successfully ---")

async def main():
    # Start Server in background
    config = uvicorn.Config(app, host="127.0.0.1", port=18790, log_level="error")
    server = uvicorn.Server(config)
    
    server_task = asyncio.create_task(server.serve())
    
    try:
        await run_client_test()
    finally:
        server.should_exit = True
        await server_task

if __name__ == "__main__":
    # Add project root to path so we can import app modules
    sys.path.append("/root/momentaic/momentaic-backend")
    asyncio.run(main())
