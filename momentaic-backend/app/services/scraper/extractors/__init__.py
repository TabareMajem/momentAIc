"""
Platform-specific profile extractors.
"""
from app.services.scraper.extractors.base import BaseExtractor
from app.services.scraper.extractors.instagram import InstagramExtractor
from app.services.scraper.extractors.twitter import TwitterExtractor
from app.services.scraper.extractors.tiktok import TikTokExtractor

EXTRACTORS = {
    "instagram": InstagramExtractor,
    "twitter": TwitterExtractor,
    "x": TwitterExtractor,
    "tiktok": TikTokExtractor,
}

__all__ = ["BaseExtractor", "InstagramExtractor", "TwitterExtractor", "TikTokExtractor", "EXTRACTORS"]
