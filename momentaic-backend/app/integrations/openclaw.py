from typing import Dict, Any, List, Optional
import httpx
import structlog
import asyncio
from app.integrations.base import BaseIntegration, SyncResult
from app.core.config import settings

logger = structlog.get_logger()

class OpenClawIntegration(BaseIntegration):
    """
    Integration with OpenClaw Execution Node.
    Acts as the "Hands" of the system.
    
    Protocol:
    - Navigation: POST /tabs/open -> returns targetId
    - Scraping: GET /snapshot?targetId=...&format=ai
    - Interactions: POST /act -> {kind: "click", targetId: ..., ref: ...}
    """
    
    provider = "openclaw"
    display_name = "OpenClaw Browser Node"
    description = "Remote browser automation and execution node"
    oauth_required = False

    def __init__(self, credentials=None, config=None):
        super().__init__(credentials, config)
        self.base_url = settings.openclaw_api_url or "http://localhost:18789"
        self.api_key = settings.openclaw_api_key
        self.current_target_id: Optional[str] = None
        
        # OpenClaw doesn't typically need auth for local nodes, but supports it
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Not used for API Key auth"""
        return ""

    async def exchange_code(self, code: str, redirect_uri: str):
        """Not used for API Key auth"""
        return None

    async def refresh_tokens(self):
        """Not used for API Key auth"""
        return None

    async def _ensure_session(self) -> str:
        """
        Ensures we have an active browser tab/session.
        If no target_id is set, it opens a new blank tab.
        """
        if self.current_target_id:
            return self.current_target_id
            
        return await self.open_tab("about:blank")

    async def open_tab(self, url: str) -> str:
        """Opens a new tab and sets it as the current session"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/tabs/open",
                    json={"url": url},
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                self.current_target_id = data.get("targetId")
                return self.current_target_id
        except Exception as e:
            logger.error("OpenClaw: Failed to open tab", error=str(e))
            raise e

    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        """
        Check node health/status.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # /profiles is a good health check endpoint
                response = await client.get(f"{self.base_url}/profiles", headers=self.headers)
            
            if response.status_code == 200:
                return SyncResult(
                    success=True,
                    items_synced=1,
                    details={"status": "connected", "profiles": response.json().get("profiles", [])}
                )
            return SyncResult(success=False, error=f"Status {response.status_code}")
        except Exception as e:
            return SyncResult(success=False, error=str(e))

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute browser actions using the OpenClaw /act protocol.
        """
        if not self.base_url:
            return {"error": "OpenClaw API URL not configured"}

        # Auto-manage session if not provided
        target_id = params.get("targetId") or self.current_target_id
        
        try:
            # 1. NAVIGATION (Maps to /tabs/open)
            if action == "browser_navigate":
                url = params.get("url")
                if not url:
                    return {"success": False, "error": "URL required"}
                
                new_target_id = await self.open_tab(url)
                
                # After nav, typically wait for load
                if params.get("wait_for"):
                     await self._act("wait", {"targetId": new_target_id, "selector": params["wait_for"]})

                # Return the snapshot immediately for efficiency
                snapshot = await self._get_snapshot(new_target_id)
                return {
                    "success": True,
                    "targetId": new_target_id,
                    "url": url,
                    "snapshot": snapshot
                }

            # 2. SCRAPING (Maps to /snapshot)
            elif action == "browser_scrape":
                if not target_id:
                    target_id = await self._ensure_session()
                
                snapshot = await self._get_snapshot(target_id)
                return {
                    "success": True, 
                    "targetId": target_id,
                    "content": snapshot
                }

            # 3. INTERACTION (Maps to /act)
            elif action == "browser_act":
                if not target_id:
                    target_id = await self._ensure_session()
                
                kind = params.get("kind", "click") # click, type, etc.
                act_params = {
                    "targetId": target_id, 
                    "kind": kind,
                    **params # Pass specific params like 'ref', 'text', 'keys'
                }
                
                result = await self._act(kind, act_params)
                
                # Return refreshed snapshot after action
                new_snapshot = await self._get_snapshot(target_id)
                return {
                    "success": True,
                    "action_result": result,
                    "snapshot": new_snapshot
                }

            # 4. SYSTEM (Maps to /system/exec - if enabled on node)
            elif action == "system_command":
                # Only strictly controlled commands
                cmd = params.get("command")
                return {"success": False, "error": "System commands temporarily disabled for safety in V2"}

            else:
                return {"success": False, "error": f"Unknown OpenClaw action: {action}"}

        except Exception as e:
            logger.error("OpenClaw action failed", action=action, error=str(e))
            return {"success": False, "error": str(e)}

    # --- Internal Helpers ---

    async def _act(self, kind: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generic handler for /act endpoint"""
        payload = {"kind": kind, **params}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/act",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def _get_snapshot(self, target_id: str) -> Dict[str, Any]:
        """Get AI-formatted snapshot"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/snapshot",
                params={"targetId": target_id, "format": "ai", "interactive": "true"},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
