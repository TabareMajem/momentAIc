"""
Yokaizen Client Integration
Connects to the Yokaizen API for Sales, Marketing, and Ops swarm automation.
"""

import httpx
import structlog
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = structlog.get_logger()

class YokaizenClient:
    """Client for interoperability with Yokaizen swarms"""
    
    def __init__(self):
        self.base_url = getattr(settings, "yokaizen_api_url", "https://ai.yokaizen.com/api/v1")
        self.api_key = getattr(settings, "yokaizen_api_key", None)
        self.timeout = 60.0
    
    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    async def execute_task(self, task: str, swarm_type: str, context: Dict[str, Any] = None, user_id: str = None) -> Dict[str, Any]:
        """
        Request Yokaizen to execute a task using a specific swarm (e.g., sales, marketing).
        """
        if not self.api_key:
            return {"success": False, "error": "Yokaizen API key missing"}
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/swarm/dispatch",
                    json={
                        "task": task,
                        "swarm_type": swarm_type,
                        "context": context or {},
                        "user_id": user_id,
                        "source": "momentaic",
                    },
                    headers=self.headers
                )
                response.raise_for_status()
                return {"success": True, "result": response.json()}
        except Exception as e:
            logger.error("Yokaizen execute_task failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def get_agents(self) -> List[Dict[str, Any]]:
        """
        List available operative agents within Yokaizen.
        """
        if not self.api_key:
            return []
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/agents", headers=self.headers)
                response.raise_for_status()
                return response.json().get("swarms", [])
        except Exception as e:
            logger.error("Yokaizen get_agents failed", error=str(e))
            return []

    async def sync_data(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize cross-platform intelligence data to Yokaizen.
        """
        if not self.api_key:
            return {"success": False, "error": "API key missing"}
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/data/sync",
                    json=dataset,
                    headers=self.headers
                )
                response.raise_for_status()
                return {"success": True, "result": response.json()}
        except Exception as e:
            logger.error("Yokaizen sync_data failed", error=str(e))
            return {"success": False, "error": str(e)}

# Singleton client
yokaizen_client = YokaizenClient()
