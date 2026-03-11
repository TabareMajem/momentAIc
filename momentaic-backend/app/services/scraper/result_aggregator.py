"""
Result Aggregator
Collects results from all parallel workers, deduplicates,
validates data completeness, and exports to CSV/JSON.
"""

import csv
import io
import json
import structlog
from typing import Dict, List, Any, Optional
from collections import OrderedDict

from app.services.scraper.extractors.base import ProfileData

logger = structlog.get_logger(__name__)


class ResultAggregator:
    """
    Thread-safe result collector for distributed scraping.
    Handles deduplication, validation, and export.
    """

    def __init__(self):
        self._results: List[ProfileData] = []
        self._seen: Dict[str, int] = {}  # "platform:handle" -> index
        self._stats = {
            "total_added": 0,
            "duplicates_removed": 0,
            "valid_profiles": 0,
            "incomplete_profiles": 0,
            "error_profiles": 0,
        }

    def add_result(self, profile: ProfileData) -> None:
        """Add a scraped profile result."""
        self._results.append(profile)
        self._stats["total_added"] += 1

        if profile.error:
            self._stats["error_profiles"] += 1
        elif profile.is_valid:
            self._stats["valid_profiles"] += 1
        else:
            self._stats["incomplete_profiles"] += 1

    def deduplicate(self) -> int:
        """
        Remove duplicate entries by platform + handle.
        Keeps the entry with the most complete data.
        """
        unique: OrderedDict[str, ProfileData] = OrderedDict()

        for profile in self._results:
            key = f"{profile.platform}:{profile.handle.lower()}"

            if key in unique:
                existing = unique[key]
                # Keep the one with more data
                if self._completeness_score(profile) > self._completeness_score(existing):
                    unique[key] = profile
                self._stats["duplicates_removed"] += 1
            else:
                unique[key] = profile

        self._results = list(unique.values())
        logger.info(
            "Deduplication complete",
            unique=len(self._results),
            removed=self._stats["duplicates_removed"],
        )
        return self._stats["duplicates_removed"]

    def _completeness_score(self, profile: ProfileData) -> int:
        """Score how complete a profile's data is."""
        score = 0
        if profile.display_name:
            score += 1
        if profile.bio:
            score += 2
        if profile.follower_count > 0:
            score += 3
        if profile.following_count > 0:
            score += 1
        if profile.public_email:
            score += 3
        if profile.public_links:
            score += 1
        if profile.is_verified:
            score += 1
        if not profile.error:
            score += 2
        return score

    def export_csv(self) -> str:
        """Export all results as a CSV string."""
        output = io.StringIO()
        fieldnames = [
            "platform", "handle", "display_name", "bio", "follower_count",
            "following_count", "post_count", "likes_count", "engagement_rate",
            "is_verified", "public_email", "public_links", "profile_pic_url",
            "location", "category", "join_date", "scraped_at", "error",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for profile in self._results:
            row = profile.to_dict()
            # Convert list fields to semicolon-separated strings
            row["public_links"] = "; ".join(row.get("public_links", []))
            writer.writerow(row)

        csv_content = output.getvalue()
        logger.info("CSV export generated", rows=len(self._results), size=len(csv_content))
        return csv_content

    def export_json(self) -> str:
        """Export all results as a JSON string."""
        data = {
            "total_profiles": len(self._results),
            "stats": self._stats,
            "profiles": [p.to_dict() for p in self._results],
        }
        json_content = json.dumps(data, indent=2, ensure_ascii=False)
        logger.info("JSON export generated", profiles=len(self._results))
        return json_content

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregation statistics."""
        return {
            **self._stats,
            "current_total": len(self._results),
            "platforms": self._platform_breakdown(),
        }

    def _platform_breakdown(self) -> Dict[str, int]:
        """Count profiles per platform."""
        breakdown: Dict[str, int] = {}
        for p in self._results:
            platform = p.platform or "unknown"
            breakdown[platform] = breakdown.get(platform, 0) + 1
        return breakdown

    async def save_to_database(self, db_session, startup_id: Optional[str] = None, is_shared: bool = False, job_id: Optional[str] = None) -> int:
        """
        Persist the deduplicated results to the database as ScrapedProfile records.
        If is_shared is True, these profiles will be accessible in the Community Database.
        """
        from app.models.scraped_profile import ScrapedProfile
        
        saved_count = 0
        
        for profile in self._results:
            if not profile.is_valid:
                continue
                
            try:
                # Extract simple keywords (from bio or category)
                keywords = []
                if profile.category:
                    keywords.append(profile.category)
                    
                db_profile = ScrapedProfile(
                    startup_id=startup_id,
                    platform=profile.platform,
                    handle=profile.handle,
                    url=profile.url,
                    follower_count=profile.follower_count or 0,
                    following_count=profile.following_count or 0,
                    bio=profile.bio,
                    email=profile.public_email,
                    engagement_rate=profile.engagement_rate,
                    keywords=keywords,
                    language=None, # TBD optionally inferred later
                    extracted_data=profile.to_dict(),
                    is_shared=is_shared,
                    job_id=job_id
                )
                db_session.add(db_profile)
                saved_count += 1
            except Exception as e:
                logger.error("Failed to prepare profile for DB", handle=profile.handle, error=str(e))
                
        if saved_count > 0:
            try:
                await db_session.commit()
                logger.info("Saved profiles to database", count=saved_count, shared=is_shared)
            except Exception as e:
                await db_session.rollback()
                logger.error("Failed to commit scraped profiles to DB", error=str(e))
                return 0
                
        return saved_count
