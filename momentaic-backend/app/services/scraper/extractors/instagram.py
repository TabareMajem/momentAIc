"""
Instagram Profile Extractor
Extracts public profile data from Instagram profile pages.
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


class InstagramExtractor(BaseExtractor):
    """Extracts profile data from Instagram public profile pages."""

    platform = "instagram"

    def get_profile_url(self, handle: str) -> str:
        handle = handle.lstrip("@").strip("/")
        return f"https://www.instagram.com/{handle}/"

    async def extract_profile(
        self,
        handle: str,
        page_content: str,
        snapshot: Optional[Dict[str, Any]] = None,
    ) -> ProfileData:
        """Extract Instagram profile data from page HTML or snapshot."""
        profile = ProfileData(
            platform="instagram",
            handle=handle.lstrip("@"),
            scraped_at=datetime.utcnow().isoformat(),
        )

        try:
            # Strategy 1: Try to extract from embedded JSON (shared_data or meta tags)
            json_data = self._extract_json_data(page_content)
            if json_data:
                profile = self._parse_json_profile(json_data, profile)
            else:
                # Strategy 2: Parse from HTML meta tags and visible text
                profile = self._parse_html_profile(page_content, profile)

            # Strategy 3: Augment with OpenClaw snapshot if available
            if snapshot:
                profile = self._augment_from_snapshot(snapshot, profile)

            # Extract email from bio
            if profile.bio:
                email, urls = self._extract_common(profile.bio)
                if email:
                    profile.public_email = email
                profile.public_links = urls

            profile.raw_html_snippet = page_content[:500]

        except Exception as e:
            logger.error("Instagram extraction failed", handle=handle, error=str(e))
            profile.error = str(e)

        return profile

    def _extract_json_data(self, html: str) -> Optional[Dict]:
        """Try to find Instagram's embedded JSON data."""
        # Look for window._sharedData or similar embedded JSON
        patterns = [
            r'window\._sharedData\s*=\s*({.*?})\s*;',
            r'"ProfilePage"\s*:\s*\[({.*?})\]',
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
        """Parse profile from Instagram's embedded JSON."""
        # Navigate the nested structure
        user = None
        try:
            # Try _sharedData path
            user = data.get("entry_data", {}).get("ProfilePage", [{}])[0].get("graphql", {}).get("user", {})
        except (IndexError, AttributeError):
            pass

        if not user:
            # Try direct user object
            user = data.get("user", data)

        if user:
            profile.display_name = user.get("full_name", "")
            profile.bio = user.get("biography", "")
            profile.follower_count = user.get("edge_followed_by", {}).get("count", 0)
            profile.following_count = user.get("edge_follow", {}).get("count", 0)
            profile.post_count = user.get("edge_owner_to_timeline_media", {}).get("count", 0)
            profile.is_verified = user.get("is_verified", False)
            profile.profile_pic_url = user.get("profile_pic_url_hd", user.get("profile_pic_url", ""))
            profile.category = user.get("category_name", "")

            # External URL
            external = user.get("external_url", "")
            if external:
                profile.public_links.append(external)

            # Business email
            business_email = user.get("business_email", "")
            if business_email:
                profile.public_email = business_email

        return profile

    def _parse_html_profile(self, html: str, profile: ProfileData) -> ProfileData:
        """Fallback: parse from HTML meta tags and visible text."""
        # Meta description (usually contains follower count)
        meta_match = re.search(
            r'<meta\s+(?:name|property)=["\'](?:og:)?description["\']\s+content=["\'](.+?)["\']',
            html,
            re.IGNORECASE,
        )
        if meta_match:
            desc = meta_match.group(1)
            # Pattern: "1,234 Followers, 56 Following, 78 Posts"
            followers = re.search(r'([\d,.]+[KkMm]?)\s*Followers', desc)
            following = re.search(r'([\d,.]+[KkMm]?)\s*Following', desc)
            posts = re.search(r'([\d,.]+[KkMm]?)\s*Posts', desc)

            if followers:
                profile.follower_count = parse_count(followers.group(1))
            if following:
                profile.following_count = parse_count(following.group(1))
            if posts:
                profile.post_count = parse_count(posts.group(1))

            # Bio often follows the counts in the description
            bio_match = re.search(r'Posts\s*[-–—]\s*(.+)', desc)
            if bio_match:
                profile.bio = bio_match.group(1).strip()

        # Title tag often has display name
        title_match = re.search(r'<title[^>]*>(.+?)</title>', html, re.IGNORECASE)
        if title_match:
            title = title_match.group(1)
            # Pattern: "Display Name (@handle) • Instagram photos and videos"
            name_match = re.search(r'^(.+?)\s*\(@', title)
            if name_match:
                profile.display_name = name_match.group(1).strip()

        # Verified badge
        if 'is_verified":true' in html or "Verified" in html:
            profile.is_verified = True

        # Profile picture
        pic_match = re.search(
            r'<meta\s+property=["\']og:image["\']\s+content=["\'](.+?)["\']',
            html,
            re.IGNORECASE,
        )
        if pic_match:
            profile.profile_pic_url = pic_match.group(1)

        return profile

    def _augment_from_snapshot(self, snapshot: Dict, profile: ProfileData) -> ProfileData:
        """Augment data from OpenClaw AI snapshot."""
        content = snapshot.get("content", "")
        if isinstance(content, dict):
            text = json.dumps(content)
        elif isinstance(content, str):
            text = content
        else:
            return profile

        # If we still don't have followers, try from snapshot text
        if not profile.follower_count:
            match = re.search(r'([\d,.]+[KkMm]?)\s*(?:followers|Followers)', text)
            if match:
                profile.follower_count = parse_count(match.group(1))

        return profile
