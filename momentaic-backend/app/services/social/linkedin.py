"""
LinkedIn Service - Real Posting via LinkedIn Marketing API
Uses OAuth 2.0 for user authentication
"""

import httpx
import structlog
from typing import Dict, Any
from urllib.parse import urlencode

from app.core.config import settings

logger = structlog.get_logger()

class LinkedInService:
    """
    Handles LinkedIn OAuth 2.0 and posting via Marketing API.
    """
    
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
    SHARE_URL = "https://api.linkedin.com/v2/ugcPosts"
    
    def __init__(self):
        self.client_id = settings.linkedin_client_id
        self.client_secret = settings.linkedin_client_secret
        self.redirect_uri = f"{settings.cors_origins[0]}/api/v1/social/callback/linkedin" if settings.cors_origins else "http://localhost:8000/api/v1/social/callback/linkedin"
        
    def generate_auth_url(self, state: str = None) -> Dict[str, str]:
        """
        Generate LinkedIn OAuth 2.0 authorization URL.
        """
        import secrets
        state = state or secrets.token_urlsafe(16)
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile email w_member_social",
            "state": state,
        }
        
        auth_url = f"{self.AUTH_URL}?{urlencode(params)}"
        
        return {
            "auth_url": auth_url,
            "state": state
        }
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error("LinkedIn token exchange failed", status=response.status_code, body=response.text)
                return {"error": response.text}
                
            tokens = response.json()
            return {
                "access_token": tokens.get("access_token"),
                "expires_in": tokens.get("expires_in"),
                "scope": tokens.get("scope"),
            }
    
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get the authenticated user's LinkedIn profile (needed for posting).
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                return {"error": response.text}
                
            return response.json()
    
    async def share_post(self, content: str, creds: Dict[str, str]) -> Dict[str, Any]:
        """
        Post to LinkedIn using the user's access token.
        This is the REAL posting method.
        """
        access_token = creds.get("access_token")
        
        if not access_token:
            return {"success": False, "error": "No access token provided"}
        
        # Get user's LinkedIn URN (required for posting as that user)
        # The user_id should be stored during OAuth callback
        user_urn = creds.get("user_urn")
        
        if not user_urn:
            # Try to get it from profile
            profile = await self.get_user_profile(access_token)
            if "error" in profile:
                return {"success": False, "error": profile["error"]}
            user_urn = f"urn:li:person:{profile.get('sub')}"
        
        # Construct the UGC Post payload
        payload = {
            "author": user_urn,
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
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.SHARE_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                json=payload
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                post_id = data.get("id", "unknown")
                logger.info("LinkedIn post created successfully", post_id=post_id)
                return {
                    "success": True,
                    "id": post_id,
                    "url": f"https://www.linkedin.com/feed/update/{post_id}",
                    "platform": "linkedin"
                }
            else:
                logger.error("LinkedIn posting failed", status=response.status_code, body=response.text)
                return {"success": False, "error": response.text}


linkedin_service = LinkedInService()
