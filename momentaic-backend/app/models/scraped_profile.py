from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class ScrapedProfile(Base):
    """
    Stores influencer profile data gathered by the Scraper module.
    If is_shared=True, this profile is accessible in the Community Database.
    """
    __tablename__ = "scraped_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    startup_id = Column(UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=True)
    
    # Core identifiers
    platform = Column(String(50), nullable=False, index=True) # instagram, twitter, tiktok
    handle = Column(String(255), nullable=False, index=True)
    url = Column(String(1024), nullable=False)
    
    # Extracted data
    follower_count = Column(Integer, default=0, index=True)
    following_count = Column(Integer, default=0)
    bio = Column(Text, nullable=True)
    email = Column(String(255), nullable=True, index=True)
    
    # Analytics
    engagement_rate = Column(String(50), nullable=True)
    keywords = Column(JSONB, default=list, server_default='[]')
    language = Column(String(10), nullable=True, index=True)
    
    # Full raw payload dump
    extracted_data = Column(JSONB, default=dict)
    
    # Sharing configuration
    is_shared = Column(Boolean, default=False, index=True)
    
    # Metadata
    job_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
