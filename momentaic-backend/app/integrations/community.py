"""
Slack & Twitter Community Integration
Lightweight community management for #MomentAIcRoast campaign
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import structlog
import httpx

from app.core.config import settings

logger = structlog.get_logger()


class SlackMessage(BaseModel):
    """A Slack message to post."""
    channel: str
    text: str
    blocks: Optional[List[Dict]] = None
    thread_ts: Optional[str] = None


class TwitterPost(BaseModel):
    """A Twitter/X post."""
    text: str
    media_ids: Optional[List[str]] = None
    reply_to_id: Optional[str] = None


class CommunityIntegration:
    """
    Slack + Twitter community integration.
    
    Features:
    - Post updates to Slack channels
    - Track #MomentAIcRoast hashtag on Twitter
    - Verify tweet unlocks for roast feature
    - Post viral content summaries
    """
    
    def __init__(self):
        self.slack_webhook = getattr(settings, 'slack_webhook_url', '')
        self.slack_bot_token = getattr(settings, 'slack_bot_token', '')
        self.twitter_bearer = getattr(settings, 'twitter_bearer_token', '')
    
    # ============ SLACK ============
    
    async def post_to_slack(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None
    ) -> bool:
        """
        Post a message to Slack.
        
        Args:
            channel: Channel name or ID
            text: Message text
            blocks: Optional rich blocks
        
        Returns:
            Success status
        """
        # Use webhook if configured (simpler)
        if self.slack_webhook:
            return await self._post_via_webhook(text, blocks)
        
        # Use Bot API if configured
        if self.slack_bot_token:
            return await self._post_via_api(channel, text, blocks)
        
        logger.warning("Slack not configured")
        return False
    
    async def _post_via_webhook(self, text: str, blocks: Optional[List[Dict]] = None) -> bool:
        """Post via incoming webhook."""
        try:
            async with httpx.AsyncClient() as client:
                payload = {"text": text}
                if blocks:
                    payload["blocks"] = blocks
                
                response = await client.post(self.slack_webhook, json=payload)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Slack webhook error: {e}")
            return False
    
    async def _post_via_api(self, channel: str, text: str, blocks: Optional[List[Dict]] = None) -> bool:
        """Post via Slack API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://slack.com/api/chat.postMessage",
                    headers={"Authorization": f"Bearer {self.slack_bot_token}"},
                    json={
                        "channel": channel,
                        "text": text,
                        "blocks": blocks
                    }
                )
                return response.json().get("ok", False)
        except Exception as e:
            logger.error(f"Slack API error: {e}")
            return False
    
    async def notify_new_roast(self, startup_name: str, score: int, region: str):
        """Notify Slack of a new viral roast."""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🔥 *New Roast Alert!*\n\n*Startup:* {startup_name}\n*Score:* {score}/100\n*Region:* {region}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"_via #MomentAIcRoast campaign_"}
                ]
            }
        ]
        
        await self.post_to_slack(
            channel="#roast-alerts",
            text=f"🔥 New roast: {startup_name} scored {score}/100",
            blocks=blocks
        )
    
    async def notify_new_ambassador(self, name: str, platform: str, followers: int):
        """Notify Slack of new ambassador signup."""
        await self.post_to_slack(
            channel="#ambassadors",
            text=f"🎉 New ambassador: {name} from {platform} ({followers:,} followers)"
        )
    
    # ============ TWITTER ============
    
    async def search_hashtag(
        self,
        hashtag: str = "MomentAIcRoast",
        max_results: int = 100
    ) -> List[Dict]:
        """
        Search for tweets with our hashtag.
        
        Args:
            hashtag: Hashtag to search (without #)
            max_results: Maximum tweets to return
        
        Returns:
            List of tweet data
        """
        if not self.twitter_bearer:
            logger.warning("Twitter API not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.twitter.com/2/tweets/search/recent",
                    headers={"Authorization": f"Bearer {self.twitter_bearer}"},
                    params={
                        "query": f"#{hashtag} -is:retweet",
                        "max_results": min(max_results, 100),
                        "tweet.fields": "author_id,created_at,public_metrics",
                        "expansions": "author_id",
                        "user.fields": "username,name,public_metrics"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Twitter API error: {response.text}")
                    return []
                
                data = response.json()
                return data.get("data", [])
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
            return []
    
    async def verify_tweet(
        self,
        tweet_url: str,
        required_hashtag: str = "MomentAIcRoast"
    ) -> Dict[str, Any]:
        """
        Verify a tweet contains our hashtag for unlock.
        
        Args:
            tweet_url: URL of the tweet
            required_hashtag: Hashtag that must be present
        
        Returns:
            Verification result with user info
        """
        # Extract tweet ID from URL
        tweet_id = tweet_url.split("/")[-1].split("?")[0]
        
        if not self.twitter_bearer:
            # Fallback: assume valid if URL looks right
            return {
                "valid": True,
                "tweet_id": tweet_id,
                "verified_via": "url_pattern",
                "message": "Tweet URL accepted (Twitter API not configured)"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.twitter.com/2/tweets/{tweet_id}",
                    headers={"Authorization": f"Bearer {self.twitter_bearer}"},
                    params={
                        "tweet.fields": "text,author_id,created_at",
                        "expansions": "author_id",
                        "user.fields": "username,name"
                    }
                )
                
                if response.status_code != 200:
                    return {"valid": False, "error": "Tweet not found"}
                
                data = response.json()
                tweet_text = data.get("data", {}).get("text", "")
                
                # Check for hashtag
                if f"#{required_hashtag}" not in tweet_text.replace(" ", ""):
                    return {
                        "valid": False,
                        "error": f"Tweet must contain #{required_hashtag}"
                    }
                
                # Get user info
                users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
                author_id = data.get("data", {}).get("author_id")
                author = users.get(author_id, {})
                
                return {
                    "valid": True,
                    "tweet_id": tweet_id,
                    "author_username": author.get("username"),
                    "author_name": author.get("name"),
                    "verified_via": "twitter_api"
                }
        except Exception as e:
            logger.error(f"Tweet verification error: {e}")
            return {"valid": False, "error": str(e)}
    
    async def get_campaign_metrics(
        self,
        hashtag: str = "MomentAIcRoast"
    ) -> Dict[str, Any]:
        """
        Get viral campaign metrics from Twitter.
        
        Args:
            hashtag: Campaign hashtag
        
        Returns:
            Campaign metrics (tweet count, impressions estimate, etc.)
        """
        tweets = await self.search_hashtag(hashtag, max_results=100)
        
        if not tweets:
            return {
                "hashtag": hashtag,
                "tweet_count": 0,
                "total_likes": 0,
                "total_retweets": 0,
                "unique_authors": 0,
                "estimated_reach": 0
            }
        
        total_likes = sum(t.get("public_metrics", {}).get("like_count", 0) for t in tweets)
        total_retweets = sum(t.get("public_metrics", {}).get("retweet_count", 0) for t in tweets)
        unique_authors = len(set(t.get("author_id") for t in tweets))
        
        # Rough reach estimate: tweets * avg follower estimate
        estimated_reach = len(tweets) * 500 + total_retweets * 1000
        
        return {
            "hashtag": hashtag,
            "tweet_count": len(tweets),
            "total_likes": total_likes,
            "total_retweets": total_retweets,
            "unique_authors": unique_authors,
            "estimated_reach": estimated_reach
        }


# Singleton
community = CommunityIntegration()
