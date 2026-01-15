"""
Twitter/X Integration - OAuth 2.0 & Social Posting
Enables agents to post tweets on behalf of users
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode
import hashlib
import base64
import secrets
import structlog

from app.integrations.base import BaseIntegration, IntegrationCredentials, SyncResult
from app.core.config import settings

logger = structlog.get_logger()


class TwitterIntegration(BaseIntegration):
    """
    Twitter/X Integration for MomentAIc
    
    Uses OAuth 2.0 PKCE flow for user authentication.
    
    Capabilities:
    - OAuth 2.0 authentication
    - Post tweets
    - Post threads
    - Get user profile
    """
    
    provider = "twitter"
    display_name = "Twitter / X"
    description = "Post tweets and engage with your audience"
    oauth_required = True
    
    # Twitter OAuth scopes for posting
    default_scopes = [
        "tweet.read",
        "tweet.write",
        "users.read",
        "offline.access",  # For refresh tokens
    ]
    
    AUTH_URL = "https://twitter.com/i/oauth2/authorize"
    TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
    API_BASE = "https://api.twitter.com/2"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # PKCE values for OAuth flow
        self._code_verifier = None
    
    def _generate_pkce(self) -> tuple:
        """Generate PKCE code verifier and challenge"""
        code_verifier = secrets.token_urlsafe(64)[:128]
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        return code_verifier, code_challenge
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate Twitter OAuth authorization URL with PKCE"""
        code_verifier, code_challenge = self._generate_pkce()
        self._code_verifier = code_verifier  # Store for token exchange
        
        # Also store in config for retrieval during callback
        self.config["code_verifier"] = code_verifier
        
        params = {
            "response_type": "code",
            "client_id": getattr(settings, "twitter_client_id", ""),
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": " ".join(self.default_scopes),
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        """Exchange authorization code for tokens"""
        code_verifier = self.config.get("code_verifier", self._code_verifier)
        
        if not code_verifier:
            raise Exception("PKCE code verifier not found")
        
        response = await self.http_client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": getattr(settings, "twitter_client_id", ""),
                "code_verifier": code_verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        
        if response.status_code != 200:
            logger.error("Twitter token exchange failed", status=response.status_code, body=response.text)
            raise Exception(f"Token exchange failed: {response.text}")
        
        data = response.json()
        
        return IntegrationCredentials(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=datetime.utcnow() + timedelta(seconds=data.get("expires_in", 7200)),
        )
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        """Refresh expired tokens"""
        if not self.credentials.refresh_token:
            raise Exception("No refresh token available")
        
        response = await self.http_client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.credentials.refresh_token,
                "client_id": getattr(settings, "twitter_client_id", ""),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        
        if response.status_code != 200:
            logger.error("Twitter token refresh failed", status=response.status_code)
            raise Exception("Token refresh failed")
        
        data = response.json()
        
        return IntegrationCredentials(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", self.credentials.refresh_token),
            expires_at=datetime.utcnow() + timedelta(seconds=data.get("expires_in", 7200)),
        )
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        """Sync user data from Twitter"""
        if not self.credentials.access_token:
            return SyncResult(success=False, errors=["Not authenticated"])
        
        try:
            # Get user profile (me endpoint)
            response = await self.http_client.get(
                f"{self.API_BASE}/users/me",
                headers={"Authorization": f"Bearer {self.credentials.access_token}"},
                params={"user.fields": "id,name,username,profile_image_url,description"},
            )
            
            if response.status_code != 200:
                return SyncResult(success=False, errors=[response.text])
            
            user = response.json().get("data", {})
            
            return SyncResult(
                success=True,
                records_synced=1,
                data={"profile": user},
            )
        except Exception as e:
            logger.error("Twitter sync failed", error=str(e))
            return SyncResult(success=False, errors=[str(e)])
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Twitter actions"""
        if action == "tweet":
            return await self._create_tweet(params)
        elif action == "thread":
            return await self._create_thread(params)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    async def _create_tweet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a tweet"""
        text = params.get("text", "")
        reply_to = params.get("reply_to")  # Optional tweet ID to reply to
        
        if not text:
            return {"success": False, "error": "Text is required"}
        
        if len(text) > 280:
            return {"success": False, "error": "Tweet exceeds 280 characters"}
        
        if not self.credentials.access_token:
            return {"success": False, "error": "Not authenticated"}
        
        tweet_data = {"text": text}
        
        if reply_to:
            tweet_data["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        response = await self.http_client.post(
            f"{self.API_BASE}/tweets",
            json=tweet_data,
            headers={
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json",
            },
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            logger.info("Tweet created successfully", tweet_id=data.get("data", {}).get("id"))
            return {"success": True, "tweet_id": data.get("data", {}).get("id")}
        else:
            logger.error("Tweet failed", status=response.status_code, body=response.text)
            return {"success": False, "error": response.text}
    
    async def _create_thread(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Twitter thread (multiple tweets)"""
        tweets = params.get("tweets", [])  # List of tweet texts
        
        if not tweets:
            return {"success": False, "error": "Tweets array is required"}
        
        tweet_ids = []
        previous_tweet_id = None
        
        for i, tweet_text in enumerate(tweets):
            result = await self._create_tweet({
                "text": tweet_text,
                "reply_to": previous_tweet_id,
            })
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed at tweet {i + 1}: {result.get('error')}",
                    "completed_tweets": tweet_ids,
                }
            
            previous_tweet_id = result.get("tweet_id")
            tweet_ids.append(previous_tweet_id)
        
        return {
            "success": True,
            "tweet_ids": tweet_ids,
            "thread_url": f"https://twitter.com/i/status/{tweet_ids[0]}",
        }
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            {
                "action": "tweet",
                "name": "Post Tweet",
                "description": "Create a single tweet",
                "params": ["text"],
            },
            {
                "action": "thread",
                "name": "Post Thread",
                "description": "Create a Twitter thread (multiple connected tweets)",
                "params": ["tweets"],  # Array of tweet texts
            },
        ]


# Singleton instance
twitter_integration = TwitterIntegration()
