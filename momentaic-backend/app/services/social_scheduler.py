
from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

from app.core.database import AsyncSessionLocal
from app.models.social import SocialPost, PostStatus, SocialPlatform
from app.models.integration import Integration, IntegrationProvider, IntegrationStatus

# Placeholder for real API Clients (we will implement these next)
# from app.services.social.twitter import twitter_service
# from app.services.social.linkedin import linkedin_service

logger = structlog.get_logger()

class SocialScheduler:
    """
    The Engine of the Buffer Killer.
    Manages scheduling and dispatching of social posts.
    """
    
    async def schedule_post(self, startup_id: str, content: str, platforms: List[str], scheduled_at: datetime) -> SocialPost:
        """Schedule a new post"""
        async with AsyncSessionLocal() as db:
            post = SocialPost(
                startup_id=startup_id,
                content=content,
                platforms=[p.lower() for p in platforms],
                scheduled_at=scheduled_at,
                status=PostStatus.SCHEDULED
            )
            db.add(post)
            await db.commit()
            await db.refresh(post)
            logger.info("SocialScheduler: Post scheduled", post_id=str(post.id), time=scheduled_at)
            return post

    async def publish_due_posts(self):
        """
        CRON TASK: Finds posts that are due and publishes them.
        """
        logger.info("SocialScheduler: Checking for due posts...")
        async with AsyncSessionLocal() as db:
            # Find posts that are SCHEDULED and time <= NOW
            result = await db.execute(
                select(SocialPost).where(
                    SocialPost.status == PostStatus.SCHEDULED,
                    SocialPost.scheduled_at <= datetime.utcnow()
                )
            )
            due_posts = result.scalars().all()
            
            logger.info(f"SocialScheduler: Found {len(due_posts)} posts to publish")
            
            for post in due_posts:
                await self._process_post(db, post)

    async def _process_post(self, db: AsyncSession, post: SocialPost):
        """Attempt to publish a single post to all requested platforms"""
        try:
            results = {}
            all_success = True
            
            for platform in post.platforms:
                # 1. Get Integration Credentials for this Startup + Platform
                creds = await self._get_credentials(db, post.startup_id, platform)
                
                if not creds:
                    results[platform] = {"success": False, "error": "No Integration Connected"}
                    all_success = False
                    continue
                
                # 2. Publish (MVP: Mocked for now, will call real service)
                try:
                    publish_result = await self._publish_to_platform(platform, post.content, creds)
                    results[platform] = publish_result
                    if not publish_result.get("success"):
                        all_success = False
                except Exception as e:
                    results[platform] = {"success": False, "error": str(e)}
                    all_success = False
            
            # 3. Update Status
            post.platform_ids = results
            if all_success:
                post.status = PostStatus.PUBLISHED
                post.published_at = datetime.utcnow()
            else:
                post.status = PostStatus.FAILED
                post.error_message = f"Partial/Full Failure: {results}"
            
            await db.flush()
            await db.commit()
            
        except Exception as e:
            logger.error("SocialScheduler: Post execution failed", post_id=str(post.id), error=str(e))
            post.status = PostStatus.FAILED
            post.error_message = str(e)
            await db.commit()

    async def _get_credentials(self, db: AsyncSession, startup_id: str, platform: str) -> Optional[Dict]:
        """Fetch integration API keys from DB"""
        # Map generic platform name to IntegrationProvider enum
        provider_map = {
            "twitter": IntegrationProvider.TWITTER,
            "linkedin": IntegrationProvider.LINKEDIN
        }
        
        provider = provider_map.get(platform)
        if not provider:
            return None
            
        result = await db.execute(
            select(Integration).where(
                Integration.startup_id == startup_id,
                Integration.provider == provider,
                Integration.status == IntegrationStatus.ACTIVE
            )
        )
        integration = result.scalar_one_or_none()
        
        if not integration:
            return None
            
        return {
            "api_key": integration.api_key,
            "api_secret": integration.api_secret,
            "access_token": integration.access_token,
            "access_token_secret": integration.config.get("access_token_secret"), # Twitter needs this
            "refresh_token": integration.refresh_token
        }

    async def _publish_to_platform(self, platform: str, content: str, creds: Dict) -> Dict:
        """
        Dispatch to specific connector.
        This is the REAL implementation.
        """
        if platform == "twitter":
            from app.services.social.twitter import twitter_service
            return await twitter_service.tweet(content, creds)
            
        elif platform == "linkedin":
            from app.services.social.linkedin import linkedin_service
            return await linkedin_service.share_post(content, creds)
            
        elif platform == "instagram":
            # Instagram requires image upload - placeholder for Phase 7b
            return {"success": False, "error": "Instagram not yet implemented. Requires image."}
            
        return {"success": False, "error": "Platform not supported"}

social_scheduler = SocialScheduler()
