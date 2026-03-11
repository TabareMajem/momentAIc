"""
Twitter/X Profile Extractor
Extracts public profile data from X.com profile pages.
"""

import re
import json
import structlog
from typing import Dict, Any, Optional
from datetime import datetime

from app.services.scraper.extractors.base import (
    BaseExtractor, ProfileData, extract_emails, extract_urls, parse_count,
)

logger = structlog.get_logger(__name__)


class TwitterExtractor(BaseExtractor):
    """Extracts profile data from X/Twitter public profile pages."""

    platform = "twitter"

    def get_profile_url(self, handle: str) -> str:
        handle = handle.lstrip("@").strip("/")
        return f"https://x.com/{handle}"

    async def extract_profile(
        self,
        handle: str,
        page_content: str,
        snapshot: Optional[Dict[str, Any]] = None,
    ) -> ProfileData:
        """Extract X/Twitter profile data."""
        profile = ProfileData(
            platform="twitter",
            handle=handle.lstrip("@"),
            scraped_at=datetime.utcnow().isoformat(),
        )

        try:
            # Strategy 1: Parse embedded JSON-LD or __NEXT_DATA__
            json_data = self._extract_json_data(page_content)
            if json_data:
                profile = self._parse_json_profile(json_data, profile)

            # Strategy 2: Fallback to HTML parsing
            if not profile.follower_count:
                profile = self._parse_html_profile(page_content, profile)

            # Strategy 3: OpenClaw snapshot
            if snapshot:
                profile = self._augment_from_snapshot(snapshot, profile)

            # Email/URL from bio
            if profile.bio:
                email, urls = self._extract_common(profile.bio)
                if email:
                    profile.public_email = email
                profile.public_links.extend(urls)

            profile.raw_html_snippet = page_content[:500]

        except Exception as e:
            logger.error("Twitter extraction failed", handle=handle, error=str(e))
            profile.error = str(e)

        return profile

    def _extract_json_data(self, html: str) -> Optional[Dict]:
        """Try to find Twitter's embedded data."""
        patterns = [
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            r'<script type="application/ld\+json">(.*?)</script>',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
        return None

    def _parse_json_profile(self, data: Dict, profile: ProfileData) -> ProfileData:
        """Parse from embedded JSON data."""
        # Navigate potential structures
        user = data.get("props", {}).get("pageProps", {}).get("user", {})
        if not user:
            user = data

        if user:
            profile.display_name = user.get("name", "")
            profile.bio = user.get("description", "")
            profile.follower_count = user.get("followers_count", 0)
            profile.following_count = user.get("friends_count", user.get("following_count", 0))
            profile.post_count = user.get("statuses_count", 0)
            profile.is_verified = user.get("verified", False) or user.get("is_blue_verified", False)
            profile.profile_pic_url = user.get("profile_image_url_https", "")
            profile.location = user.get("location", "")
            profile.join_date = user.get("created_at", "")

            # URL entity
            url_entity = user.get("url", "")
            if url_entity:
                profile.public_links.append(url_entity)

        return profile

    def _parse_html_profile(self, html: str, profile: ProfileData) -> ProfileData:
        """Fallback HTML parsing for Twitter profiles."""
        # Meta description
        meta_match = re.search(
            r'<meta\s+(?:name|property)=["\'](?:og:)?description["\']\s+content=["\'](.+?)["\']',
            html,
            re.IGNORECASE,
        )
        if meta_match:
            desc = meta_match.group(1)
            profile.bio = desc

        # Title → display name
        title_match = re.search(r'<title[^>]*>(.+?)</title>', html, re.IGNORECASE)
        if title_match:
            title = title_match.group(1)
            # Pattern: "Display Name (@handle) / X"
            name_match = re.search(r'^(.+?)\s*\(@', title)
            if name_match:
                profile.display_name = name_match.group(1).strip()

        # data-testid based extraction for follower/following counts
        follower_patterns = [
            r'([\d,.]+[KkMm]?)\s*Followers',
            r'followers_count["\s:]+(\d+)',
            r'aria-label=["\'][^"\']*?([\d,.]+[KkMm]?)\s*Followers',
        ]
        for pattern in follower_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                profile.follower_count = parse_count(match.group(1))
                break

        following_patterns = [
            r'([\d,.]+[KkMm]?)\s*Following',
            r'friends_count["\s:]+(\d+)',
        ]
        for pattern in following_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                profile.following_count = parse_count(match.group(1))
                break

        # Verified
        if "is_blue_verified" in html or 'verified":true' in html:
            profile.is_verified = True

        # Profile pic from og:image
        pic_match = re.search(
            r'<meta\s+property=["\']og:image["\']\s+content=["\'](.+?)["\']',
            html,
            re.IGNORECASE,
        )
        if pic_match:
            profile.profile_pic_url = pic_match.group(1)

        return profile

    def _augment_from_snapshot(self, snapshot: Dict, profile: ProfileData) -> ProfileData:
        """Augment from OpenClaw AI snapshot."""
        content = snapshot.get("content", "")
        if isinstance(content, dict):
            text = json.dumps(content)
        elif isinstance(content, str):
            text = content
        else:
            return profile

        if not profile.follower_count:
            match = re.search(r'([\d,.]+[KkMm]?)\s*(?:Followers|followers)', text)
            if match:
                profile.follower_count = parse_count(match.group(1))

        if not profile.bio:
            # Try to find bio-like text
            bio_match = re.search(r'bio["\s:]+["\'](.+?)["\']', text, re.IGNORECASE)
            if bio_match:
                profile.bio = bio_match.group(1)

        return profile
