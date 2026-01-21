"""
Twitter Service - Real Posting via Twitter API v2
Uses OAuth 2.0 with PKCE for user authentication
"""

import httpx
import structlog
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import secrets
import hashlib
import base64

from app.core.config import settings

logger = structlog.get_logger()

class TwitterService:
    """
    Handles Twitter OAuth 2.0 and posting via API v2.
    """
    
    AUTH_URL = "https://twitter.com/i/oauth2/authorize"
    TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
    TWEET_URL = "https://api.twitter.com/2/tweets"
    
    def __init__(self):
        self.client_id = settings.twitter_client_id
        self.client_secret = settings.twitter_client_secret
        self.redirect_uri = f"{settings.cors_origins[0]}/api/v1/social/callback/twitter" if settings.cors_origins else "http://localhost:8000/api/v1/social/callback/twitter"
        
    def generate_auth_url(self, state: str = None) -> Dict[str, str]:
        """
        Generate Twitter OAuth 2.0 authorization URL with PKCE.
        Returns the URL and the code_verifier (must be stored in session).
        """
        # PKCE: Generate code_verifier and code_challenge
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        
        state = state or secrets.token_urlsafe(16)
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "tweet.read tweet.write users.read offline.access",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        
        auth_url = f"{self.AUTH_URL}?{urlencode(params)}"
        
        return {
            "auth_url": auth_url,
            "code_verifier": code_verifier,
            "state": state
        }
    
    async def exchange_code_for_tokens(self, code: str, code_verifier: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "code_verifier": code_verifier,
                    "client_id": self.client_id,
                },
                auth=(self.client_id, self.client_secret) if self.client_secret else None,
            )
            
            if response.status_code != 200:
                logger.error("Twitter token exchange failed", status=response.status_code, body=response.text)
                return {"error": response.text}
                
            tokens = response.json()
            return {
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "expires_in": tokens.get("expires_in"),
                "scope": tokens.get("scope"),
            }
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                },
            )
            
            if response.status_code != 200:
                logger.error("Twitter token refresh failed", body=response.text)
                return {"error": response.text}
                
            return response.json()
    
    async def tweet(self, content: str, creds: Dict[str, str]) -> Dict[str, Any]:
        """
        Post a tweet using the user's access token.
        This is the REAL posting method.
        """
        access_token = creds.get("access_token")
        
        if not access_token:
            return {"success": False, "error": "No access token provided"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TWEET_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={"text": content}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                tweet_id = data.get("data", {}).get("id")
                logger.info("Tweet posted successfully", tweet_id=tweet_id)
                return {
                    "success": True,
                    "id": tweet_id,
                    "url": f"https://twitter.com/i/web/status/{tweet_id}",
                    "platform": "twitter"
                }
            else:
                logger.error("Tweet posting failed", status=response.status_code, body=response.text)
                # If token expired, try refresh
                if response.status_code == 401 and creds.get("refresh_token"):
                    logger.info("Attempting token refresh...")
                    new_tokens = await self.refresh_access_token(creds["refresh_token"])
                    if "access_token" in new_tokens:
                        # Retry with new token (recursive, but only once)
                        return await self.tweet(content, {"access_token": new_tokens["access_token"]})
                
                return {"success": False, "error": response.text}


twitter_service = TwitterService()
