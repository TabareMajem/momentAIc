"""
LinkedIn Integration - OAuth & Social Posting
Enables agents to post content on behalf of users
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode
import structlog

from app.integrations.base import BaseIntegration, IntegrationCredentials, SyncResult
from app.core.config import settings

logger = structlog.get_logger()


class LinkedInIntegration(BaseIntegration):
    """
    LinkedIn Integration for MomentAIc
    
    Capabilities:
    - OAuth 2.0 authentication
    - Post text content
    - Post with images
    - Share articles
    - Get profile info
    """
    
    provider = "linkedin"
    display_name = "LinkedIn"
    description = "Post content and engage with your professional network"
    oauth_required = True
    
    # LinkedIn OAuth scopes for posting
    default_scopes = [
        "openid",
        "profile",
        "w_member_social",  # Required for posting
    ]
    
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_BASE = "https://api.linkedin.com/v2"
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate LinkedIn OAuth authorization URL"""
        params = {
            "response_type": "code",
            "client_id": settings.linkedin_client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": " ".join(self.default_scopes),
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        """Exchange authorization code for tokens"""
        response = await self.http_client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.linkedin_client_id,
                "client_secret": settings.linkedin_client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        
        if response.status_code != 200:
            logger.error("LinkedIn token exchange failed", status=response.status_code, body=response.text)
            raise Exception(f"Token exchange failed: {response.text}")
        
        data = response.json()
        
        return IntegrationCredentials(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600)),
        )
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        """LinkedIn tokens don't support refresh - user must re-auth"""
        # LinkedIn's refresh token support is limited
        # For now, return existing credentials
        logger.warning("LinkedIn token refresh not fully supported")
        return self.credentials
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        """Sync profile data from LinkedIn"""
        if not self.credentials.access_token:
            return SyncResult(success=False, errors=["Not authenticated"])
        
        try:
            # Get user profile
            profile_response = await self.http_client.get(
                f"{self.API_BASE}/userinfo",
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
            )
            
            if profile_response.status_code != 200:
                return SyncResult(success=False, errors=[profile_response.text])
            
            profile = profile_response.json()
            
            return SyncResult(
                success=True,
                records_synced=1,
                data={"profile": profile},
            )
        except Exception as e:
            logger.error("LinkedIn sync failed", error=str(e))
            return SyncResult(success=False, errors=[str(e)])
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LinkedIn actions"""
        if action == "post":
            return await self._create_post(params)
        elif action == "share_article":
            return await self._share_article(params)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    async def _create_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a text post on LinkedIn"""
        content = params.get("content", "")
        
        if not content:
            return {"success": False, "error": "Content is required"}
        
        if not self.credentials.access_token:
            return {"success": False, "error": "Not authenticated"}
        
        # Get user URN (required for posting)
        user_info = await self.http_client.get(
            f"{self.API_BASE}/userinfo",
            headers={"Authorization": f"Bearer {self.credentials.access_token}"},
        )
        
        if user_info.status_code != 200:
            return {"success": False, "error": "Failed to get user info"}
        
        user_data = user_info.json()
        author_urn = f"urn:li:person:{user_data.get('sub')}"
        
        # Create post
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = await self.http_client.post(
            f"{self.API_BASE}/ugcPosts",
            json=post_data,
            headers={
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            },
        )
        
        if response.status_code in [200, 201]:
            logger.info("LinkedIn post created successfully")
            return {"success": True, "post_id": response.headers.get("x-restli-id")}
        else:
            logger.error("LinkedIn post failed", status=response.status_code, body=response.text)
            return {"success": False, "error": response.text}
    
    async def _share_article(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Share an article on LinkedIn"""
        url = params.get("url", "")
        commentary = params.get("commentary", "")
        
        if not url:
            return {"success": False, "error": "URL is required"}
        
        # Similar to _create_post but with ARTICLE media category
        # Implementation would follow LinkedIn API documentation
        return {"success": False, "error": "Not implemented in this version"}
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            {
                "action": "post",
                "name": "Create Post",
                "description": "Create a text post on LinkedIn",
                "params": ["content"],
            },
            {
                "action": "share_article",
                "name": "Share Article",
                "description": "Share a URL with commentary",
                "params": ["url", "commentary"],
            },
        ]


# Singleton instance
linkedin_integration = LinkedInIntegration()
