"""
Base Extractor Interface
Abstract interface for platform-specific profile data extractors.
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class ProfileData:
    """Standardized profile data extracted from any platform."""
    platform: str = ""
    handle: str = ""
    display_name: str = ""
    bio: str = ""
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    likes_count: int = 0          # TikTok specific
    engagement_rate: float = 0.0
    is_verified: bool = False
    profile_pic_url: str = ""
    public_email: str = ""
    public_links: List[str] = field(default_factory=list)
    join_date: str = ""
    location: str = ""
    category: str = ""            # Instagram business category
    scraped_at: str = ""
    raw_html_snippet: str = ""    # First 500 chars for debugging
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def is_valid(self) -> bool:
        """A profile is valid if we got at least the handle and follower count."""
        return bool(self.handle) and self.follower_count > 0


# Common regex for extracting emails from bio text
EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)

# Common regex for extracting URLs from bio text
URL_REGEX = re.compile(
    r"https?://[^\s<>\"']+|(?:www\.)[^\s<>\"']+",
    re.IGNORECASE,
)


def extract_emails(text: str) -> List[str]:
    """Extract all email addresses from text."""
    return list(set(EMAIL_REGEX.findall(text)))


def extract_urls(text: str) -> List[str]:
    """Extract all URLs from text."""
    return list(set(URL_REGEX.findall(text)))


def parse_count(text: str) -> int:
    """
    Parse follower/following count strings like '1.2M', '45.3K', '1,234'.
    Returns integer count.
    """
    if not text:
        return 0

    text = text.strip().replace(",", "").replace(" ", "")

    multipliers = {
        "K": 1_000,
        "k": 1_000,
        "M": 1_000_000,
        "m": 1_000_000,
        "B": 1_000_000_000,
        "b": 1_000_000_000,
    }

    for suffix, mult in multipliers.items():
        if text.endswith(suffix):
            try:
                return int(float(text[:-1]) * mult)
            except ValueError:
                return 0

    try:
        return int(float(text))
    except ValueError:
        return 0


class BaseExtractor(ABC):
    """Abstract base class for platform-specific profile extractors."""

    platform: str = "unknown"

    @abstractmethod
    async def extract_profile(
        self,
        handle: str,
        page_content: str,
        snapshot: Optional[Dict[str, Any]] = None,
    ) -> ProfileData:
        """
        Extract profile data from page content or OpenClaw snapshot.

        Args:
            handle: The username/handle of the profile.
            page_content: Raw HTML or text content of the profile page.
            snapshot: Optional OpenClaw AI-formatted snapshot dict.

        Returns:
            ProfileData with extracted fields.
        """
        pass

    @abstractmethod
    def get_profile_url(self, handle: str) -> str:
        """Get the full URL for a given handle on this platform."""
        pass

    def _extract_common(self, bio: str) -> tuple:
        """Extract emails and URLs from bio text."""
        emails = extract_emails(bio)
        urls = extract_urls(bio)
        primary_email = emails[0] if emails else ""
        return primary_email, urls
