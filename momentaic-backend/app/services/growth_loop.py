"""
Growth Loop Engine
Self-improving marketing machine that learns from past performance

Part of Project PHOENIX
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog

from app.core.database import AsyncSessionLocal
from app.models.social import SocialPost, PostStatus
from app.models.growth import Lead, ContentItem

logger = structlog.get_logger()


class GrowthLoopEngine:
    """
    The closed-loop growth engine that:
    1. Tracks performance of all actions
    2. Learns patterns (best posting times, content types, etc.)
    3. Auto-adjusts strategies based on data
    """
    
    async def analyze_past_performance(self, startup_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Analyze the past N days of performance data.
        Returns insights about what's working and what's not.
        """
        async with AsyncSessionLocal() as db:
            # Get published posts and their performance
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            result = await db.execute(
                select(SocialPost).where(
                    SocialPost.startup_id == startup_id,
                    SocialPost.status == PostStatus.PUBLISHED,
                    SocialPost.published_at >= cutoff
                )
            )
            posts = result.scalars().all()
            
            if not posts:
                return {
                    "posts_analyzed": 0,
                    "insights": ["No published posts in the last 30 days. Start posting!"],
                    "recommendations": []
                }
            
            # Analyze by day of week
            day_performance: Dict[int, List[int]] = {i: [] for i in range(7)}
            hour_performance: Dict[int, List[int]] = {i: [] for i in range(24)}
            platform_performance: Dict[str, int] = {}
            
            for post in posts:
                if post.published_at:
                    day_of_week = post.published_at.weekday()
                    hour = post.published_at.hour
                    
                    # Use engagement from platform_ids if available
                    engagement = 1  # Default minimal engagement
                    if post.platform_ids:
                        for platform, data in post.platform_ids.items():
                            if isinstance(data, dict):
                                engagement = data.get("likes", 0) + data.get("retweets", 0) + data.get("comments", 0)
                    
                    day_performance[day_of_week].append(engagement)
                    hour_performance[hour].append(engagement)
                    
                    for platform in post.platforms:
                        platform_performance[platform] = platform_performance.get(platform, 0) + engagement
            
            # Find best performing day
            avg_by_day = {day: sum(engagements)/len(engagements) if engagements else 0 
                          for day, engagements in day_performance.items()}
            best_day = max(avg_by_day, key=avg_by_day.get)
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            # Find best hour
            avg_by_hour = {hour: sum(engagements)/len(engagements) if engagements else 0 
                          for hour, engagements in hour_performance.items()}
            best_hour = max(avg_by_hour, key=avg_by_hour.get)
            
            # Find best platform
            best_platform = max(platform_performance, key=platform_performance.get) if platform_performance else "twitter"
            
            insights = [
                f"Your best posting day is {day_names[best_day]}",
                f"Your best posting hour is {best_hour}:00 UTC",
                f"Your best performing platform is {best_platform}",
                f"Analyzed {len(posts)} posts over the last {days} days"
            ]
            
            recommendations = [
                f"Schedule more posts for {day_names[best_day]}s around {best_hour}:00 UTC",
                f"Focus more effort on {best_platform}" if platform_performance else "Connect social accounts to track performance",
                "Experiment with different content types to find what resonates"
            ]
            
            return {
                "posts_analyzed": len(posts),
                "best_day": day_names[best_day],
                "best_hour": best_hour,
                "best_platform": best_platform,
                "performance_by_day": {day_names[d]: round(v, 2) for d, v in avg_by_day.items()},
                "insights": insights,
                "recommendations": recommendations
            }
    
    async def optimize_schedule(self, startup_id: str) -> Dict[str, Any]:
        """
        Based on past performance, suggest optimal posting schedule.
        """
        performance = await self.analyze_past_performance(startup_id)
        
        if performance["posts_analyzed"] < 5:
            return {
                "schedule": {
                    "monday": "09:00",
                    "wednesday": "14:00",
                    "friday": "11:00"
                },
                "note": "Default schedule. Post more to unlock personalized optimization."
            }
        
        best_day = performance.get("best_day", "Tuesday")
        best_hour = performance.get("best_hour", 9)
        
        # Generate optimized schedule based on data
        schedule = {
            best_day.lower(): f"{best_hour:02d}:00",
        }
        
        # Add secondary posting days
        day_perf = performance.get("performance_by_day", {})
        sorted_days = sorted(day_perf.items(), key=lambda x: x[1], reverse=True)
        
        for day, _ in sorted_days[1:3]:  # Add 2 more top days
            schedule[day.lower()] = f"{best_hour:02d}:00"
        
        return {
            "schedule": schedule,
            "rationale": f"Optimized based on {performance['posts_analyzed']} posts. Best day: {best_day}, Best hour: {best_hour}:00"
        }
    
    async def track_conversion(
        self, 
        startup_id: str, 
        source_type: str,  # "post", "email", "experiment"
        source_id: str,
        conversion_type: str,  # "signup", "lead", "sale"
        value: float = 0
    ) -> bool:
        """
        Track a conversion back to its source for attribution.
        This closes the loop and allows learning.
        """
        # TODO: Implement proper attribution tracking
        logger.info(
            "Conversion tracked",
            startup_id=startup_id,
            source_type=source_type,
            source_id=source_id,
            conversion_type=conversion_type,
            value=value
        )
        return True


# Singleton
growth_loop = GrowthLoopEngine()
