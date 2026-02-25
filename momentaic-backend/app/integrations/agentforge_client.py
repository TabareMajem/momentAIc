"""
AgentForge Client Integration
Connects to the AgentForge API for complex multi-agent orchestration.
"""

import httpx
import structlog
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = structlog.get_logger()

class AgentForgeClient:
    """Client for interoperability with AgentForge network"""
    
    def __init__(self):
        self.base_url = getattr(settings, "agentforge_api_url", "https://api.agentforgeai.com/api/v1")
        self.api_key = getattr(settings, "agentforge_api_key", None)
        self.timeout = 60.0
    
    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    async def orchestrate(self, task: str, context: Dict[str, Any] = None, user_id: str = None) -> Dict[str, Any]:
        """
        Request AgentForge to orchestrate a complex workflow.
        """
        if not self.api_key:
            return {"success": False, "error": "AgentForge API key missing"}
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/orchestrate",
                    json={
                        "task": task,
                        "context": context or {},
                        "user_id": user_id,
                        "source": "momentaic",
                    },
                    headers=self.headers
                )
                response.raise_for_status()
                return {"success": True, "result": response.json()}
        except Exception as e:
            logger.error("AgentForge orchestration failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def list_agents(self) -> List[Dict[str, Any]]:
        """
        List available specialized agents on the AgentForge network.
        """
        if not self.api_key:
            return []
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/agents", headers=self.headers)
                response.raise_for_status()
                return response.json().get("agents", [])
        except Exception as e:
            logger.error("AgentForge list_agents failed", error=str(e))
            return []

    async def get_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a previously submitted orchestration job.
        """
        if not self.api_key:
            return {"status": "error", "error": "API key missing"}
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/jobs/{job_id}", headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"AgentForge get_status failed for {job_id}", error=str(e))
            return {"status": "error", "error": str(e)}

# Singleton client
agentforge_client = AgentForgeClient()
