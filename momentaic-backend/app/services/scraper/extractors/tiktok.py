"""
TikTok Profile Extractor
Extracts public profile data from TikTok profile pages.
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


class TikTokExtractor(BaseExtractor):
    """Extracts profile data from TikTok public profile pages."""

    platform = "tiktok"

    def get_profile_url(self, handle: str) -> str:
        handle = handle.lstrip("@").strip("/")
        return f"https://www.tiktok.com/@{handle}"

    async def extract_profile(
        self,
        handle: str,
        page_content: str,
        snapshot: Optional[Dict[str, Any]] = None,
    ) -> ProfileData:
        """Extract TikTok profile data."""
        profile = ProfileData(
            platform="tiktok",
            handle=handle.lstrip("@"),
            scraped_at=datetime.utcnow().isoformat(),
        )

        try:
            # Strategy 1: Parse __UNIVERSAL_DATA_FOR_REHYDRATION__ or SIGI_STATE
            json_data = self._extract_json_data(page_content)
            if json_data:
                profile = self._parse_json_profile(json_data, profile)

            # Strategy 2: HTML fallback
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
            logger.error("TikTok extraction failed", handle=handle, error=str(e))
            profile.error = str(e)

        return profile

    def _extract_json_data(self, html: str) -> Optional[Dict]:
        """Extract TikTok's embedded hydration data."""
        patterns = [
            r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
            r'<script id="SIGI_STATE" type="application/json">(.*?)</script>',
            r'window\[\'SIGI_STATE\'\]\s*=\s*({.*?});',
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
        """Parse from TikTok's embedded JSON data."""
        # Navigate __UNIVERSAL_DATA_FOR_REHYDRATION__ structure
        user_module = None

        # Path 1: __DEFAULT_SCOPE__ structure
        default_scope = data.get("__DEFAULT_SCOPE__", {})
        webapp_user = default_scope.get("webapp.user-detail", {})
        if webapp_user:
            user_info = webapp_user.get("userInfo", {})
            user = user_info.get("user", {})
            stats = user_info.get("stats", {})
            user_module = {"user": user, "stats": stats}

        # Path 2: SIGI_STATE structure
        if not user_module:
            user_module_data = data.get("UserModule", {})
            users = user_module_data.get("users", {})
            stats_data = user_module_data.get("stats", {})
            if users:
                username = list(users.keys())[0] if users else None
                if username:
                    user_module = {
                        "user": users[username],
                        "stats": stats_data.get(username, {}),
                    }

        if user_module:
            user = user_module.get("user", {})
            stats = user_module.get("stats", {})

            profile.display_name = user.get("nickname", "")
            profile.bio = user.get("signature", "")
            profile.is_verified = user.get("verified", False)
            profile.profile_pic_url = user.get("avatarLarger", user.get("avatarMedium", ""))

            # Stats
            profile.follower_count = stats.get("followerCount", 0)
            profile.following_count = stats.get("followingCount", 0)
            profile.likes_count = stats.get("heartCount", stats.get("heart", 0))
            profile.post_count = stats.get("videoCount", 0)

            # Bio link
            bio_link = user.get("bioLink", {})
            if isinstance(bio_link, dict) and bio_link.get("link"):
                profile.public_links.append(bio_link["link"])

        return profile

    def _parse_html_profile(self, html: str, profile: ProfileData) -> ProfileData:
        """Fallback HTML parsing for TikTok."""
        # Meta description
        meta_match = re.search(
            r'<meta\s+(?:name|property)=["\'](?:og:)?description["\']\s+content=["\'](.+?)["\']',
            html,
            re.IGNORECASE,
        )
        if meta_match:
            desc = meta_match.group(1)

            # Pattern: "@handle. 1.2M Followers. 5.6M Likes. Bio text here."
            followers_match = re.search(r'([\d,.]+[KkMm]?)\s*Follower', desc)
            likes_match = re.search(r'([\d,.]+[KkMm]?)\s*Like', desc)
            following_match = re.search(r'([\d,.]+[KkMm]?)\s*Following', desc)

            if followers_match:
                profile.follower_count = parse_count(followers_match.group(1))
            if likes_match:
                profile.likes_count = parse_count(likes_match.group(1))
            if following_match:
                profile.following_count = parse_count(following_match.group(1))

            # Bio is usually the remaining text
            parts = desc.split(".")
            bio_parts = [p.strip() for p in parts if not any(kw in p for kw in ["Follower", "Like", "Following", "video"])]
            if bio_parts:
                profile.bio = ". ".join(bio_parts).strip()

        # Title → display name
        title_match = re.search(r'<title[^>]*>(.+?)</title>', html, re.IGNORECASE)
        if title_match:
            title = title_match.group(1)
            # "Display Name (@handle) | TikTok"
            name_match = re.search(r'^(.+?)\s*\(@', title)
            if name_match:
                profile.display_name = name_match.group(1).strip()

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
        """Augment from OpenClaw AI snapshot."""
        content = snapshot.get("content", "")
        if isinstance(content, dict):
            text = json.dumps(content)
        elif isinstance(content, str):
            text = content
        else:
            return profile

        if not profile.follower_count:
            match = re.search(r'([\d,.]+[KkMm]?)\s*(?:Follower)', text)
            if match:
                profile.follower_count = parse_count(match.group(1))

        return profile
