"""
Slack Integration
Team communication and notifications
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.integrations.base import BaseIntegration, IntegrationCredentials, SyncResult
from app.core.config import settings

logger = structlog.get_logger()


class SlackIntegration(BaseIntegration):
    """
    Slack integration for notifications and team data
    
    Data types:
    - channels: List of channels
    - messages: Recent messages
    - users: Team members
    
    Actions:
    - send_message: Post to a channel
    - send_dm: Send direct message
    """
    
    provider = "slack"
    display_name = "Slack"
    description = "Send notifications and monitor team activity"
    oauth_required = True
    
    default_scopes = [
        "channels:read",
        "channels:history",
        "chat:write",
        "users:read",
        "im:write",
    ]
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.base_url = "https://slack.com/api"
        self.client_id = getattr(settings, 'slack_client_id', None)
        self.client_secret = getattr(settings, 'slack_client_secret', None)
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate Slack OAuth URL"""
        scopes = ",".join(self.default_scopes)
        return (
            f"https://slack.com/oauth/v2/authorize"
            f"?client_id={self.client_id}"
            f"&scope={scopes}"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
        )
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        """Exchange authorization code for access token"""
        try:
            response = await self.http_client.post(
                f"{self.base_url}/oauth.v2.access",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
            
            data = response.json()
            
            if not data.get("ok"):
                raise Exception(data.get("error", "OAuth failed"))
            
            return IntegrationCredentials(
                access_token=data.get("access_token"),
            )
        except Exception as e:
            logger.error("Slack token exchange failed", error=str(e))
            raise
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        """Slack tokens don't expire by default"""
        return self.credentials
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        """Sync Slack data"""
        if not self.credentials.access_token:
            return SyncResult(success=False, errors=["No access token"])
        
        data_types = data_types or ["channels", "users"]
        
        try:
            result_data = {}
            records = 0
            
            if "channels" in data_types:
                channels = await self._get_channels()
                result_data["channels"] = channels
                records += 1
            
            if "users" in data_types:
                users = await self._get_users()
                result_data["users"] = users
                records += 1
            
            return SyncResult(
                success=True,
                records_synced=records,
                data=result_data
            )
        except Exception as e:
            logger.error("Slack sync failed", error=str(e))
            return SyncResult(success=False, errors=[str(e)])
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Slack actions"""
        actions = {
            "send_message": self._send_message,
            "send_dm": self._send_dm,
        }
        
        if action not in actions:
            return {"error": f"Unknown action: {action}"}
        
        return await actions[action](params)
    
    async def _get_channels(self) -> List[Dict[str, Any]]:
        """Get list of channels"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/conversations.list",
                params={"types": "public_channel,private_channel"},
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            data = response.json()
            
            if not data.get("ok"):
                return []
            
            return [
                {
                    "id": ch["id"],
                    "name": ch["name"],
                    "is_private": ch.get("is_private", False),
                    "member_count": ch.get("num_members", 0),
                }
                for ch in data.get("channels", [])
            ]
        except Exception as e:
            logger.error("Failed to get channels", error=str(e))
            return []
    
    async def _get_users(self) -> List[Dict[str, Any]]:
        """Get team members"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/users.list",
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            data = response.json()
            
            if not data.get("ok"):
                return []
            
            return [
                {
                    "id": user["id"],
                    "name": user.get("real_name", user.get("name")),
                    "email": user.get("profile", {}).get("email"),
                    "is_bot": user.get("is_bot", False),
                }
                for user in data.get("members", [])
                if not user.get("deleted")
            ]
        except Exception as e:
            logger.error("Failed to get users", error=str(e))
            return []
    
    async def _send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to a channel"""
        channel = params.get("channel")
        text = params.get("text")
        
        if not channel or not text:
            return {"error": "channel and text required"}
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/chat.postMessage",
                json={"channel": channel, "text": text},
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            data = response.json()
            
            if not data.get("ok"):
                return {"error": data.get("error", "Failed to send")}
            
            return {"success": True, "ts": data.get("ts")}
        except Exception as e:
            return {"error": str(e)}
    
    async def _send_dm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send direct message to a user"""
        user_id = params.get("user_id")
        text = params.get("text")
        
        if not user_id or not text:
            return {"error": "user_id and text required"}
        
        try:
            # Open DM channel
            response = await self.http_client.post(
                f"{self.base_url}/conversations.open",
                json={"users": user_id},
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            data = response.json()
            
            if not data.get("ok"):
                return {"error": "Failed to open DM"}
            
            channel = data["channel"]["id"]
            return await self._send_message({"channel": channel, "text": text})
        except Exception as e:
            return {"error": str(e)}
    
    def get_supported_data_types(self) -> List[str]:
        return ["channels", "users", "messages"]
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            {"name": "send_message", "description": "Post message to channel"},
            {"name": "send_dm", "description": "Send direct message"},
        ]
